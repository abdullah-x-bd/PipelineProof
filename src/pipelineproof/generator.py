from __future__ import annotations

import shutil
from collections.abc import Iterable
from pathlib import Path

from pipelineproof.catalog import task_catalog
from pipelineproof.schema import TaskSpec
from pipelineproof.templates import write_task


def generate_specs(specs: Iterable[TaskSpec], output: Path, style: str = "broken") -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    generated = []
    for spec in specs:
        destination = output / spec.task_id
        if destination.exists():
            shutil.rmtree(destination)
        generated.append(write_task(spec, destination, style))
    return generated


def generate_tasks(output: Path, style: str = "broken") -> list[Path]:
    return generate_specs(task_catalog(), output, style)
