from pathlib import Path

from pipelineproof import load_environment


def test_load_environment_exposes_public_contracts() -> None:
    spec = load_environment(Path("example-tasks"))

    assert spec.name == "pipelineproof"
    assert spec.version == "0.1.0"
    assert spec.task_root == Path("example-tasks")
    assert spec.integrity_contracts == (
        "training-data-provenance",
        "evaluation-validity",
        "train-serving-equivalence",
    )


def test_reference_material_is_protected() -> None:
    spec = load_environment()

    assert "hidden_assets/**" in spec.protected_globs
    assert "oracle/**" in spec.protected_globs
    assert "tests/**" in spec.protected_globs
