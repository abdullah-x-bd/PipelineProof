from pipelineproof import load_environment


def test_load_environment():
    environment = load_environment()
    assert len(environment.tasks) == 6
    assert len(environment.families) == 6
