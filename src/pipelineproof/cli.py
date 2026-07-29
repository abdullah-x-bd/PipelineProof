"""Command-line entry points for repository health and project orientation."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

from pipelineproof import __version__
from pipelineproof.environment import load_environment


def _doctor() -> int:
    spec = load_environment()
    report = {
        "package": spec.name,
        "version": __version__,
        "python": platform.python_version(),
        "task_root": str(spec.task_root),
        "task_root_exists": spec.task_root.exists(),
        "integrity_contracts": list(spec.integrity_contracts),
        "status": "ok",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def _show_plan() -> int:
    plan_path = Path("docs/BUILD_PLAN.md")
    if not plan_path.exists():
        print(f"Build plan not found at {plan_path}")
        return 1
    print(plan_path.read_text(encoding="utf-8"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pipelineproof")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="Print package and environment health information")
    subparsers.add_parser("show-plan", help="Print the checked-in implementation plan")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "doctor":
        return _doctor()
    if args.command == "show-plan":
        return _show_plan()
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
