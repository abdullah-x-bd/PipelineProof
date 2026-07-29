from __future__ import annotations

import hashlib
import json
import statistics
import tempfile
from pathlib import Path
from typing import Any

from pipelineproof.catalog import get_task, task_catalog
from pipelineproof.failures import classify
from pipelineproof.quality import quality_score
from pipelineproof.sandbox import DockerSandbox, LocalSandbox
from pipelineproof.stats import wilson_interval
from pipelineproof.templates import write_task
from pipelineproof.verifier import verify_spec

ATTACKS = (
    "constant",
    "hardcoded",
    "shape_forgery",
    "fake_success",
    "public_conditional",
    "oracle_import",
    "metric_monkeypatch",
    "protected_edit",
)
VALID_CONTROLS = ("canonical", "alternative", "refactor")


def _trial(
    spec, style: str, seed: int, mode: str = "local", measure_quality: bool = True
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="pipelineproof-trial-") as directory:
        candidate = Path(directory) / style
        write_task(spec, candidate, style)
        result = verify_spec(spec, candidate, seed, mode)
        quality = (
            quality_score(spec, candidate, seed + 100_000, mode)
            if measure_quality
            else {"task_id": spec.task_id, "score": None, "checks": {}}
        )
    data = result.to_dict()
    data["style"] = style
    data["candidate"] = style
    data["quality"] = quality
    data["failure_class"] = classify(result.checks)
    return data


def soundness_receipt(
    seed_count: int = 4, mode: str = "local", seed_offset: int = 0
) -> dict[str, Any]:
    spec = get_task("feature-schema-a")
    invalid = []
    valid = []
    for seed_index in range(seed_offset, seed_offset + seed_count):
        base = spec.seed + 20_000 + seed_index * 101
        invalid.extend(_trial(spec, style, base + index, mode, False) for index, style in enumerate(ATTACKS))
        valid.extend(
            _trial(spec, style, base + 500 + index, mode, False)
            for index, style in enumerate(VALID_CONTROLS)
        )
    false_accepts = sum(item["passed"] for item in invalid)
    false_rejects = sum(not item["passed"] for item in valid)
    return {
        "verifier_version": "0.3.0",
        "attack_battery_version": "1.0.0",
        "verifier_mode": mode,
        "scope": [spec.task_id],
        "repeated_seed_trials_share_one_structural_task": True,
        "false_accept": {
            "count": false_accepts,
            "trials": len(invalid),
            "rate": false_accepts / len(invalid),
            "wilson_95": list(wilson_interval(false_accepts, len(invalid))),
        },
        "false_reject": {
            "count": false_rejects,
            "trials": len(valid),
            "rate": false_rejects / len(valid),
            "wilson_95": list(wilson_interval(false_rejects, len(valid))),
        },
        "surviving_attacks": sorted({item["style"] for item in invalid if item["passed"]}),
        "invalid_trials": invalid,
        "valid_trials": valid,
    }


def reward_ladder(mode: str = "local") -> dict[str, Any]:
    spec = get_task("feature-schema-a")
    levels = (
        ("invalid interface", "syntax_error"),
        ("format-only success", "fake_success"),
        ("unrepaired repository", "broken"),
        ("correct repair with protected edit", "correct_protected_edit"),
        ("complete repair", "canonical"),
    )
    rows = []
    for index, (label, style) in enumerate(levels):
        result = _trial(spec, style, spec.seed + 40_000 + index, mode)
        rows.append(
            {
                "label": label,
                "style": style,
                "reward": result["reward"],
                "quality": result["quality"],
                "passed": result["passed"],
            }
        )
    totals = [row["reward"]["total"] for row in rows]
    return {
        "task_id": spec.task_id,
        "strictly_monotonic": all(totals[index] < totals[index + 1] for index in range(len(totals) - 1)),
        "levels": rows,
    }


def family_controls(mode: str = "local") -> dict[str, Any]:
    rows = []
    for spec in task_catalog():
        for style in ("broken", *VALID_CONTROLS):
            result = _trial(spec, style, spec.seed + 50_000, mode)
            rows.append(
                {
                    "task_id": spec.task_id,
                    "family": spec.family,
                    "style": style,
                    "passed": result["passed"],
                    "reward": result["reward"]["total"],
                    "quality": result["quality"]["score"],
                    "failure_class": result["failure_class"],
                }
            )
    valid = [row for row in rows if row["style"] in VALID_CONTROLS]
    broken = [row for row in rows if row["style"] == "broken"]
    return {
        "controls": rows,
        "accepted_valid": sum(row["passed"] for row in valid),
        "valid_total": len(valid),
        "rejected_broken": sum(not row["passed"] for row in broken),
        "broken_total": len(broken),
    }


