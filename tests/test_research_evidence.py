import pytest

from pipelineproof.catalog import task_catalog
from pipelineproof.soundness import (
    ATTACK_CASES,
    VALID_CONTROLS,
    attack_matrix,
    attack_receipt,
    valid_control_receipt,
    valid_repair_matrix,
)

pytestmark = pytest.mark.slow


def test_attack_receipt_has_no_invalid_fixtures_or_false_accepts():
    receipt = attack_receipt(seed_count=1, mode="local")
    assert receipt["structural_attack_cells"] == len(ATTACK_CASES)
    assert receipt["valid_attack_trials"] == len(ATTACK_CASES)
    assert receipt["invalid_attack_trials"] == 0, receipt["invalid_attack_ids"]
    assert receipt["false_accept"]["count"] == 0, receipt["surviving_attacks"]
    assert receipt["clean_rejections"] == len(ATTACK_CASES)
    assert receipt["other_rejections"] == 0


def test_attack_matrix_is_structural_not_seed_inflated():
    receipt = {"attack_evidence": attack_receipt(seed_count=2, mode="local")}
    rows = attack_matrix(receipt)
    assert len(rows) == len(ATTACK_CASES)
    assert all(row["seed_trials"] == 2 for row in rows)
    assert all(row["valid_trials"] == 2 for row in rows)
    assert all(row["invalid_trials"] == 0 for row in rows)
    assert all(row["false_accepts"] == 0 for row in rows)
    assert all(row["clean_rejections"] == 2 for row in rows)


def test_all_eighteen_valid_repair_cells_are_accepted():
    receipt = valid_control_receipt(seed_count=1, mode="local")
    expected = len(task_catalog()) * len(VALID_CONTROLS)
    assert expected == 18
    assert receipt["structural_valid_control_cells"] == expected
    assert receipt["false_reject"]["count"] == 0, receipt["rejected_repairs"]


def test_valid_repair_matrix_preserves_solution_diversity():
    control = valid_control_receipt(seed_count=2, mode="local")
    receipt = {"valid_control_evidence": control}
    rows = valid_repair_matrix(receipt)
    assert len(rows) == 18
    assert {(row["task_id"], row["style"]) for row in rows} == {
        (spec.task_id, style)
        for spec in task_catalog()
        for style in VALID_CONTROLS
    }
    assert all(row["seed_trials"] == 2 for row in rows)
    assert all(row["all_accepted"] for row in rows)
