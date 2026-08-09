from __future__ import annotations

import json
import shutil
from pathlib import Path

from pipelineproof.evidence import validate_evidence_bundle, write_evidence_manifest


def _copy_committed_evidence(tmp_path: Path) -> Path:
    source = Path("results/public/v0.4.0")
    target = tmp_path / "evidence"
    shutil.copytree(source, target)
    write_evidence_manifest(target)
    return target


def test_committed_evidence_satisfies_release_invariants(tmp_path):
    target = _copy_committed_evidence(tmp_path)
    result = validate_evidence_bundle(target)
    assert result["valid"], result


def test_validator_rejects_false_accept_claim(tmp_path):
    target = _copy_committed_evidence(tmp_path)
    path = target / "summary.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["false_accepts"] = 1
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_evidence_manifest(target)
    result = validate_evidence_bundle(target)
    assert not result["valid"]
    assert "false accepts are non-zero" in result["errors"]


def test_validator_rejects_tampered_manifest(tmp_path):
    target = _copy_committed_evidence(tmp_path)
    summary = target / "summary.md"
    summary.write_text(summary.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
    result = validate_evidence_bundle(target)
    assert not result["valid"]
    assert any("manifest digest mismatch" in error for error in result["errors"])
