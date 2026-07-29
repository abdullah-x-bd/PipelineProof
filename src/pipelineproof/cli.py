from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pipelineproof import __version__
from pipelineproof.catalog import get_task, load_private_spec, task_catalog
from pipelineproof.generator import generate_tasks
from pipelineproof.model_results import write_model_report
from pipelineproof.quality import quality_score
from pipelineproof.sandbox import DockerSandbox, LocalSandbox
from pipelineproof.soundness import reproduce, soundness_receipt
from pipelineproof.verifier import verify_spec


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pipelineproof")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor")
    sub.add_parser("list-tasks")

    generate = sub.add_parser("generate")
    generate.add_argument("--output", type=Path, required=True)

    verify_parser = sub.add_parser("verify")
    source = verify_parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--task")
    source.add_argument("--spec", type=Path)
    verify_parser.add_argument("--candidate", type=Path, required=True)
    verify_parser.add_argument("--seed", type=int)
    verify_parser.add_argument("--mode", choices=["local", "docker"], default="local")

    quality_parser = sub.add_parser("quality")
    quality_source = quality_parser.add_mutually_exclusive_group(required=True)
    quality_source.add_argument("--task")
    quality_source.add_argument("--spec", type=Path)
    quality_parser.add_argument("--candidate", type=Path, required=True)
    quality_parser.add_argument("--seed", type=int, required=True)
    quality_parser.add_argument("--mode", choices=["local", "docker"], default="local")

    soundness = sub.add_parser("soundness-report")
    soundness.add_argument("--seeds", type=int, default=4)
    soundness.add_argument("--mode", choices=["local", "docker"], default="local")

    reproduce_parser = sub.add_parser("reproduce")
    reproduce_parser.add_argument("--output", type=Path, required=True)
    reproduce_parser.add_argument("--seeds", type=int, default=4)
    reproduce_parser.add_argument("--mode", choices=["local", "docker"], default="local")

    model_report = sub.add_parser("model-report")
    model_report.add_argument("--input", type=Path, required=True)
    model_report.add_argument("--output", type=Path, required=True)

    sub.add_parser("sandbox-manifest")
    return parser


def _spec(args):
    return load_private_spec(args.spec) if args.spec else get_task(args.task)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "doctor":
        payload = {
            "version": __version__,
            "tasks": len(task_catalog()),
            "families": len({task.family for task in task_catalog()}),
            "docker_executable": DockerSandbox().available(),
            "default_verifier_mode": "local",
        }
    elif args.command == "list-tasks":
        payload = [task.public_dict() for task in task_catalog()]
    elif args.command == "generate":
        payload = {"generated": [str(path) for path in generate_tasks(args.output)]}
    elif args.command == "verify":
        payload = verify_spec(_spec(args), args.candidate, args.seed, args.mode).to_dict()
    elif args.command == "quality":
        payload = quality_score(_spec(args), args.candidate, args.seed, args.mode)
    elif args.command == "soundness-report":
        payload = soundness_receipt(args.seeds, args.mode)
    elif args.command == "reproduce":
        payload = reproduce(args.output, args.mode, args.seeds)
    elif args.command == "model-report":
        payload = write_model_report(args.input, args.output)
    else:
        payload = {
            "local": LocalSandbox().manifest(),
            "docker": DockerSandbox().manifest(),
            "docker_executable": DockerSandbox().available(),
        }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
