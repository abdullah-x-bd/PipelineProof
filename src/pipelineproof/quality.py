from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from pipelineproof.data import expected, make_rows
from pipelineproof.sandbox import DockerSandbox, LocalSandbox
from pipelineproof.schema import TaskSpec
from pipelineproof.verifier import _predictions, _rmse, _strip, execute_operations


def _runner(mode: str):
    if mode == "local":
        return LocalSandbox()
    if mode == "docker":
        runner = DockerSandbox()
        if not runner.available():
            raise RuntimeError("docker executable not found")
        return runner
    raise ValueError(mode)


def _score(checks: dict[str, bool], weights: dict[str, float] | None = None) -> float:
    if weights is None:
        return sum(checks.values()) / len(checks)
    return sum(float(checks[name]) * weight for name, weight in weights.items())


def quality_score(spec: TaskSpec, candidate: Path, seed: int, mode: str = "local") -> dict[str, Any]:
    runner = _runner(mode)
    try:
        if spec.family == "feature_schema":
            train = make_rows(spec, seed, 100)
            probe = _strip(spec, make_rows(spec, seed + 1, 30, shifted=True))
            rotations = []
            names = list(spec.features)
            for shift in range(len(names)):
                order = names[shift:] + names[:shift]
                rotations.append([{name: row[name] for name in order} for row in probe])
            operations = [{"id": "state", "op": "train", "train": train}]
            operations.extend(
                {"id": f"p{index}", "op": "predict", "state": "state", "rows": rows}
                for index, rows in enumerate(rotations)
            )
            result = execute_operations(runner, candidate, operations)
            predictions = [_predictions(result[f"p{index}"], len(probe)) for index in range(len(rotations))]
            checks = {
                "extreme_accuracy": _rmse(expected(spec, probe), predictions[0]) < 0.08,
                "all_rotations": all(
                    max(abs(a - b) for a, b in zip(predictions[0], values, strict=True)) < 1e-9
                    for values in predictions[1:]
                ),
            }
        elif spec.family == "preprocessing_eval":
            train = make_rows(spec, seed, 90)
            eval_a = make_rows(spec, seed + 1, 25)
            eval_b = make_rows(spec, seed + 2, 25, shifted=True)
            eval_c = [dict(row, **{name: float(row[name]) * 20 for name in spec.features}) for row in eval_b]
            probe = _strip(spec, make_rows(spec, seed + 3, 25, shifted=True))
            result = execute_operations(
                runner,
                candidate,
                [
                    {"id": "a", "op": "train", "train": train, "eval": eval_a},
                    {"id": "b", "op": "train", "train": train, "eval": eval_b},
                    {"id": "c", "op": "train", "train": train, "eval": eval_c},
                    {"id": "pred", "op": "predict", "state": "a", "rows": probe},
                ],
            )
            pred = _predictions(result["pred"], len(probe))
            states = [json.dumps(result[name], sort_keys=True) for name in ("a", "b", "c")]
            checks = {
                "shifted_accuracy": _rmse(expected(spec, probe), pred) < 0.08,
                "three_way_artifact_invariance": len(set(states)) == 1,
            }
        elif spec.family == "serialization":
            train = make_rows(spec, seed, 100)
            probe = _strip(spec, make_rows(spec, seed + 1, 9, shifted=True))
            row = probe[0]
            batches = [[row], probe[:3], probe[1:] + [row]]
            operations = [
                {"id": "state", "op": "train", "train": train},
                {"id": "loaded", "op": "roundtrip", "state": "state"},
            ]
            operations.extend(
                {"id": f"p{index}", "op": "predict", "state": "loaded", "rows": rows}
                for index, rows in enumerate(batches)
            )
            result = execute_operations(runner, candidate, operations)
            values = [_predictions(result[f"p{index}"], len(rows)) for index, rows in enumerate(batches)]
            same_row = [values[0][0], values[1][0], values[2][-1]]
            checks = {
                "batch_invariance": max(same_row) - min(same_row) < 1e-9,
                "large_batch_accuracy": _rmse(expected(spec, batches[2]), values[2]) < 0.08,
            }
        elif spec.family == "wrong_eval":
            train = make_rows(spec, seed, 90)
            evaluation = make_rows(spec, seed + 1, 33, shifted=True)
            probe = _strip(spec, evaluation)
            result = execute_operations(
                runner,
                candidate,
                [
                    {"id": "state", "op": "train", "train": train},
                    {"id": "pred", "op": "predict", "state": "state", "rows": probe},
                    {"id": "report", "op": "evaluate", "state": "state", "train": train, "eval": evaluation},
                ],
            )
            pred = _predictions(result["pred"], len(probe))
            trusted = _rmse([float(row["target"]) for row in evaluation], pred)
            reported = float(result["report"].get("rmse", float("inf")))
            checks = {
                "shifted_accuracy": _rmse(expected(spec, evaluation), pred) < 0.08,
                "second_report_agreement": math.isfinite(reported) and abs(reported - trusted) < 1e-9,
            }
        elif spec.family == "group_leakage":
            rows = make_rows(spec, seed, 103, groups=True, uneven_groups=True)
            result = execute_operations(
                runner,
                candidate,
                [
                    {"id": "a", "op": "split", "rows": rows, "ratio": 0.67},
                    {"id": "b", "op": "split", "rows": rows, "ratio": 0.67},
                ],
            )
            first = result["a"]
            train_rows = first.get("train", [])
            eval_rows = first.get("eval", [])
            overlap = {row["group_id"] for row in train_rows} & {row["group_id"] for row in eval_rows}
            identifiers = [row["row_id"] for row in train_rows + eval_rows]
            checks = {
                "uneven_group_separation": not overlap,
                "complete_partition": len(identifiers) == len(rows) and len(set(identifiers)) == len(rows),
                "deterministic": result["a"] == result["b"],
            }
        else:
            train = make_rows(spec, seed, 90)
            probe = make_rows(spec, seed + 1, 25, shifted=True)
            altered = [
                dict(row, target=-999.0, target_proxy=999.0, future_target=1234.0, annotation="held-out")
                for row in probe
            ]
            result = execute_operations(
                runner,
                candidate,
                [
                    {"id": "state", "op": "train", "train": train},
                    {"id": "a", "op": "predict", "state": "state", "rows": probe},
                    {"id": "b", "op": "predict", "state": "state", "rows": altered},
                    {"id": "features", "op": "features", "rows": altered[:4]},
                ],
            )
            first = _predictions(result["a"], len(probe))
            second = _predictions(result["b"], len(probe))
            columns = result["features"].get("columns", [])
            checks = {
                "metadata_invariance": max(abs(a - b) for a, b in zip(first, second, strict=True)) < 1e-9,
                "exact_feature_contract": columns == list(spec.features),
                "shifted_accuracy": _rmse(expected(spec, probe), first) < 0.08,
            }
        weights = {"extreme_accuracy": 0.6, "all_rotations": 0.4} if spec.family == "feature_schema" else None
        return {"task_id": spec.task_id, "score": _score(checks, weights), "checks": checks}
    except Exception as error:
        return {
            "task_id": spec.task_id,
            "score": 0.0,
            "checks": {},
            "error": f"{type(error).__name__}: {error}",
        }
