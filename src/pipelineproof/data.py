from __future__ import annotations

import hashlib
from typing import Any

from pipelineproof.schema import TaskSpec

_SCALE = float((1 << 64) - 1)


def _unit(seed: int, index: int, label: str) -> float:
    payload = f"{seed}:{index}:{label}".encode()
    value = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
    return value / _SCALE


def _uniform(seed: int, index: int, label: str, low: float, high: float) -> float:
    return low + (high - low) * _unit(seed, index, label)


def make_rows(
    spec: TaskSpec,
    seed: int,
    count: int,
    *,
    shifted: bool = False,
    groups: bool = False,
    uneven_groups: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    group_index = 0
    group_remaining = 1
    center = 4.5 if shifted else 0.0
    for index in range(count):
        values = [
            _uniform(seed, index, f"feature:{name}", -3.0, 3.0) + center
            for name in spec.features
        ]
        target = spec.intercept + sum(
            coefficient * value
            for coefficient, value in zip(spec.coefficients, values, strict=True)
        )
        target += _uniform(seed, index, "target-noise", -0.015, 0.015)
        row: dict[str, Any] = dict(zip(spec.features, values, strict=True))
        row["target"] = target
        row["target_proxy"] = target + _uniform(seed, index, "proxy-noise", -0.002, 0.002)
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
        + sum(
            coefficient * float(row[name])
            for coefficient, name in zip(spec.coefficients, spec.features, strict=True)
        )
        for row in rows
    ]


def public_rows(spec: TaskSpec) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups = spec.family == "group_leakage"
    return (
        make_rows(spec, spec.seed, 30, groups=groups),
        make_rows(spec, spec.seed + 1, 5, groups=groups),
    )
