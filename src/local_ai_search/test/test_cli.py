from local_ai_search.cli import main


def test_status_command(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["local-ai-search", "status", "--self"])

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
    monkeypatch.setattr("sys.argv", ["local-ai-search", "doctor", "--self"])

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
    from local_ai_search.adapters import local_ai, local_search

    calls = []

    def fake_search_status():
        calls.append("local-search-status")
        return 0

    def fake_ai_status():
        calls.append("local-ai-status")
        return 0

    monkeypatch.setattr(local_search, "run_status", fake_search_status)
    monkeypatch.setattr(local_ai, "run_status", fake_ai_status)
    monkeypatch.setattr("sys.argv", ["local-ai-search", "status", "--self"])

    assert cli.main() == 0
    assert calls == []


def test_status_default_checks_ecosystem(capsys, monkeypatch):
    from local_ai_search import cli
    from local_ai_search.adapters import local_ai, local_search

    calls = []

    def fake_search_status():
        calls.append("local-search-status")
        return 0

    def fake_ai_status():
        calls.append("local-ai-status")
        return 0

    monkeypatch.setattr(local_search, "run_status", fake_search_status)
    monkeypatch.setattr(local_ai, "run_status", fake_ai_status)
    monkeypatch.setattr("sys.argv", ["local-ai-search", "status"])

    assert cli.main() == 0

    assert calls == [
        "local-search-status",
        "local-ai-status",
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
    from local_ai_search.adapters import local_ai, local_search

    calls = []

    def fake_search_doctor():
        calls.append("local-search-doctor")
        return 0

    def fake_ai_doctor():
        calls.append("local-ai-doctor")
        return 0

    monkeypatch.setattr(local_search, "run_doctor", fake_search_doctor)
    monkeypatch.setattr(local_ai, "run_doctor", fake_ai_doctor)
    monkeypatch.setattr("sys.argv", ["local-ai-search", "doctor"])

    assert cli.main() == 0

    assert calls == [
        "local-search-doctor",
        "local-ai-doctor",
    ]

import pytest
from local_ai_search import cli


def test_top_level_help(capsys, monkeypatch):
    from local_ai_search import cli

    monkeypatch.setattr("sys.argv", ["local-ai-search", "--help"])

    assert cli.main() == 0

    output = capsys.readouterr().out
    assert "status" in output


@pytest.mark.parametrize(
    "argv, expected",
    [
        (["local-ai-search", "status", "--help"], "--self"),
        (["local-ai-search", "doctor", "--help"], "--self"),
        (["local-ai-search", "config-show", "--help"], "config-show"),
        (["local-ai-search", "inspect-evidence", "--help"], "--json"),
    ],
)


def test_subcommand_help(capsys, monkeypatch, argv, expected):
    from local_ai_search import cli

    monkeypatch.setattr("sys.argv", argv)

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 0

    output = capsys.readouterr().out
    assert expected in output

def test_top_level_query_ai_only(monkeypatch, capsys):
    from local_ai_search import cli
    from local_ai_search.adapters import local_ai

    calls = []

    def fake_ask(prompt):
        calls.append(prompt)
        return "answer text"

    monkeypatch.setattr(local_ai, "ask", fake_ask)
    monkeypatch.setattr("sys.argv", ["local-ai-search", "what is sqlite?", "--ai-only"])

    assert cli.main() == 0
    assert calls == ["what is sqlite?"]
    assert "answer text" in capsys.readouterr().out


def test_top_level_query_web_only(monkeypatch):
    from local_ai_search import cli
    from local_ai_search.adapters import local_search

    calls = []

    def fake_search(query):
        calls.append(query)
        return 0

    monkeypatch.setattr(local_search, "search", fake_search)
    monkeypatch.setattr("sys.argv", ["local-ai-search", "jumping insects", "--web-only"])

    assert cli.main() == 0
    assert calls == ["jumping insects"]


def test_top_level_query_runs_search_then_pipeline(monkeypatch, capsys):
    from pathlib import Path

    from local_ai_search import cli
    from local_ai_search.adapters import local_search

    calls = []

    evidence = {
        "retrieval_version": 1,
        "artifact_type": "web_search_results",
        "query": "what is sqlite?",
        "provider": "local_search",
        "fetched_at": "2026-06-24T00:00:00+00:00",
        "results": [],
    }

    def fake_search(query):
        calls.append(("search", query))
        return 0

    def fake_latest(query):
        calls.append(("latest", query))
        return Path("/tmp/search_what_is_sqlite.json")

    def fake_load(path, *, limit, max_chars):
        calls.append(("load", str(path), limit, max_chars))
        return evidence

    def fake_run_query(query, loaded_evidence, session_name=None):
        calls.append(
            ("run_query", query, loaded_evidence, session_name)
        )
        return "answer text"

    monkeypatch.setattr(local_search, "search", fake_search)
    monkeypatch.setattr(cli, "latest_web_artifact_for_query", fake_latest)
    monkeypatch.setattr(cli, "load_evidence_from_local_search", fake_load)
    monkeypatch.setattr(cli.pipeline, "run_query", fake_run_query)
    monkeypatch.setattr("sys.argv", ["local-ai-search", "what is sqlite?"])

    assert cli.main() == 0

    assert calls == [
        ("search", "what is sqlite?"),
        ("latest", "what is sqlite?"),
        ("load", "/tmp/search_what_is_sqlite.json", 5, 4000),
        ("run_query", "what is sqlite?", evidence, None),
    ]

    assert "answer text" in capsys.readouterr().out


def test_serve_command(monkeypatch):
    from local_ai_search import cli

    calls = []

    def fake_run(app, *, host, port):
        calls.append((host, port))

    monkeypatch.setattr("uvicorn.run", fake_run)
    monkeypatch.setattr("sys.argv", ["local-ai-search", "serve"])

    assert cli.main() == 0
    assert calls == [("0.0.0.0", 8765)]


def test_top_level_session_followup_skips_retrieval(monkeypatch, capsys):
    from local_ai_search import cli
    from local_ai_search.adapters import local_search

    calls = []

    def fake_search(query):
        calls.append(("search", query))
        return 0

    def fake_run_query(query, evidence, session_name=None):
        calls.append(("run_query", query, evidence, session_name))
        return "SQLite"

    monkeypatch.setattr(local_search, "search", fake_search)
    monkeypatch.setattr(cli.pipeline, "run_query", fake_run_query)
    monkeypatch.setattr(
        "sys.argv",
        [
            "local-ai-search",
            "--session",
            "api-test",
            "what database did I just tell you I liked?",
        ],
    )

    assert cli.main() == 0

    assert calls == [
        (
            "run_query",
            "what database did I just tell you I liked?",
            {"results": []},
            "api-test",
        )
    ]

    captured = capsys.readouterr()
    assert "SQLite" in captured.out