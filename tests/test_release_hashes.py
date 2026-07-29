from pipelineproof.soundness import _hash_files


def test_release_hashes_ignore_checkout_artifacts(tmp_path):
    included = tmp_path / "src" / "module.py"
    included.parent.mkdir()
    included.write_text("value = 1\n", encoding="utf-8")

    ignored = [
        tmp_path / ".git" / "HEAD",
        tmp_path / ".pytest_cache" / "state",
        tmp_path / "src" / "package.egg-info" / "PKG-INFO",
        tmp_path / "results" / "public" / "summary.json",
    ]
    for path in ignored:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("unstable\n", encoding="utf-8")

    hashes = _hash_files(tmp_path)
    assert set(hashes) == {"src/module.py"}
