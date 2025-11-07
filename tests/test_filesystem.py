import re
import pytest
from src.commands.filesystem import Cp, Mv, Rm
from src.core.errors import ExecutionError
from .conftest import pc

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
    names = [p.name for p in ctx.trash_dir.iterdir()]
    assert any(re.match(r"\d+_t2\.txt$", n) for n in names)
    assert not f.exists()
