from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

_REQUIRED_FIELDS = {
    "model",
    "provider_route",
    "harness",
    "task_id",
    "rollout_id",
    "reward",
    "passed",
    "independent_quality",
    "failure_class",
}


def load_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number} is not an object")
        missing = sorted(_REQUIRED_FIELDS - value.keys())
        if missing:
            raise ValueError(f"line {line_number} missing fields: {', '.join(missing)}")
        reward = float(value["reward"])
        quality = float(value["independent_quality"])
        if not 0.0 <= reward <= 1.0:
            raise ValueError(f"line {line_number} reward outside [0, 1]")
        if not 0.0 <= quality <= 1.0:
            raise ValueError(f"line {line_number} independent_quality outside [0, 1]")
        value = dict(value)
        value["reward"] = reward
        value["independent_quality"] = quality
        value["passed"] = bool(value["passed"])
        records.append(value)
    if not records:
        raise ValueError("no rollout records found")
    return records


def _bootstrap_interval(values: list[float], seed: int = 0, draws: int = 10_000) -> list[float]:
    if not values:
        raise ValueError("cannot estimate an empty sample")
    if len(values) == 1:
        return [values[0], values[0]]
    generator = np.random.default_rng(seed)
    array = np.asarray(values, dtype=float)
    indices = generator.integers(0, len(array), size=(draws, len(array)))
    means = array[indices].mean(axis=1)
    low, high = np.quantile(means, [0.025, 0.975])
    return [float(low), float(high)]


def _cell_key(record: dict[str, Any]) -> tuple[str, str, str]:
    return str(record["model"]), str(record["provider_route"]), str(record["harness"])


def model_panel(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[_cell_key(record)].append(record)
    rows = []
    for index, (key, items) in enumerate(sorted(groups.items())):
        rewards = [float(item["reward"]) for item in items]
        qualities = [float(item["independent_quality"]) for item in items]
        rows.append(
            {
                "model": key[0],
                "provider_route": key[1],
                "harness": key[2],
                "rollouts": len(items),
                "tasks": len({item["task_id"] for item in items}),
                "mean_reward": float(np.mean(rewards)),
                "reward_bootstrap_95": _bootstrap_interval(rewards, seed=1000 + index),
                "mean_independent_quality": float(np.mean(qualities)),
                "quality_bootstrap_95": _bootstrap_interval(qualities, seed=2000 + index),
                "pass_rate": sum(bool(item["passed"]) for item in items) / len(items),
            }
        )
    ranked = sorted(rows, key=lambda row: row["reward_bootstrap_95"][0], reverse=True)
    for rank, row in enumerate(ranked, start=1):
        row["lower_bound_rank"] = rank
    return {"cells": ranked, "ranking_basis": "reward bootstrap 95% lower bound"}


def best_of_n(records: Iterable[dict[str, Any]], budgets: tuple[int, ...] = (1, 2, 4, 8)) -> dict[str, Any]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        key = (*_cell_key(record), str(record["task_id"]))
        groups[key].append(record)
    curves = []
    cells = sorted({_cell_key(item) for items in groups.values() for item in items})
    for cell in cells:
        task_groups = {
            key[3]: sorted(items, key=lambda item: str(item["rollout_id"]))
            for key, items in groups.items()
            if key[:3] == cell
        }
        points = []
        for budget in budgets:
            selected = []
            for items in task_groups.values():
                if len(items) < budget:
                    continue
                selected.append(max(items[:budget], key=lambda item: float(item["reward"])))
            if selected:
                points.append(
                    {
                        "budget": budget,
                        "tasks": len(selected),
                        "mean_selected_reward": float(np.mean([item["reward"] for item in selected])),
                        "mean_independent_quality": float(
                            np.mean([item["independent_quality"] for item in selected])
                        ),
                    }
                )
        curves.append(
            {
                "model": cell[0],
                "provider_route": cell[1],
                "harness": cell[2],
                "points": points,
            }
        )
    return {"budgets": list(budgets), "curves": curves}


def failure_breakdown(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    for record in records:
        groups[_cell_key(record)][str(record["failure_class"])] += 1
    return {
        "cells": [
            {
                "model": key[0],
                "provider_route": key[1],
                "harness": key[2],
                "counts": dict(sorted(counts.items())),
            }
            for key, counts in sorted(groups.items())
        ]
    }


def write_model_report(input_path: Path, output: Path) -> dict[str, Any]:
    records = load_records(input_path)
    output.mkdir(parents=True, exist_ok=True)
    files = {
        "model_panel.json": model_panel(records),
        "best_of_n.json": best_of_n(records),
        "failure_breakdown.json": failure_breakdown(records),
    }
    for name, value in files.items():
        (output / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"records": len(records), "output": str(output), "files": sorted(files)}
