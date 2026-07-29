from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipelineproof.catalog import load_private_spec
from pipelineproof.verifier import verify_spec


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--mode", choices=["local", "docker"], default="docker")
    args = parser.parse_args()
    manifest = json.loads((args.bundle / "manifest.json").read_text())
    rows = []
    for item in manifest["tasks"]:
        spec = load_private_spec(args.bundle / item["spec"])
        result = verify_spec(spec, args.bundle / item["task"], mode=args.mode)
        rows.append(result.to_dict())
    print(json.dumps(rows, indent=2, sort_keys=True))
    return 0 if all(not row["passed"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
