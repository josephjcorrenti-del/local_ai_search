from local_ai_search.output import (
    ANSI_BLUE,
    ANSI_GREEN,
    ANSI_RED,
    color_enabled,
    fail_print,
    info_print,
    pass_print,
)


def test_color_enabled_by_default(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    assert color_enabled() is True


def test_color_disabled_with_no_color(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")

    assert color_enabled() is False


def test_pass_print_uses_green(capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    pass_print("ok")
    output = capsys.readouterr().out

    assert ANSI_GREEN in output
    assert "[✓] ok" in output


def test_fail_print_uses_red(capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    fail_print("bad")
    output = capsys.readouterr().out

    assert ANSI_RED in output
    assert "[x] bad" in output


def test_info_print_uses_blue(capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    info_print("note")
    output = capsys.readouterr().out

    assert ANSI_BLUE in output
    assert "[*] note" in output


def test_no_color_removes_ansi(capsys, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")

    pass_print("ok")
    output = capsys.readouterr().out

    assert output == "[✓] ok\n"
