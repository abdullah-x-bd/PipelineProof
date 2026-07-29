import pytest

from pipelineproof.catalog import task_catalog
from pipelineproof.templates import write_task
from pipelineproof.verifier import verify_spec


pytestmark = pytest.mark.slow


@pytest.mark.parametrize("spec", task_catalog(), ids=lambda spec: spec.task_id)
def test_broken_tasks_fail_their_contract(spec, tmp_path):
    candidate = write_task(spec, tmp_path / spec.task_id, "broken")
    result = verify_spec(spec, candidate, spec.seed + 9000)
    assert not result.passed
    assert result.checks["interface"]
    assert result.checks["public_tests"]
    assert not result.checks["causal"]


@pytest.mark.parametrize("spec", task_catalog(), ids=lambda spec: spec.task_id)
@pytest.mark.parametrize("style", ["canonical", "alternative", "refactor"])
def test_valid_repairs_pass(spec, style, tmp_path):
    candidate = write_task(spec, tmp_path / f"{spec.task_id}-{style}", style)
    result = verify_spec(spec, candidate, spec.seed + 9100)
    assert result.passed, result.to_dict()
    assert result.reward.total == 1.0
