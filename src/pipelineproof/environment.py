"""Environment metadata and loader entry point.

The initial loader intentionally exposes only public configuration. Hidden tests,
oracle implementations, and private seeds belong to the trusted verifier runtime,
not to the package surface available to a solving agent.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class EnvironmentSpec:
    """Public description of a PipelineProof environment build."""

    name: str
    version: str
    task_root: Path
    integrity_contracts: tuple[str, ...]
    mutable_globs: tuple[str, ...]
    protected_globs: tuple[str, ...]


def load_environment(task_root: str | Path | None = None) -> EnvironmentSpec:
    """Load the public environment specification.

    Args:
        task_root: Optional path containing public task instances. When omitted,
            the conventional repository location ``tasks/public`` is used.

    Returns:
        An immutable public environment specification.
    """

    root = Path(task_root) if task_root is not None else Path("tasks/public")
    return EnvironmentSpec(
        name="pipelineproof",
        version="0.1.0",
        task_root=root,
        integrity_contracts=(
            "training-data-provenance",
            "evaluation-validity",
            "train-serving-equivalence",
        ),
        mutable_globs=("src/**", "config/**"),
        protected_globs=(
            "tests/**",
            "data/**",
            "hidden_assets/**",
            "oracle/**",
            "pyproject.toml",
        ),
    )
