import json

from pipelineproof.cli import main


def test_doctor_reports_ok(monkeypatch, capsys) -> None:
    monkeypatch.setattr("sys.argv", ["pipelineproof", "doctor"])

    exit_code = main()
    report = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert report["package"] == "pipelineproof"
    assert report["status"] == "ok"
    assert len(report["integrity_contracts"]) == 3
