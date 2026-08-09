from __future__ import annotations

import json
import tomllib
from pathlib import Path

from pipelineproof import __version__
from pipelineproof.evidence import validate_evidence_bundle

REQUIRED_RELEASE_FILES = (
    "README.md",
    "CHANGELOG.md",
    "CITATION.cff",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/BENCHMARK_CARD.md",
    "docs/TASK_TAXONOMY.md",
    "docs/VERIFIER_SPEC.md",
    "docs/REWARD_SPEC.md",
    "docs/THREAT_MODEL.md",
    "docs/MODEL_EVALUATION.md",
    "docs/RELATED_WORK.md",
    "docs/RELEASE_PROCESS.md",
    "schemas/evidence-summary.schema.json",
    "schemas/model-rollout.schema.json",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    missing = [path for path in REQUIRED_RELEASE_FILES if not (root / path).is_file()]
    if missing:
        errors.append(f"missing release files: {', '.join(missing)}")

    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    if "version" in pyproject["project"]:
        errors.append("pyproject version must come from the centralized dynamic version")
    dynamic = set(pyproject["project"].get("dynamic", []))
    if "version" not in dynamic:
        errors.append("pyproject does not declare a dynamic version")
    if __version__ != "0.4.0":
        errors.append(f"unexpected runtime version: {__version__}")

    citation = (root / "CITATION.cff").read_text(encoding="utf-8") if (root / "CITATION.cff").is_file() else ""
    if 'cff-version: "1.2.0"' not in citation:
        errors.append("CITATION.cff is not pinned to CFF 1.2.0")
    if 'version: "0.4.0"' not in citation:
        errors.append("CITATION.cff version does not match v0.4.0")

    evidence_root = root / "results" / "public" / "v0.4.0"
    if evidence_root.is_dir():
        evidence = validate_evidence_bundle(evidence_root)
        if not evidence["valid"]:
            errors.extend(f"evidence: {error}" for error in evidence["errors"])
    else:
        errors.append("committed v0.4.0 evidence directory is missing")
        evidence = {"valid": False}

    payload = {
        "valid": not errors,
        "version": __version__,
        "required_release_files": len(REQUIRED_RELEASE_FILES),
        "evidence_valid": evidence.get("valid", False),
        "errors": errors,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
