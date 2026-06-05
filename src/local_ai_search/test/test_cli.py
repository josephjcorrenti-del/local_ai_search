from local_ai_search.cli import main


def test_status_command(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["local-ai-search", "status"])

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "local_ai_search status" in output
    assert "data_root:" in output
    assert "evidence_dir:" in output


def test_config_show_command(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["local-ai-search", "config-show"])

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "local_ai_search config" in output
    assert "search_provider: local_search" in output
    assert "- local_search" in output
    assert "- duckduckgo" in output


def test_doctor_command(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["local-ai-search", "doctor"])

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "local_ai_search doctor" in output
    assert "data_root writable" in output
    assert "config loaded" in output
    assert "search_provider valid: local_search" in output
    assert "doctor passed" in output
