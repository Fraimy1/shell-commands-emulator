from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ParsedCommand:
    name: str
    flags: set[str]
    positionals: list[str]
    raw: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

@dataclass
class HistoryEntry:
    id: int
    raw: str
    name: str
    flags: set[str] = field(default_factory=set)
    positionals: list[str] = field(default_factory=list)
    cwd: Path
    timestamp: str
    meta: dict[str, Any] = field(default_factory=dict)