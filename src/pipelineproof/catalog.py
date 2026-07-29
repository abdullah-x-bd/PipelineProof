from __future__ import annotations

import json
from pathlib import Path

from pipelineproof.schema import TaskSpec

_FAMILIES = (
    "feature_schema",
    "preprocessing_eval",
    "serialization",
    "wrong_eval",
    "group_leakage",
    "target_leakage",
)

_FEATURES = (
    ("alpha", "beta", "gamma"),
    ("signal", "context", "reserve"),
    ("mass", "temperature", "pressure"),
    ("volume", "density", "viscosity"),
    ("exposure", "duration", "intensity"),
    ("capacity", "latency", "load"),
)

_COEFFICIENTS = (
    (4.0, -2.0, 0.5),
    (-1.5, 3.25, 2.0),
    (2.5, 1.0, -3.0),
    (0.75, -4.0, 1.5),
    (3.0, 0.25, -1.75),
    (-2.0, 1.25, 4.5),
)


def task_catalog() -> tuple[TaskSpec, ...]:
    return tuple(
        TaskSpec(
            task_id=f"{family.replace('_', '-')}-a",
            family=family,
            variant="a",
            split="development",
            features=_FEATURES[index],
            coefficients=_COEFFICIENTS[index],
            intercept=1.5 + index,
            seed=1100 + index * 17,
        )
        for index, family in enumerate(_FAMILIES)
    )


def get_task(task_id: str) -> TaskSpec:
    for task in task_catalog():
        if task.task_id == task_id:
            return task
    raise KeyError(task_id)


def load_private_spec(path: Path) -> TaskSpec:
    return TaskSpec.from_private_dict(json.loads(path.read_text(encoding="utf-8")))


def families() -> tuple[str, ...]:
    return _FAMILIES
