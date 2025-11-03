from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ParsedCommand:
    name: str
    flags: set[str]
    positionals: list[str]
    raw: str

@dataclass
class HistoryEntry:
    id: int
    raw: str
    name: str
    flags: set[str]
    positionals: list[str]
    cwd: Path
    timestamp: str
    meta: dict[str, Any]