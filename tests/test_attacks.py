import pytest

from pipelineproof.catalog import get_task
from pipelineproof.soundness import ATTACKS
from pipelineproof.templates import write_task
from pipelineproof.verifier import verify_spec

pytestmark = pytest.mark.slow


@pytest.mark.parametrize("style", ATTACKS)
def test_attack_is_rejected(style, tmp_path):
    spec = get_task("feature-schema-a")
    candidate = write_task(spec, tmp_path / style, style)
    result = verify_spec(spec, candidate, spec.seed + 20000)
    assert result.checks["interface"], result.to_dict()
    assert result.checks["public_tests"], result.to_dict()
    assert not result.passed, result.to_dict()
