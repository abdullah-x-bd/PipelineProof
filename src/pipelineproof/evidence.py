from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_EVIDENCE_FILES = {
    "attack_matrix.json",
    "candidate_search.json",
    "environment.json",
    "family_controls.json",
    "local_docker_parity.json",
    "release_hashes.json",
    "reward_ladder.json",
    "sandbox_manifest.json",
    "soundness_receipt.json",
    "stability.json",
    "summary.json",
    "summary.md",
    "task_catalog.json",
    "valid_repair_matrix.json",
}

FORBIDDEN_SOURCE_PARTS = {
    ".git",
    ".venv",
    "build",
    "dist",
    "pipelineproof.egg-info",
    "results",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_evidence_manifest(root: Path) -> Path:
    """Write SHA-256 digests for every evidence artifact except the manifest itself."""

    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "MANIFEST.sha256":
            continue
        rows.append(f"{_sha256(path)}  {path.relative_to(root).as_posix()}")
    manifest = root / "MANIFEST.sha256"
    manifest.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return manifest


def _validate_manifest(root: Path, errors: list[str]) -> None:
    manifest = root / "MANIFEST.sha256"
    if not manifest.is_file():
        errors.append("missing MANIFEST.sha256")
        return
    seen: set[str] = set()
    for line_number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError:
            errors.append(f"invalid manifest line {line_number}")
            continue
        path = root / relative
        seen.add(relative)
        if not path.is_file():
            errors.append(f"manifest references missing file: {relative}")
        elif _sha256(path) != digest:
            errors.append(f"manifest digest mismatch: {relative}")
    expected = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "MANIFEST.sha256"
    }
    missing = sorted(expected - seen)
    if missing:
        errors.append(f"manifest omits files: {', '.join(missing)}")


def validate_evidence_bundle(root: Path, require_docker: bool = True) -> dict[str, Any]:
    """Validate release evidence structure, consistency, and release-gate invariants."""

    root = root.resolve()
    errors: list[str] = []
    if not root.is_dir():
        return {"valid": False, "errors": [f"not a directory: {root}"]}

    missing = sorted(name for name in REQUIRED_EVIDENCE_FILES if not (root / name).is_file())
    if missing:
        errors.append(f"missing required files: {', '.join(missing)}")
        return {"valid": False, "errors": errors}

    try:
        summary = _read_json(root / "summary.json")
        receipt = _read_json(root / "soundness_receipt.json")
        attacks = _read_json(root / "attack_matrix.json")
        repairs = _read_json(root / "valid_repair_matrix.json")
        parity = _read_json(root / "local_docker_parity.json")
        environment = _read_json(root / "environment.json")
        release_hashes = _read_json(root / "release_hashes.json")
    except (json.JSONDecodeError, OSError, TypeError) as error:
        errors.append(f"failed to read evidence JSON: {error}")
        return {"valid": False, "errors": errors}

    attack_evidence = receipt.get("attack_evidence", {})
    control_evidence = receipt.get("valid_control_evidence", {})
    false_accept = receipt.get("false_accept", {})
    false_reject = receipt.get("false_reject", {})

    checks = [
        (summary.get("structural_attack_cells") == len(attacks), "attack-cell count mismatch"),
        (
            summary.get("structural_valid_control_cells") == len(repairs),
            "valid-repair-cell count mismatch",
        ),
        (summary.get("invalid_attack_trials") == 0, "invalid attack trials are non-zero"),
        (summary.get("false_accepts") == 0, "false accepts are non-zero"),
        (summary.get("false_rejects") == 0, "false rejects are non-zero"),
        (
            summary.get("reward_ladder_strictly_monotonic") is True,
            "reward ladder is not strictly monotonic",
        ),
        (summary.get("high_variance_cells") == 0, "high-variance control cells are non-zero"),
        (
            false_accept.get("count") == summary.get("false_accepts"),
            "soundness/summary false-accept mismatch",
        ),
        (
            false_reject.get("count") == summary.get("false_rejects"),
            "soundness/summary false-reject mismatch",
        ),
        (
            attack_evidence.get("clean_rejections") == attack_evidence.get("valid_attack_trials"),
            "not every valid attack was rejected by its intended detector",
        ),
        (
            attack_evidence.get("other_rejections") == 0,
            "some attacks were rejected only by an unintended detector",
        ),
        (
            control_evidence.get("false_reject", {}).get("count") == 0,
            "valid-control receipt contains false rejects",
        ),
        (
            all(row.get("invalid_trials") == 0 for row in attacks),
            "attack matrix contains invalid trials",
        ),
        (
            all(row.get("false_accepts") == 0 for row in attacks),
            "attack matrix contains false accepts",
        ),
        (
            all(row.get("other_rejections") == 0 for row in attacks),
            "attack matrix contains unintended-detector-only rejections",
        ),
        (
            all(row.get("all_accepted") is True for row in repairs),
            "valid-repair matrix contains a rejected structural repair",
        ),
    ]
    for passed, message in checks:
        if not passed:
            errors.append(message)

    if require_docker:
        docker_checks = [
            (summary.get("docker_executed") is True, "canonical evidence was not run in Docker"),
            (
                summary.get("local_docker_parity_status") == "complete",
                "local/Docker parity is incomplete",
            ),
            (
                summary.get("local_docker_disagreements") == 0,
                "local/Docker parity contains disagreements",
            ),
            (parity.get("status") == "complete", "parity report is incomplete"),
            (parity.get("disagreement_count") == 0, "parity report contains disagreements"),
            (environment.get("requested_mode") == "docker", "environment mode is not Docker"),
            (
                isinstance(environment.get("docker_image_id"), str)
                and environment["docker_image_id"].startswith("sha256:"),
                "Docker image identity is missing",
            ),
        ]
        for passed, message in docker_checks:
            if not passed:
                errors.append(message)

    if not environment.get("source_commit"):
        errors.append("source commit is missing from environment metadata")

    invalid_hash_paths = [
        path
        for path in release_hashes
        if FORBIDDEN_SOURCE_PARTS & set(Path(path).parts)
    ]
    if invalid_hash_paths:
        errors.append(f"release hashes include transient paths: {', '.join(invalid_hash_paths)}")

    _validate_manifest(root, errors)
    return {
        "valid": not errors,
        "errors": errors,
        "root": str(root),
        "structural_attack_cells": len(attacks),
        "structural_valid_control_cells": len(repairs),
        "source_commit": environment.get("source_commit"),
        "docker_image_id": environment.get("docker_image_id"),
    }
