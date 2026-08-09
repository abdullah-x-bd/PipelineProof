from importlib.metadata import version

from pipelineproof import __version__
from pipelineproof.sandbox import DockerSandbox


def test_package_metadata_matches_runtime_version():
    assert version("pipelineproof") == __version__ == "0.4.0"


def test_docker_image_tracks_runtime_version():
    assert DockerSandbox.image == f"pipelineproof-task:{__version__}"
