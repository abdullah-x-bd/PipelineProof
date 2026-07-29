import pytest

from pipelineproof.stats import wilson_interval


def test_wilson_zero_failures_has_nonzero_upper_bound():
    lower, upper = wilson_interval(0, 32)
    assert lower == pytest.approx(0.0, abs=1e-12)
    assert 0.09 < upper < 0.12


def test_wilson_rejects_invalid_counts():
    with pytest.raises(ValueError):
        wilson_interval(2, 1)
