import re
import pytest
from src.core.services import Context
from src.core.models import ParsedCommand
import src.commands.filesystem as filesystem_mod  # for TRASH_DIR monkeypatch

def pc(name, flags=None, pos=None, raw="", meta=None):
    cmd = ParsedCommand(
        name=name,
        flags=set() if flags is None else set(flags),
        positionals=[] if pos is None else list(pos),
        raw=raw,
    )
    if meta:
        cmd.meta.update(meta)
    return cmd

@pytest.fixture
def ctx(tmp_path, monkeypatch):
    c = Context()
    c.cwd = tmp_path
    trash = tmp_path / ".trash"
    trash.mkdir(exist_ok=True)
    monkeypatch.setattr(filesystem_mod, "TRASH_DIR", trash, raising=False)
    c.trash_dir = trash
    return c

def strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)
