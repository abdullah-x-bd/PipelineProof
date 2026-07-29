from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from taskapp import core as pipeline


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    Path(path).write_text(json.dumps(value, allow_nan=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    train = sub.add_parser("train")
    train.add_argument("--train", required=True)
    train.add_argument("--eval")
    train.add_argument("--artifact", required=True)

    predict = sub.add_parser("predict")
    predict.add_argument("--artifact", required=True)
    predict.add_argument("--input", required=True)
    predict.add_argument("--output", required=True)

    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--artifact", required=True)
    evaluate.add_argument("--train", required=True)
    evaluate.add_argument("--eval", required=True)
    evaluate.add_argument("--output", required=True)

    split = sub.add_parser("split")
    split.add_argument("--input", required=True)
    split.add_argument("--output", required=True)
    split.add_argument("--ratio", type=float, default=0.75)

    features = sub.add_parser("features")
    features.add_argument("--input", required=True)
    features.add_argument("--output", required=True)

    args = parser.parse_args()
    if args.command == "train":
        state = pipeline.train(read(args.train), read(args.eval) if args.eval else None)
        pipeline.save_state(state, args.artifact)
    elif args.command == "predict":
        state = pipeline.load_state(args.artifact)
        write(args.output, {"predictions": pipeline.predict(state, read(args.input))})
    elif args.command == "evaluate":
        state = pipeline.load_state(args.artifact)
        write(args.output, pipeline.evaluate(state, read(args.train), read(args.eval)))
    elif args.command == "split":
        write(args.output, pipeline.split(read(args.input), args.ratio))
    else:
        write(args.output, pipeline.build_features(read(args.input)))


if __name__ == "__main__":
    main()
