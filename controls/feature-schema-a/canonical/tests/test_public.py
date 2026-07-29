from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from taskapp import core as pipeline


def rows():
    return [
        {name: float(index + offset) for offset, name in enumerate(pipeline.FEATURES)}
        | {"target": float(index), "target_proxy": float(index), "row_id": str(index), "group_id": f"g{index // 2}"}
        for index in range(8)
    ]


def test_pipeline_runs():
    data = rows()
    state = pipeline.train(data[:6], data[6:])
    predictions = pipeline.predict(state, data[6:])
    assert len(predictions) == 2
    assert all(isinstance(value, float) for value in predictions)


def test_public_shapes():
    data = rows()
    assert pipeline.split(data)["train"]
    features = pipeline.build_features(data[:2])
    assert len(features["matrix"]) == 2
