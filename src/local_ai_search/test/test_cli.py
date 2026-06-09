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

def test_inspect_evidence_json_command(capsys, monkeypatch):
    from local_ai_search import cli

    evidence = {
        "retrieval_version": 1,
        "artifact_type": "web_search_results",
        "query": "test query",
        "provider": "local_search",
        "fetched_at": "2026-06-07T00:00:00+00:00",
        "results": [],
    }

    def fake_load_evidence(path, *, limit, max_chars):
        assert str(path) == "artifact.json"
        assert limit == 5
        assert max_chars == 4000
        return evidence

    monkeypatch.setattr(cli, "load_evidence_from_local_search", fake_load_evidence)

    parser = cli.build_parser()
    args = parser.parse_args(["inspect-evidence", "artifact.json", "--json"])

    assert args.func(args) == 0

    output = capsys.readouterr().out
    assert '"retrieval_version": 1' in output
    assert '"provider": "local_search"' in output
    assert "[*] local_ai_search evidence" not in output


def test_status_self_skips_ecosystem(capsys, monkeypatch):
    from local_ai_search import cli

    calls = []

    def fake_external(command):
        calls.append(command)
        return 0

    monkeypatch.setattr(cli, "_external_command_run", fake_external)
    monkeypatch.setattr("sys.argv", ["local-ai-search", "status", "--self"])

    assert cli.main() == 0
    assert calls == []


def test_status_default_checks_ecosystem(capsys, monkeypatch):
    from local_ai_search import cli

    calls = []

    def fake_external(command):
        calls.append(command)
        return 0

    monkeypatch.setattr(cli, "_external_command_run", fake_external)
    monkeypatch.setattr("sys.argv", ["local-ai-search", "status"])

    assert cli.main() == 0
    assert calls == [
        ["local-search", "status"],
        ["local-ai", "status"],
    ]


def test_doctor_self_skips_ecosystem(capsys, monkeypatch):
    from local_ai_search import cli

    calls = []

    def fake_external(command):
        calls.append(command)
        return 0

    monkeypatch.setattr(cli, "_external_command_run", fake_external)
    monkeypatch.setattr("sys.argv", ["local-ai-search", "doctor", "--self"])

    assert cli.main() == 0
    assert calls == []


def test_doctor_default_checks_ecosystem(capsys, monkeypatch):
    from local_ai_search import cli

    calls = []

    def fake_external(command):
        calls.append(command)
        return 0

    monkeypatch.setattr(cli, "_external_command_run", fake_external)
    monkeypatch.setattr("sys.argv", ["local-ai-search", "doctor"])

    assert cli.main() == 0
    assert calls == [
        ["local-search", "doctor"],
        ["local-ai", "doctor"],
    ]

import pytest
from local_ai_search import cli


@pytest.mark.parametrize(
    "argv, expected",
    [
        (["local-ai-search", "--help"], "status"),
        (["local-ai-search", "status", "--help"], "--self"),
        (["local-ai-search", "doctor", "--help"], "--self"),
        (["local-ai-search", "config-show", "--help"], "config-show"),
        (["local-ai-search", "inspect-evidence", "--help"], "--json"),
    ],
)
def test_help_commands(capsys, monkeypatch, argv, expected):
    monkeypatch.setattr("sys.argv", argv)

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert expected in output