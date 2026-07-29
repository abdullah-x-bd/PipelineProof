import pytest

from pipelineproof.catalog import task_catalog
from pipelineproof.quality import quality_score
from pipelineproof.templates import write_task

pytestmark = pytest.mark.slow


@pytest.mark.parametrize("spec", task_catalog(), ids=lambda spec: spec.task_id)
def test_independent_quality_separates_broken_and_correct(spec, tmp_path):
    broken = write_task(spec, tmp_path / f"{spec.task_id}-broken", "broken")
    correct = write_task(spec, tmp_path / f"{spec.task_id}-correct", "canonical")
    bad_score = quality_score(spec, broken, spec.seed + 100000)["score"]
    good_score = quality_score(spec, correct, spec.seed + 100000)["score"]
    assert good_score == 1.0
    assert bad_score < good_score
