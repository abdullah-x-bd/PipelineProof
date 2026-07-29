import json

from pipelineproof.catalog import get_task
from pipelineproof.templates import task_files, write_task


def test_public_manifest_excludes_oracle_fields(tmp_path):
    spec = get_task("feature-schema-a")
    write_task(spec, tmp_path / spec.task_id)
    manifest = json.loads((tmp_path / spec.task_id / "manifest.json").read_text())
    assert "coefficients" not in manifest
    assert "intercept" not in manifest
    assert "seed" not in manifest


def test_task_files_are_reproducible():
    spec = get_task("serialization-a")
    assert task_files(spec, "broken") == task_files(spec, "broken")
