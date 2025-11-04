import pytest
from pathlib import Path
from src.commands.listing import Ls, Cat
from src.core.errors import ExecutionError
from .conftest import pc, strip_ansi

def test_ls_names(tmp_path, ctx, capsys):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    Ls().execute(pc("ls"), ctx)
    out = capsys.readouterr().out
    assert "a.txt" in out and "b.txt" in out

def test_ls_long(tmp_path, ctx, capsys):
    (tmp_path / "f.txt").write_text("x")
    Ls().execute(pc("ls", flags={"l"}), ctx)
    out = capsys.readouterr().out
    assert "f.txt" in out and ("Perms" in out or "Modified" in out)

def test_ls_no_such_dir(ctx):
    with pytest.raises(ExecutionError):
        Ls().execute(pc("ls", pos=["nope"]), ctx)

def test_cat_file(tmp_path, ctx, capsys):
    p = tmp_path / "note.txt"
    p.write_text("hello\nworld")
    Cat().execute(pc("cat", pos=[str(p)]), ctx)
    out = capsys.readouterr().out
    assert "hello" in out and "world" in out

def test_cat_dir_raises(tmp_path, ctx):
    d = tmp_path / "dir"
    d.mkdir()
    with pytest.raises(ExecutionError):
        Cat().execute(pc("cat", pos=[str(d)]), ctx)

def test_cat_missing_raises(ctx):
    with pytest.raises(ExecutionError):
        Cat().execute(pc("cat", pos=["missing.txt"]), ctx)
