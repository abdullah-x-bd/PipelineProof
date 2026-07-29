from pipelineproof.soundness import _hash_files


def test_release_hashes_exclude_checkout_and_build_state(tmp_path):
    included = tmp_path / "src" / "package.py"
    included.parent.mkdir(parents=True)
    included.write_text("value = 1\n", encoding="utf-8")

    excluded = [
        tmp_path / ".git" / "HEAD",
        tmp_path / ".venv" / "pyvenv.cfg",
        tmp_path / "src" / "pipelineproof.egg-info" / "PKG-INFO",
        tmp_path / "build" / "artifact.txt",
        tmp_path / "dist" / "package.whl",
        tmp_path / "results" / "public" / "summary.json",
    ]
    for path in excluded:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("excluded\n", encoding="utf-8")

    assert list(_hash_files(tmp_path)) == ["src/package.py"]
