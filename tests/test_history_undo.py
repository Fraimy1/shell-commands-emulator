from datetime import datetime
from src.commands.history import History, Undo
from src.commands.filesystem import Cp, Rm, Mv
from src.core.models import HistoryEntry
from .conftest import pc, strip_ansi

def _mk_entry(cmd, ctx, meta=None, eid=1):
    if meta:
        cmd.meta.update(meta)
    return HistoryEntry(
        id=eid,
        raw=cmd.raw,
        name=cmd.name,
        flags=set(cmd.flags),
        positionals=list(cmd.positionals),
        cwd=ctx.cwd,
        timestamp=datetime.now().isoformat(),
        meta=dict(cmd.meta),
    )

def test_history_display(ctx, capsys, monkeypatch):
    now = datetime.now().isoformat()
    import src.commands.history as history_mod
    monkeypatch.setattr(history_mod, "get_history", lambda: [{"raw": "ls -l", "timestamp": now}], raising=False)
    History().execute(pc("history"), ctx)
    out = strip_ansi(capsys.readouterr().out)
    assert "1:" in out and "ls -l" in out

def test_undo_cp(tmp_path, ctx):
    src = tmp_path / "s.txt"
    dst = tmp_path / "d.txt"
    src.write_text("x")
    cmd = pc("cp", pos=[str(src), str(dst)])
    Cp().execute(cmd, ctx)
    ctx.history.append(_mk_entry(cmd, ctx, eid=101))
    assert dst.exists()
    Undo().execute(pc("undo"), ctx)
    assert not dst.exists()

def test_undo_rm(tmp_path, ctx):
    f = tmp_path / "rmme.txt"
    f.write_text("1")
    cmd = pc("rm", pos=[str(f)], meta={"non_interactive": True})
    Rm().execute(cmd, ctx)
    assert any(p.name.endswith("_rmme.txt") for p in ctx.trash_dir.iterdir())
    ctx.history.append(_mk_entry(cmd, ctx, eid=202))
    Undo().execute(pc("undo"), ctx)
    assert f.exists()

def test_undo_mv(tmp_path, ctx):
    f = tmp_path / "m.txt"
    f.write_text("m")
    d = tmp_path / "dst"
    d.mkdir()
    cmd = pc("mv", pos=[str(f), str(d)])
    Mv().execute(cmd, ctx)
    moved = d / "m.txt"
    assert moved.exists() and not f.exists()
    ctx.history.append(_mk_entry(cmd, ctx, eid=303))
    Undo().execute(pc("undo"), ctx)
    assert f.exists() and not moved.exists()
