from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    family: str
    variant: str
    split: str
    features: tuple[str, str, str]
    coefficients: tuple[float, float, float]
    intercept: float
    seed: int
    writable_paths: tuple[str, ...] = ("src/**",)
    protected_paths: tuple[str, ...] = (
        "ISSUE.md",
        "manifest.json",
        "run_pipeline.py",
        "tests/**",
        "data/**",
    )

    def public_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "family": self.family,
            "variant": self.variant,
            "split": self.split,
            "features": list(self.features),
            "writable_paths": list(self.writable_paths),
            "protected_paths": list(self.protected_paths),
        }

    def private_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for name in ("features", "coefficients", "writable_paths", "protected_paths"):
            data[name] = list(data[name])
        return data

    @classmethod
    def from_private_dict(cls, data: dict[str, Any]) -> TaskSpec:
        values = dict(data)
        for name in ("features", "coefficients", "writable_paths", "protected_paths"):
            if name in values:
                values[name] = tuple(values[name])
        return cls(**values)


@dataclass(frozen=True)
class RewardBreakdown:
    interface: float = 0.0
    public_tests: float = 0.0
    functional: float = 0.0
    causal: float = 0.0
    persistence: float = 0.0
    protected: float = 0.0

    @property
    def total(self) -> float:
        return round(
            0.10 * self.interface
            + 0.10 * self.public_tests
            + 0.25 * self.functional
            + 0.35 * self.causal
            + 0.10 * self.persistence
            + 0.10 * self.protected,
            6,
        )

    def to_dict(self) -> dict[str, float]:
        data = asdict(self)
        data["total"] = self.total
        return data


@dataclass(frozen=True)
class VerificationResult:
    task_id: str
    candidate: str
    verifier_mode: str
    reward: RewardBreakdown
    passed: bool
    checks: dict[str, bool]
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "candidate": self.candidate,
            "verifier_mode": self.verifier_mode,
            "reward": self.reward.to_dict(),
            "passed": self.passed,
            "checks": self.checks,
            "details": self.details,
        }


@dataclass(frozen=True)
class EnvironmentInfo:
    root: Path
    task_count: int
    families: tuple[str, ...]
