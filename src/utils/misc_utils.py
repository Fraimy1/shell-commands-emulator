from src.core.models import ParsedCommand
from src.core.services import Context
from src.config import HISTORY_FILE

from datetime import datetime
import json

def has_flag(cmd:ParsedCommand, *flags):
    return any(f in cmd.flags for f in flags)

def append_history(cmd:ParsedCommand, ctx:Context, append_to_file:bool = True):
    ctx.history.append(cmd)
    if not append_to_file:
        return 
    
    entry = {
        "raw": cmd.raw,
        "name": cmd.name,
        "flags": cmd.flags,
        "positionals": cmd.positionals,
        "cwd": str(ctx.cwd),
        "timestamp": datetime.now().isoformat(),
    }
    
    try:
        with open(HISTORY_FILE, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()
    except FileNotFoundError:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([entry], f, indent=4, ensure_ascii=False)


def get_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    return data

def update_history_from_file(ctx:Context):
    data = get_history()

    ctx.history = [
        ParsedCommand(
            name=e["name"],
            flags=e.get("flags", []),
            positionals=e.get("positionals", []),
            raw=e.get("raw", ""),
        )
        for e in data
    ]