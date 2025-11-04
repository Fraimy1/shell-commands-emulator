import pytest
from src.commands.archive import Zip, Unzip, Tar, Untar
from src.core.errors import ExecutionError
from .conftest import pc

def test_zip_unzip(tmp_path, ctx):
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

def test_zip_requires_dir(tmp_path, ctx):
    f = tmp_path / "notdir.txt"
    f.write_text("x")
    dest = tmp_path / "x.zip"
    with pytest.raises(ExecutionError):
        Zip().execute(pc("zip", pos=[str(f), str(dest)]), ctx)

def test_zip_ext_required(tmp_path, ctx):
    d = tmp_path / "d"
    d.mkdir()
    dest = tmp_path / "badname"
    with pytest.raises(ExecutionError):
        Zip().execute(pc("zip", pos=[str(d), str(dest)]), ctx)
