from __future__ import annotations

import json
import math
import random
from pathlib import Path

import numpy as np

FEATURES = ['alpha', 'beta', 'gamma']
SEED = 1100


def _matrix(rows, names=None):
    selected = FEATURES if names is None else names
    return np.asarray([[float(row[name]) for name in selected] for row in rows], dtype=float)


def _targets(rows):
    return np.asarray([float(row["target"]) for row in rows], dtype=float)


def _fit_linear(matrix, targets):
    design = np.column_stack([np.ones(len(matrix)), matrix])
    values, *_ = np.linalg.lstsq(design, targets, rcond=None)
    return {"intercept": float(values[0]), "coef": [float(value) for value in values[1:]]}


def _linear_predict(model, matrix):
    coefficient = np.asarray(model["coef"], dtype=float)
    return [float(model["intercept"] + row @ coefficient) for row in matrix]


def save_state(state, path):
    Path(path).write_text(json.dumps(state, sort_keys=True), encoding="utf-8")


def load_state(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))



def train(train_rows, eval_rows=None):
    model = _fit_linear(_matrix(train_rows), _targets(train_rows))
    return {
        "model": model,
        "features": FEATURES,
        "mean_target": float(np.mean(_targets(train_rows))),
    }


def predict(state, rows):
    return _linear_predict(state["model"], _matrix(rows, state["features"]))



def evaluate(state, train_rows, eval_rows):
    predictions = predict(state, eval_rows)
    errors = np.asarray(predictions) - _targets(eval_rows)
    return {"rmse": float(np.sqrt(np.mean(errors ** 2)))}


def split(rows, ratio=0.75):
    cut = int(len(rows) * ratio)
    return {"train": rows[:cut], "eval": rows[cut:]}


def build_features(rows):
    return {"columns": FEATURES, "matrix": _matrix(rows).tolist()}
