from pipelineproof.catalog import get_task
from pipelineproof.templates import write_task
from pipelineproof.verifier import verify_spec


def test_vertical_slice_smoke(tmp_path):
    spec = get_task("feature-schema-a")
    broken = write_task(spec, tmp_path / "broken", "broken")
    correct = write_task(spec, tmp_path / "correct", "canonical")
    assert not verify_spec(spec, broken, spec.seed + 9000).passed
    assert verify_spec(spec, correct, spec.seed + 9000).passed
