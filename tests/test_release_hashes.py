from pipelineproof.soundness import _hash_files, _stable_payload


def test_release_hashes_ignore_checkout_artifacts(tmp_path):
    included = tmp_path / "src" / "module.py"
    included.parent.mkdir()
    included.write_text("value = 1\n", encoding="utf-8")

    ignored = [
        tmp_path / ".git" / "HEAD",
        tmp_path / ".github" / "workflows" / "ci.yml",
        tmp_path / ".pytest_cache" / "state",
        tmp_path / "src" / "package.egg-info" / "PKG-INFO",
        tmp_path / "results" / "public" / "summary.json",
    ]
    for path in ignored:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("unstable\n", encoding="utf-8")

    hashes = _hash_files(tmp_path)
    assert set(hashes) == {"src/module.py"}


def test_evidence_errors_use_stable_exception_summary():
    payload = {
        "details": {
            "execution_error": (
                "Traceback (most recent call last):\n"
                '  File "/tmp/random/task.py", line 1\n'
                "ValueError: invalid output\n"
            )
        },
        "quality": {
            "error": (
                "Traceback (most recent call last):\n"
                '  File "/home/runner/project.py", line 2\n'
                "SyntaxError: invalid syntax\n"
            )
        },
    }

    stable = _stable_payload(payload)
    assert stable["details"]["execution_error"] == "ValueError: invalid output"
    assert stable["quality"]["error"] == "SyntaxError: invalid syntax"
