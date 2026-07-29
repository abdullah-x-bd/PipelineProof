from pipelineproof.catalog import get_task
from pipelineproof.templates import write_task
from pipelineproof.verifier import verify_spec


def test_protected_edit_is_detected(tmp_path):
    spec = get_task("feature-schema-a")
    candidate = write_task(spec, tmp_path / "candidate", "correct_protected_edit")
    result = verify_spec(spec, candidate, spec.seed + 30000)
    assert not result.passed
    assert not result.checks["protected"]
    assert result.checks["functional"]
    assert result.checks["causal"]


def test_extra_file_outside_src_is_detected(tmp_path):
    spec = get_task("feature-schema-a")
    candidate = write_task(spec, tmp_path / "candidate", "canonical")
    (candidate / "answers.json").write_text("{}")
    result = verify_spec(spec, candidate, spec.seed + 30001)
    assert not result.checks["protected"]
