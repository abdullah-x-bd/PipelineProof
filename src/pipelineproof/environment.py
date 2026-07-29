from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pipelineproof.catalog import families, task_catalog
from pipelineproof.generator import generate_tasks
from pipelineproof.quality import quality_score
from pipelineproof.schema import TaskSpec
from pipelineproof.verifier import verify, verify_spec


@dataclass(frozen=True)
class PipelineProofEnvironment:
    root: Path

    @property
    def tasks(self):
        return task_catalog()

    @property
    def families(self):
        return families()

    def generate(self, output: Path):
        return generate_tasks(output)

    def verify(self, task_id: str, candidate: Path, seed: int | None = None, mode: str = "local"):
        return verify(task_id, candidate, seed, mode)

    def verify_spec(self, spec: TaskSpec, candidate: Path, seed: int | None = None, mode: str = "local"):
        return verify_spec(spec, candidate, seed, mode)

    def quality(self, spec: TaskSpec, candidate: Path, seed: int, mode: str = "local"):
        return quality_score(spec, candidate, seed, mode)


def load_environment(root: str | Path | None = None) -> PipelineProofEnvironment:
    return PipelineProofEnvironment(Path(root or ".").resolve())
