import json

from pipelineproof.model_results import load_records, write_model_report


def _record(model, task, rollout, reward, quality, passed, failure):
    return {
        "model": model,
        "provider_route": "direct",
        "harness": "terminal-agent",
        "task_id": task,
        "rollout_id": rollout,
        "reward": reward,
        "passed": passed,
        "independent_quality": quality,
        "failure_class": failure,
    }


def test_model_report_generates_ranked_outputs(tmp_path):
    records = [
        _record("strong", "feature-schema-a", "1", 1.0, 1.0, True, "success"),
        _record("strong", "feature-schema-a", "2", 0.8, 0.9, False, "partial_repair"),
        _record("strong", "wrong-eval-a", "1", 0.9, 0.95, True, "success"),
        _record("strong", "wrong-eval-a", "2", 1.0, 1.0, True, "success"),
        _record("weak", "feature-schema-a", "1", 0.3, 0.2, False, "capability_limit"),
        _record("weak", "feature-schema-a", "2", 0.4, 0.3, False, "capability_limit"),
        _record("weak", "wrong-eval-a", "1", 0.2, 0.1, False, "capability_limit"),
        _record("weak", "wrong-eval-a", "2", 0.3, 0.2, False, "capability_limit"),
    ]
    input_path = tmp_path / "rollouts.jsonl"
    input_path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")

    output = tmp_path / "report"
    result = write_model_report(input_path, output)

    assert result["records"] == 8
    panel = json.loads((output / "model_panel.json").read_text(encoding="utf-8"))
    assert panel["cells"][0]["model"] == "strong"
    search = json.loads((output / "best_of_n.json").read_text(encoding="utf-8"))
    strong = next(curve for curve in search["curves"] if curve["model"] == "strong")
    assert [point["budget"] for point in strong["points"]] == [1, 2]
    failures = json.loads((output / "failure_breakdown.json").read_text(encoding="utf-8"))
    assert len(failures["cells"]) == 2


def test_model_records_require_complete_schema(tmp_path):
    path = tmp_path / "invalid.jsonl"
    path.write_text('{"model": "incomplete"}\n', encoding="utf-8")

    try:
        load_records(path)
    except ValueError as error:
        assert "missing fields" in str(error)
    else:
        raise AssertionError("invalid records were accepted")