def stability_report(seed_count: int = 4, mode: str = "local") -> dict[str, Any]:
    rows = []
    for spec in task_catalog():
        for style in ("broken", "canonical"):
            rewards = []
            qualities = []
            for index in range(seed_count):
                result = _trial(spec, style, spec.seed + 60_000 + index * 137, mode)
                rewards.append(result["reward"]["total"])
                qualities.append(result["quality"]["score"])
            rows.append(
                {
                    "task_id": spec.task_id,
                    "style": style,
                    "rollouts": seed_count,
                    "mean_reward": statistics.fmean(rewards),
                    "reward_std": statistics.pstdev(rewards),
                    "mean_quality": statistics.fmean(qualities),
                    "quality_std": statistics.pstdev(qualities),
                    "stable": len(set(rewards)) == 1 and len(set(qualities)) == 1,
                }
            )
    return {"rows": rows, "high_variance": [row for row in rows if not row["stable"]]}


def candidate_search(mode: str = "local") -> dict[str, Any]:
    spec = get_task("feature-schema-a")
    styles = [
        "syntax_error",
        "fake_success",
        "constant",
        "broken",
        "correct_protected_edit",
        "canonical",
        "alternative",
        "refactor",
    ]
    candidates = [
        _trial(spec, style, spec.seed + 70_000 + index, mode)
        for index, style in enumerate(styles)
    ]
    curve = []
    for budget in (1, 2, 4, 8):
        selected = max(candidates[:budget], key=lambda item: item["reward"]["total"])
        curve.append(
            {
                "budget": budget,
                "selected_style": selected["style"],
                "reward": selected["reward"]["total"],
                "independent_quality": selected["quality"]["score"],
            }
        )
    return {
        "kind": "deterministic labelled-candidate search",
        "not_a_model_best_of_n_experiment": True,
        "curve": curve,
    }


def _hash_files(root: Path) -> dict[str, str]:
    ignored_roots = {
        ".git",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "build",
        "dist",
        "results",
    }
    values = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
  continue
        relative = path.relative_to(root).as_posix()
        parts = Path(relative).parts
        if parts[0] in ignored_roots or any(part.endswith(".egg-info") for part in parts):
  continue
        values[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return values

def reproduce(output: Path, mode: str = "local", seed_count: int = 4) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    receipt = soundness_receipt(seed_count, mode)
    ladder = reward_ladder(mode)
    controls = family_controls(mode)
    stability = stability_report(seed_count, mode)
    search = candidate_search(mode)
    sandbox = {
        "local": LocalSandbox().manifest(),
        "docker": DockerSandbox().manifest(),
        "docker_available_during_run": DockerSandbox().available(),
    }
    files = {
        "task_catalog.json": [task.public_dict() for task in task_catalog()],
        "soundness_receipt.json": receipt,
        "reward_ladder.json": ladder,
        "family_controls.json": controls,
        "stability.json": stability,
        "candidate_search.json": search,
        "sandbox_manifest.json": sandbox,
    }
    for name, value in files.items():
        (output / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "task_count": len(task_catalog()),
        "families": len({task.family for task in task_catalog()}),
        "false_accepts": receipt["false_accept"]["count"],
        "false_accept_trials": receipt["false_accept"]["trials"],
        "false_rejects": receipt["false_reject"]["count"],
        "false_reject_trials": receipt["false_reject"]["trials"],
        "reward_ladder_strictly_monotonic": ladder["strictly_monotonic"],
        "accepted_valid_controls": controls["accepted_valid"],
        "valid_controls": controls["valid_total"],
        "rejected_broken_tasks": controls["rejected_broken"],
        "broken_tasks": controls["broken_total"],
        "high_variance_cells": len(stability["high_variance"]),
        "docker_executed": mode == "docker",
        "frontier_model_panel": "not run",
        "model_best_of_n": "not run",
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    root = Path(__file__).resolve().parents[2]
    (output / "release_hashes.json").write_text(
        json.dumps(_hash_files(root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary
