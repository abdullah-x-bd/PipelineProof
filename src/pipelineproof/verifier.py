from __future__ import annotations

import hashlib
import json
import math
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from pipelineproof.catalog import get_task
from pipelineproof.data import expected, make_rows
from pipelineproof.sandbox import DockerSandbox, LocalSandbox
from pipelineproof.schema import RewardBreakdown, TaskSpec, VerificationResult
from pipelineproof.templates import task_files

_IGNORED_PARTS = {"__pycache__", ".pytest_cache"}
_IGNORED_NAMES = {".coverage"}


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _ignored(path: Path) -> bool:
    return bool(_IGNORED_PARTS & set(path.parts)) or path.name in _IGNORED_NAMES or path.suffix == ".pyc"


def _surface_check(spec: TaskSpec, candidate: Path) -> tuple[bool, list[str]]:
    baseline = task_files(spec, "broken")
    changes: list[str] = []
    seen: set[str] = set()
    if not candidate.is_dir():
        return False, ["candidate_missing"]
    for path in candidate.rglob("*"):
        relative_path = path.relative_to(candidate)
        if _ignored(relative_path):
            continue
        relative = relative_path.as_posix()
        if path.is_symlink():
            changes.append(f"symlink:{relative}")
            continue
        if not path.is_file():
            continue
        seen.add(relative)
        if relative.startswith("src/"):
            continue
        if relative not in baseline:
            changes.append(f"added:{relative}")
            continue
        if _digest(path.read_bytes()) != _digest(baseline[relative].encode()):
            changes.append(f"changed:{relative}")
    for relative in baseline:
        if relative.startswith("src/"):
            continue
        if relative not in seen:
            changes.append(f"missing:{relative}")
    return not changes, sorted(changes)


def _runner(mode: str):
    if mode == "local":
        return LocalSandbox()
    if mode == "docker":
        runner = DockerSandbox()
        if not runner.available():
            raise RuntimeError("docker executable not found")
        return runner
    raise ValueError(f"unknown verifier mode: {mode}")


def _run_command(runner, candidate: Path, command: list[str], timeout_label: str) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="pipelineproof-command-") as directory:
        result = runner.run_command(command, candidate, Path(directory))
    if result.returncode == 0:
        return True, ""
    message = (result.stderr or result.stdout or timeout_label)[-2000:]
    return False, message


def _interface(runner, candidate: Path) -> tuple[bool, str]:
    return _run_command(runner, candidate, ["python", "-I", "run_pipeline.py", "--help"], "interface failed")


def _public_tests(runner, candidate: Path) -> tuple[bool, str]:
    return _run_command(runner, candidate, ["python", "-m", "pytest", "-q", "tests"], "public tests failed")


