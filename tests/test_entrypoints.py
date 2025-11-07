def test_main_invokes_shell(monkeypatch):
    import src.main as main_mod

    called = {"value": False}

    def fake_start():
        called["value"] = True

    monkeypatch.setattr(main_mod.shell, "start_shell", fake_start)

    main_mod.main()

    assert called["value"] is True


def test_shell_executes_command_and_exits(monkeypatch, capsys, tmp_path):
    inputs = iter(["ls", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    import src.shell as shell_mod

    monkeypatch.setattr(shell_mod, "USER_WELCOME_MESSAGE", "Welcome!", raising=False)
    monkeypatch.setattr(shell_mod, "USER_GOODBYE_MESSAGE", "Goodbye!", raising=False)
    monkeypatch.setattr(shell_mod, "update_history_from_file", lambda ctx: None)

    seen = {
        "prompts": [],
        "validated": False,
        "dispatched": False,
    }

    class DummyCmd:
        name = "ls"
        flags = set()
        positionals = []
        raw = "ls"
        meta = {}

    class EasyParser:
        def tokenize(self, expr):
            seen["prompts"].append(expr)
            return DummyCmd()

    class EasyValidator:
        def validate_cmd(self, cmd):
            seen["validated"] = True

    class EasyDispatcher:
        def dispatch_command(self, cmd, ctx):
            seen["dispatched"] = cmd.name

    monkeypatch.setattr(shell_mod, "Parser", EasyParser)
    monkeypatch.setattr(shell_mod, "Validator", EasyValidator)
    monkeypatch.setattr(shell_mod, "Dispatcher", EasyDispatcher)

    shell = shell_mod.Shell()
    shell.ctx.cwd = tmp_path

    shell.start_shell()

    out = capsys.readouterr().out

    assert "Welcome!" in out and "Goodbye!" in out
    assert seen["prompts"] == ["ls"]
    assert seen["validated"] is True
    assert seen["dispatched"] == "ls"

