from pathlib import Path
from src.core.models import ParsedCommand, HistoryEntry

class Context:
    def __init__(self):
        self.cwd: Path = Path.cwd()
        self.history: list[HistoryEntry] = []