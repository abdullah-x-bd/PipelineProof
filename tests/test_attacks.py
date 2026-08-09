import pytest

from pipelineproof.catalog import get_task
from pipelineproof.soundness import ATTACK_CASES, write_attack_task
from pipelineproof.verifier import verify_spec

pytestmark = pytest.mark.slow


@pytest.mark.parametrize("case", ATTACK_CASES, ids=lambda case: case.attack_id)
def test_attack_is_valid_and_rejected_by_intended_path(case, tmp_path):
    spec = get_task(case.task_id)
    candidate = write_attack_task(case, tmp_path / case.attack_id)
    result = verify_spec(spec, candidate, spec.seed + 20_000)
    payload = result.to_dict()

    assert result.checks["interface"], payload
    assert result.checks["public_tests"], payload

    if case.expected_execution_error:
        assert payload["details"].get("execution_error"), payload
        assert not result.passed, payload
        return

    assert not payload["details"].get("execution_error"), payload
    for check in case.required_checks:
        assert result.checks[check], payload
    assert not result.checks[case.intended_check], payload
    assert not result.passed, payload
