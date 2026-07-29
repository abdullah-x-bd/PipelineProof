import pytest

from pipelineproof.soundness import reward_ladder


pytestmark = pytest.mark.slow
def test_reward_ladder_is_strictly_monotonic():
    report = reward_ladder()
    assert report["strictly_monotonic"], report
