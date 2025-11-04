from src.core.models import ParsedCommand, HistoryEntry
from src.core.services import Context
from src.config import HISTORY_FILE

from typing import Any
from pathlib import Path
from datetime import datetime
import json

def has_flag(cmd:ParsedCommand, *flags):
    return any(f in cmd.flags for f in flags)

def entry_to_dict(e: HistoryEntry) -> dict[str, Any]:
    return {
        "id": e.id,
        "raw": e.raw,
        "name": e.name,
        "flags": list(e.flags),
        "positionals": e.positionals,
        "cwd": str(e.cwd),
        "timestamp": e.timestamp,
        "meta": e.meta,
    }

def dict_to_entry(d: dict[str, Any]) -> HistoryEntry:
    return HistoryEntry(
        id = int(d.get("id", 0)),
        raw = d.get("raw", ""),
        name = d.get("name", ""),
        flags = set(d.get("flags", [])),
        positionals = d.get("positionals", []),
        cwd = Path(d.get("cwd", ".")),
        timestamp = d.get("timestamp", datetime.now().isoformat()),
        meta = d.get("meta", {}),
    )

def get_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    return data

def append_history(ctx:Context, entry: HistoryEntry, append_to_file:bool = True):
    ctx.history.append(entry)
    if not append_to_file:
        return

    try:
        with open(HISTORY_FILE, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            data.append(entry_to_dict(entry))
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()

    except FileNotFoundError:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([entry], f, indent=4, ensure_ascii=False)

def remove_entry_from_file(entry_id: int):
    try:
        with open(HISTORY_FILE, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

            new_data = [e for e in data if e.get("id") != entry_id]

            if len(new_data) != len(data):
                f.seek(0)
                json.dump(new_data, f, indent=4, ensure_ascii=False)
                f.truncate()
    except FileNotFoundError:
        pass

def update_history_from_file(ctx:Context):
    data = get_history()

    ctx.history = [dict_to_entry(e) for e in data]

def cmd_from_history_entry(entry:HistoryEntry):
    return ParsedCommand(
        name = entry.name,
        flags = entry.flags,
        positionals = entry.positionals,
        raw = entry.raw,
        meta = entry.meta
    )
