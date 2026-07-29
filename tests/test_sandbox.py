from pipelineproof.sandbox import DockerSandbox, LocalSandbox


def test_sandbox_manifests_disclose_isolation():
    local = LocalSandbox().manifest()
    docker = DockerSandbox().manifest()
    assert local["network_isolation"] is False
    assert docker["network"] == "none"
    assert docker["candidate_mount"] == "read-only"
