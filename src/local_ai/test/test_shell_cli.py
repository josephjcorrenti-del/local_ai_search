def test_shell_routes_explicit_command(monkeypatch):
    from local_ai import cli
    from local_ai import shell

    called = {}

    def fake_handler(args):
        called["command"] = args.command
        called["workspace"] = args.workspace
        called["session"] = args.session

    handlers = dict(cli.COMMAND_HANDLERS)
    handlers["workspace-add-session"] = fake_handler

    shell.shell_line_run(
        "workspace-add-session test-ws default",
        {"session": "default", "model": "test-model"},
        parser_build=cli.parser_build,
        command_handlers=handlers,
        chat_run=lambda *a, **k: None,
    )

    assert called["command"] == "workspace-add-session"
    assert called["workspace"] == "test-ws"
    assert called["session"] == "default"
