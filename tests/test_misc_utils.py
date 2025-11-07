import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

import src.utils.misc_utils as misc_utils
from src.core.models import HistoryEntry
from src.core.services import Context
from .conftest import pc


def _sample_entry(tmp_path: Path, **overrides) -> HistoryEntry:
    base = {
        "id": 123,
        "raw": "ls -l",
        "name": "ls",
        "flags": {"l"},
        "positionals": [str(tmp_path / "dir")],
        "cwd": tmp_path,
        "timestamp": datetime.now(UTC).isoformat(),
        "meta": {"note": "test"},
    }
    base.update(overrides)
    return HistoryEntry(**base)


def test_has_flag(tmp_path):
    cmd = pc("ls", flags={"l"})
    assert misc_utils.has_flag(cmd, "l")
    assert not misc_utils.has_flag(cmd, "a", "recursive")


def test_entry_to_dict_and_back(tmp_path):
    entry = _sample_entry(tmp_path)
    data = misc_utils.entry_to_dict(entry)
    restored = misc_utils.dict_to_entry(data)

    assert restored.id == entry.id
    assert restored.name == entry.name
    assert restored.flags == entry.flags
    assert restored.positionals == entry.positionals
    assert restored.cwd == entry.cwd
    assert restored.meta == entry.meta


def test_get_history_missing_file(monkeypatch, tmp_path):
    history_path = tmp_path / "history.json"
    monkeypatch.setattr(misc_utils, "HISTORY_FILE", history_path)
    assert misc_utils.get_history() == []


def test_get_history_bad_json(monkeypatch, tmp_path):
    history_path = tmp_path / "history.json"
    history_path.write_text("not-json")
    monkeypatch.setattr(misc_utils, "HISTORY_FILE", history_path)
    assert misc_utils.get_history() == []


def test_append_history_updates_context_and_file(monkeypatch, tmp_path):
    history_path = tmp_path / "history.json"
    history_path.write_text("[]")
    monkeypatch.setattr(misc_utils, "HISTORY_FILE", history_path)

    ctx = Context()
    ctx.history = []
    entry = _sample_entry(tmp_path)

    misc_utils.append_history(ctx, entry)

    assert ctx.history[-1] == entry

    saved = json.loads(history_path.read_text())
    assert saved and saved[-1]["name"] == entry.name
    assert saved[-1]["id"] == entry.id


def test_append_history_skips_file_when_disabled(monkeypatch, tmp_path):
    history_path = tmp_path / "history.json"
    history_path.write_text("[]")
    monkeypatch.setattr(misc_utils, "HISTORY_FILE", history_path)

    ctx = Context()
    ctx.history = []
    entry = _sample_entry(tmp_path, id=999)

    misc_utils.append_history(ctx, entry, append_to_file=False)

    assert ctx.history[-1].id == 999
    assert json.loads(history_path.read_text()) == []


def test_remove_entry_from_file(monkeypatch, tmp_path):
    history_path = tmp_path / "history.json"
    history_path.write_text(json.dumps([
        {"id": 1, "name": "ls", "raw": "ls", "flags": [], "positionals": [], "cwd": str(tmp_path), "timestamp": "t", "meta": {}},
        {"id": 2, "name": "cat", "raw": "cat f", "flags": [], "positionals": ["f"], "cwd": str(tmp_path), "timestamp": "t", "meta": {}},
    ]))
    monkeypatch.setattr(misc_utils, "HISTORY_FILE", history_path)

    misc_utils.remove_entry_from_file(1)

    data = json.loads(history_path.read_text())
    assert len(data) == 1 and data[0]["id"] == 2


def test_update_history_from_file(monkeypatch, tmp_path):
    history_path = tmp_path / "history.json"
    history_path.write_text(json.dumps([
        {"id": 7, "name": "ls", "raw": "ls", "flags": ["l"], "positionals": [], "cwd": str(tmp_path), "timestamp": "t", "meta": {}}
    ]))
    monkeypatch.setattr(misc_utils, "HISTORY_FILE", history_path)

    ctx = Context()
    ctx.history = []

    misc_utils.update_history_from_file(ctx)

    assert len(ctx.history) == 1
    assert ctx.history[0].id == 7
    assert isinstance(ctx.history[0].cwd, Path)


def test_cmd_from_history_entry(tmp_path):
    entry = _sample_entry(tmp_path, positionals=["file.txt"], flags={"r"})
    cmd = misc_utils.cmd_from_history_entry(entry)

    assert cmd.name == entry.name
    assert cmd.flags == entry.flags
    assert cmd.positionals == entry.positionals
    assert cmd.meta == entry.meta


def test_setup_creates_history_file(monkeypatch, tmp_path):
    history_path = tmp_path / "history.json"
    monkeypatch.setattr(misc_utils, "HISTORY_FILE", history_path)
    assert not history_path.exists()

    misc_utils.setup()

    assert history_path.exists()
    assert history_path.read_text() == ""