def execute_operations(runner, candidate: Path, operations: list[dict[str, Any]]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="pipelineproof-batch-") as directory:
        scratch = Path(directory)
        request = scratch / "request.json"
        output = scratch / "output.json"
        request.write_text(json.dumps({"operations": operations}), encoding="utf-8")
        result = runner.run_worker(candidate, request, output, scratch)
        if result.returncode != 0 or not output.exists():
            message = (result.stderr or result.stdout or "candidate execution failed")[-2000:]
            raise RuntimeError(message)
        if output.stat().st_size > 8_000_000:
            raise RuntimeError("candidate output exceeds limit")
        value = json.loads(output.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise RuntimeError("candidate output must be an object")
        return value


def _predictions(value: Any, count: int) -> list[float]:
    if not isinstance(value, list) or len(value) != count:
        raise ValueError("prediction length mismatch")
    result = [float(item) for item in value]
    if not all(math.isfinite(item) for item in result):
        raise ValueError("predictions must be finite")
    return result


def _rmse(actual: list[float], predicted: list[float]) -> float:
    if len(actual) != len(predicted) or not actual:
        raise ValueError("metric input mismatch")
    return float(np.sqrt(np.mean((np.asarray(actual) - np.asarray(predicted)) ** 2)))


def _strip(spec: TaskSpec, rows: list[dict[str, Any]]) -> list[dict[str, float]]:
    return [{name: float(row[name]) for name in spec.features} for row in rows]


def _feature_schema(spec: TaskSpec, candidate: Path, seed: int, runner):
    train = make_rows(spec, seed, 80)
    probe = _strip(spec, make_rows(spec, seed + 1, 24, shifted=True))
    permuted = [{name: row[name] for name in reversed(spec.features)} for row in probe]
    result = execute_operations(
        runner,
        candidate,
        [
            {"id": "state", "op": "train", "train": train},
            {"id": "loaded", "op": "roundtrip", "state": "state"},
            {"id": "normal", "op": "predict", "state": "state", "rows": probe},
            {"id": "loaded_pred", "op": "predict", "state": "loaded", "rows": probe},
            {"id": "permuted", "op": "predict", "state": "state", "rows": permuted},
        ],
    )
    normal = _predictions(result["normal"], len(probe))
    loaded = _predictions(result["loaded_pred"], len(probe))
    permuted_values = _predictions(result["permuted"], len(probe))
    error = _rmse(expected(spec, probe), normal)
    permutation_delta = max(abs(a - b) for a, b in zip(normal, permuted_values, strict=True))
    reload_delta = max(abs(a - b) for a, b in zip(normal, loaded, strict=True))
    return {
        "functional": error < 0.08,
        "causal": permutation_delta < 1e-9,
        "persistence": reload_delta < 1e-9,
    }, {
        "hidden_rmse": error,
        "permutation_delta": permutation_delta,
        "reload_delta": reload_delta,
    }


def _preprocessing_eval(spec: TaskSpec, candidate: Path, seed: int, runner):
    train = make_rows(spec, seed, 80)
    eval_a = make_rows(spec, seed + 1, 30)
    eval_b = make_rows(spec, seed + 2, 30, shifted=True)
    probe = _strip(spec, make_rows(spec, seed + 3, 20, shifted=True))
    result = execute_operations(
        runner,
        candidate,
        [
            {"id": "a", "op": "train", "train": train, "eval": eval_a},
            {"id": "b", "op": "train", "train": train, "eval": eval_b},
            {"id": "loaded", "op": "roundtrip", "state": "a"},
            {"id": "pred", "op": "predict", "state": "a", "rows": probe},
            {"id": "loaded_pred", "op": "predict", "state": "loaded", "rows": probe},
        ],
    )
    predictions = _predictions(result["pred"], len(probe))
    loaded = _predictions(result["loaded_pred"], len(probe))
    error = _rmse(expected(spec, probe), predictions)
    artifact_invariant = json.dumps(result["a"], sort_keys=True) == json.dumps(result["b"], sort_keys=True)
    reload_delta = max(abs(a - b) for a, b in zip(predictions, loaded, strict=True))
    return {
        "functional": error < 0.08,
        "causal": artifact_invariant,
        "persistence": reload_delta < 1e-9,
    }, {
        "hidden_rmse": error,
        "artifact_invariant": artifact_invariant,
        "reload_delta": reload_delta,
    }


def _serialization(spec: TaskSpec, candidate: Path, seed: int, runner):
    train = make_rows(spec, seed, 80)
    probe = _strip(spec, make_rows(spec, seed + 1, 7, shifted=True))
    mixed = probe[1:] + [probe[0]]
    result = execute_operations(
        runner,
        candidate,
        [
            {"id": "state", "op": "train", "train": train},
            {"id": "loaded", "op": "roundtrip", "state": "state"},
            {"id": "single", "op": "predict", "state": "loaded", "rows": [probe[0]]},
            {"id": "mixed", "op": "predict", "state": "loaded", "rows": mixed},
        ],
    )
    single = _predictions(result["single"], 1)
    mixed_values = _predictions(result["mixed"], len(mixed))
    error = _rmse(expected(spec, mixed), mixed_values)
    batch_delta = abs(single[0] - mixed_values[-1])
    return {
        "functional": error < 0.08,
        "causal": batch_delta < 1e-9,
        "persistence": batch_delta < 1e-9,
    }, {"hidden_rmse": error, "batch_composition_delta": batch_delta}


def _wrong_eval(spec: TaskSpec, candidate: Path, seed: int, runner):
    train = make_rows(spec, seed, 70)
    evaluation = make_rows(spec, seed + 1, 25, shifted=True)
    probe = _strip(spec, evaluation)
    result = execute_operations(
        runner,
        candidate,
        [
            {"id": "state", "op": "train", "train": train},
            {"id": "loaded", "op": "roundtrip", "state": "state"},
            {"id": "pred", "op": "predict", "state": "loaded", "rows": probe},
            {"id": "report", "op": "evaluate", "state": "loaded", "train": train, "eval": evaluation},
        ],
    )
    predictions = _predictions(result["pred"], len(probe))
    error = _rmse(expected(spec, evaluation), predictions)
    trusted = _rmse([float(row["target"]) for row in evaluation], predictions)
    report = result["report"]
    if not isinstance(report, dict):
        raise ValueError("evaluation report must be an object")
    reported = float(report.get("rmse", float("inf")))
    agreement = abs(reported - trusted)
    return {
        "functional": error < 0.08,
        "causal": math.isfinite(reported) and agreement < 1e-9,
        "persistence": math.isfinite(reported),
    }, {"hidden_rmse": error, "reported_rmse": reported, "trusted_rmse": trusted}


def _group_leakage(spec: TaskSpec, candidate: Path, seed: int, runner):
    rows = make_rows(spec, seed, 90, groups=True)
    result = execute_operations(
        runner,
        candidate,
        [
            {"id": "first", "op": "split", "rows": rows, "ratio": 0.75},
            {"id": "second", "op": "split", "rows": rows, "ratio": 0.75},
        ],
    )
    first = result["first"]
    if not isinstance(first, dict):
        raise ValueError("split output must be an object")
    train_rows = first.get("train", [])
    eval_rows = first.get("eval", [])
    if not isinstance(train_rows, list) or not isinstance(eval_rows, list):
        raise ValueError("split rows must be lists")
    row_ids = [row.get("row_id") for row in train_rows + eval_rows]
    coverage = len(row_ids) == len(rows) and len(set(row_ids)) == len(rows)
    ratio = len(train_rows) / len(rows)
    train_groups = {row.get("group_id") for row in train_rows}
    eval_groups = {row.get("group_id") for row in eval_rows}
    overlap = train_groups & eval_groups
    deterministic = result["first"] == result["second"]
    return {
        "functional": coverage and 0.55 <= ratio <= 0.90,
        "causal": not overlap,
        "persistence": deterministic,
    }, {"train_ratio": ratio, "group_overlap": len(overlap)}


def _target_leakage(spec: TaskSpec, candidate: Path, seed: int, runner):
    train = make_rows(spec, seed, 80)
    probe = make_rows(spec, seed + 1, 20, shifted=True)
    altered = [
        dict(row, target=float(row["target"]) + 500.0, target_proxy=float(row["target_proxy"]) + 500.0)
        for row in probe
    ]
    result = execute_operations(
        runner,
        candidate,
        [
            {"id": "state", "op": "train", "train": train},
            {"id": "loaded", "op": "roundtrip", "state": "state"},
            {"id": "first", "op": "predict", "state": "loaded", "rows": probe},
            {"id": "second", "op": "predict", "state": "loaded", "rows": altered},
            {"id": "features", "op": "features", "rows": probe[:3]},
        ],
    )
    first = _predictions(result["first"], len(probe))
    second = _predictions(result["second"], len(probe))
    error = _rmse(expected(spec, probe), first)
    metadata_delta = max(abs(a - b) for a, b in zip(first, second, strict=True))
    features = result["features"]
    if not isinstance(features, dict):
        raise ValueError("feature report must be an object")
    columns = features.get("columns", [])
    no_target = isinstance(columns, list) and not ({"target", "target_proxy"} & set(columns))
    return {
        "functional": error < 0.08,
        "causal": metadata_delta < 1e-9 and no_target,
        "persistence": True,
    }, {"hidden_rmse": error, "metadata_delta": metadata_delta, "columns": columns}


_FAMILY_CHECKS = {
    "feature_schema": _feature_schema,
    "preprocessing_eval": _preprocessing_eval,
    "serialization": _serialization,
    "wrong_eval": _wrong_eval,
    "group_leakage": _group_leakage,
    "target_leakage": _target_leakage,
}


def verify_spec(
    spec: TaskSpec,
    candidate: Path,
    seed: int | None = None,
    mode: str = "local",
) -> VerificationResult:
    candidate = candidate.resolve()
    protected, surface_changes = _surface_check(spec, candidate)
    runner = _runner(mode)
    interface, interface_error = _interface(runner, candidate)
    public_tests, public_error = _public_tests(runner, candidate) if interface else (False, "not run")
    family = {"functional": False, "causal": False, "persistence": False}
    details: dict[str, Any] = {"surface_changes": surface_changes}
    if interface_error:
        details["interface_error"] = interface_error
    if public_error:
        details["public_test_error"] = public_error
    if interface:
        try:
            family, family_details = _FAMILY_CHECKS[spec.family](
                spec,
                candidate,
                spec.seed + 9000 if seed is None else seed,
                runner,
            )
            details.update(family_details)
        except Exception as error:
            details["execution_error"] = f"{type(error).__name__}: {error}"
    checks = {
        "interface": interface,
        "public_tests": public_tests,
        "functional": bool(family["functional"]),
        "causal": bool(family["causal"]),
        "persistence": bool(family["persistence"]),
        "protected": protected,
    }
    functional = checks["functional"]
    reward = RewardBreakdown(
        interface=float(checks["interface"]),
        public_tests=float(checks["public_tests"]),
        functional=float(functional),
        causal=float(checks["causal"] and functional),
        persistence=float(checks["persistence"] and functional),
        protected=float(checks["protected"]),
    )
    return VerificationResult(
        task_id=spec.task_id,
        candidate=str(candidate),
        verifier_mode=mode,
        reward=reward,
        passed=all(checks.values()) and reward.total == 1.0,
        checks=checks,
        details=details,
    )


def verify(task_id: str, candidate: Path, seed: int | None = None, mode: str = "local") -> VerificationResult:
    return verify_spec(get_task(task_id), candidate, seed, mode)
