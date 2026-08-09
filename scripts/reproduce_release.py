from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from pipelineproof import __version__
from pipelineproof.evidence import validate_evidence_bundle, write_evidence_manifest
from pipelineproof.soundness import reproduce


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/reproduced") / f"v{__version__}",
    )
    parser.add_argument("--seeds", type=int, default=4)
    return parser


def _docker_image_id(image: str) -> str:
    completed = subprocess.run(
        ["docker", "image", "inspect", image, "--format", "{{.Id}}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def main() -> int:
    args = _parser().parse_args()
    image = f"pipelineproof-task:{__version__}"
    subprocess.run(
        ["docker", "build", "-f", "docker/task.Dockerfile", "-t", image, "."],
        check=True,
    )
    reproduce(args.output, "docker", args.seeds)

    environment_path = args.output / "environment.json"
    environment = json.loads(environment_path.read_text(encoding="utf-8"))
    environment["docker_image_id"] = _docker_image_id(image)
    environment_path.write_text(
        json.dumps(environment, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_evidence_manifest(args.output)
    validation = validate_evidence_bundle(args.output)
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0 if validation["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
