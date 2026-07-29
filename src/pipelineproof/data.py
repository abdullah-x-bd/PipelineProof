from __future__ import annotations

import random
from typing import Any

from pipelineproof.schema import TaskSpec


def _symmetric_noise(rng: random.Random, amplitude: float) -> float:
    return (2.0 * rng.random() - 1.0) * amplitude


def make_rows(
    spec: TaskSpec,
    seed: int,
    count: int,
    *,
    shifted: bool = False,
    groups: bool = False,
    uneven_groups: bool = False,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    group_index = 0
    group_remaining = 1
    for index in range(count):
        center = 4.5 if shifted else 0.0
        values = [rng.uniform(-3.0, 3.0) + center for _ in spec.features]
        target = spec.intercept + sum(c * x for c, x in zip(spec.coefficients, values, strict=True))
        target += _symmetric_noise(rng, 0.015)
        row: dict[str, Any] = dict(zip(spec.features, values, strict=True))
        row["target"] = target
        row["target_proxy"] = target + _symmetric_noise(rng, 0.002)
        row["row_id"] = f"r{seed}-{index}"
        if groups:
            if uneven_groups:
                if group_remaining == 0:
                    group_index += 1
                    group_remaining = 1 + group_index % 5
                row["group_id"] = f"g{group_index}"
                group_remaining -= 1
            else:
                row["group_id"] = f"g{index // 3}"
        rows.append(row)
    return rows


def expected(spec: TaskSpec, rows: list[dict[str, Any]]) -> list[float]:
    return [
        spec.intercept
        + sum(c * float(row[name]) for c, name in zip(spec.coefficients, spec.features, strict=True))
        for row in rows
    ]


def public_rows(spec: TaskSpec) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups = spec.family == "group_leakage"
    return (
        make_rows(spec, spec.seed, 30, groups=groups),
        make_rows(spec, spec.seed + 1, 5, groups=groups),
    )
