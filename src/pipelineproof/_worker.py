from __future__ import annotations

import importlib.abc
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


class _BlockInternalImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "pipelineproof" or fullname.startswith("pipelineproof."):
            raise ImportError("internal verifier modules are unavailable")
        return None


def _load_module(candidate: Path):
    manifest = json.loads((candidate / "manifest.json").read_text(encoding="utf-8"))
    sys.path.insert(0, str(candidate / "src"))
    relative = manifest["module"].replace(".", "/") + ".py"
    path = candidate / "src" / relative
    spec = importlib.util.spec_from_file_location("candidate_pipeline", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("candidate module unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    candidate = Path(sys.argv[1]).resolve()
    request = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    output = Path(sys.argv[3])
    sys.meta_path.insert(0, _BlockInternalImports())
    module = _load_module(candidate)
    states = {}
    results = {}
    with tempfile.TemporaryDirectory(prefix="pipelineproof-worker-") as directory:
        temp = Path(directory)
        for operation in request["operations"]:
            operation_id = operation["id"]
            kind = operation["op"]
            if kind == "train":
                state = module.train(operation["train"], operation.get("eval"))
                states[operation_id] = state
                results[operation_id] = state
            elif kind == "roundtrip":
                path = temp / f"{operation_id}.json"
                module.save_state(states[operation["state"]], path)
                state = module.load_state(path)
                states[operation_id] = state
                results[operation_id] = state
            elif kind == "predict":
                results[operation_id] = module.predict(
                    states[operation["state"]], operation["rows"]
                )
            elif kind == "evaluate":
                results[operation_id] = module.evaluate(
                    states[operation["state"]], operation["train"], operation["eval"]
                )
            elif kind == "split":
                results[operation_id] = module.split(
                    operation["rows"], operation.get("ratio", 0.75)
                )
            elif kind == "features":
                results[operation_id] = module.build_features(operation["rows"])
            else:
                raise RuntimeError(f"unknown operation: {kind}")
    output.write_text(json.dumps(results, allow_nan=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
