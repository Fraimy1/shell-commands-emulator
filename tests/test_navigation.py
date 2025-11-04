import pytest
from src.commands.navigation import Cd
from src.core.errors import ExecutionError
from .conftest import pc
import src.commands.navigation as nav_mod

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
