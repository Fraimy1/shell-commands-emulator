import re
import pytest

from pathlib import Path
from datetime import datetime

import src.commands.files as files_mod
import src.commands.navigation as nav_mod
from src.commands.files import Ls, Cp, Cat, Mv, Rm, Zip, Unzip, Tar, Untar, Grep, History
from src.commands.navigation import Cd
from src.core.services import Context
from src.core.models import ParsedCommand
from src.core.errors import ExecutionError


def pc(name, flags=None, pos=None, raw=""):
    return ParsedCommand(
        name=name,
        flags=set() if flags is None else set(flags),
        positionals=[] if pos is None else list(pos),
        raw=raw,
    )


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    c = Context()
    c.cwd = tmp_path
    c.history = []
    trash = tmp_path / ".trash"
    trash.mkdir(exist_ok=True)
    monkeypatch.setattr(files_mod, "TRASH_DIR", trash, raising=False)
    return c


def strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def test_ls_names(tmp_path, ctx, capsys):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    Ls().execute(pc("ls"), ctx)
    out = capsys.readouterr().out
    assert "a.txt" in out
    assert "b.txt" in out


def test_ls_long(tmp_path, ctx, capsys):
    (tmp_path / "f.txt").write_text("x")
    Ls().execute(pc("ls", flags={"l"}), ctx)
    out = capsys.readouterr().out
    assert "f.txt" in out
    assert "Perms" in out or "Modified" in out


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


def test_cp_file(tmp_path, ctx):
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("x")
    Cp().execute(pc("cp", pos=[str(src), str(dst)]), ctx)
    assert dst.read_text() == "x"


def test_cp_dir_requires_recursive(tmp_path, ctx):
    src = tmp_path / "d"
    src.mkdir()
    (src / "f.txt").write_text("1")
    dst = tmp_path / "d_copy"
    with pytest.raises(ExecutionError):
        Cp().execute(pc("cp", pos=[str(src), str(dst)]), ctx)


def test_cp_dir_recursive_ok(tmp_path, ctx):
    src = tmp_path / "d"
    src.mkdir()
    (src / "f.txt").write_text("1")
    dst = tmp_path / "d_copy"
    Cp().execute(pc("cp", flags={"r"}, pos=[str(src), str(dst)]), ctx)
    assert (dst / "f.txt").read_text() == "1"


def test_mv_file_into_dir(tmp_path, ctx):
    f = tmp_path / "x.txt"
    f.write_text("z")
    target_dir = tmp_path / "dst"
    target_dir.mkdir()
    Mv().execute(pc("mv", pos=[str(f), str(target_dir)]), ctx)
    assert (target_dir / "x.txt").read_text() == "z"
    assert not f.exists()


def test_mv_dir_requires_recursive(tmp_path, ctx):
    src = tmp_path / "folder"
    src.mkdir()
    (src / "a").write_text("1")
    dst = tmp_path / "folder2"
    with pytest.raises(ExecutionError):
        Mv().execute(pc("mv", pos=[str(src), str(dst)]), ctx)


def test_rm_cancel(tmp_path, ctx, monkeypatch):
    f = tmp_path / "t.txt"
    f.write_text("x")
    monkeypatch.setattr("builtins.input", lambda _: "n")
    Rm().execute(pc("rm", pos=[str(f)]), ctx)
    assert f.exists()


def test_rm_to_trash(tmp_path, ctx, monkeypatch):
    f = tmp_path / "t2.txt"
    f.write_text("x")
    monkeypatch.setattr("builtins.input", lambda _: "y")
    Rm().execute(pc("rm", pos=[str(f)]), ctx)
    trash = files_mod.TRASH_DIR
    names = [p.name for p in trash.iterdir()]
    assert any(n.startswith("t2.txt_") for n in names)
    assert not f.exists()


def test_zip_unzip(tmp_path, ctx, capsys):
    folder = tmp_path / "srcdir"
    folder.mkdir()
    (folder / "a.txt").write_text("q")
    dest = tmp_path / "arch.zip"
    Zip().execute(pc("zip", pos=[str(folder), str(dest)]), ctx)
    assert dest.exists()
    Unzip().execute(pc("unzip", pos=[str(dest)]), ctx)
    out_dir = ctx.cwd / "arch"
    assert (out_dir / "a.txt").read_text() == "q"


def test_tar_untar(tmp_path, ctx):
    folder = tmp_path / "tardir"
    folder.mkdir()
    (folder / "b.txt").write_text("w")
    dest = tmp_path / "pack.tar"
    Tar().execute(pc("tar", pos=[str(folder), str(dest)]), ctx)
    assert dest.exists()
    Untar().execute(pc("untar", pos=[str(dest)]), ctx)
    assert (ctx.cwd / "tardir" / "b.txt").read_text() == "w"


def test_grep_file(tmp_path, ctx, capsys):
    p = tmp_path / "g.txt"
    p.write_text("hello\nx\ny\nhello again\n")
    Grep().execute(pc("grep", pos=["hello", str(p)]), ctx)
    out = strip_ansi(capsys.readouterr().out)
    assert "g.txt:1:hello" in out
    assert "g.txt:4:hello again" in out


def test_grep_dir_requires_recursive(tmp_path, ctx):
    d = tmp_path / "gg"
    d.mkdir()
    (d / "f.txt").write_text("hello")
    with pytest.raises(ExecutionError):
        Grep().execute(pc("grep", pos=["hello", str(d)]), ctx)


def test_history_display(ctx, capsys, monkeypatch):
    now = datetime.now().isoformat()
    monkeypatch.setattr(
        files_mod,
        "get_history",
        lambda: [{"raw": "ls -l", "timestamp": now}],
        raising=False,
    )
    History().execute(pc("history"), ctx)
    out = strip_ansi(capsys.readouterr().out)
    assert "1:" in out and "ls -l" in out


def test_cd_changes_dir(tmp_path, ctx):
    new = tmp_path / "sub"
    new.mkdir()
    Cd().execute(pc("cd", pos=[str(new)]), ctx)
    assert ctx.cwd == new


def test_cd_home(tmp_path, ctx, monkeypatch):
    monkeypatch.setattr(nav_mod, "HOME_DIR", tmp_path, raising=False)
    Cd().execute(pc("cd", pos=["~"]), ctx)
    assert ctx.cwd == tmp_path


def test_cd_not_dir(tmp_path, ctx):
    p = tmp_path / "f.txt"
    p.write_text("x")
    with pytest.raises(ExecutionError):
        Cd().execute(pc("cd", pos=[str(p)]), ctx)

#TODO: Add coverage for misc_utils update_history_from_file, get_history (i'm so fcking tired) add undo