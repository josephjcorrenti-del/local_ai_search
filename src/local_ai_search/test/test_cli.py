from local_ai_search.cli import main


def test_status_command(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["local-ai-search", "status"])

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "local_ai_search status" in output
    assert "data_root:" in output
    assert "evidence_dir:" in output
