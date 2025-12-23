from pathlib import Path
from src.core.models import HistoryEntry

class Context:
    def __init__(self, history: list[HistoryEntry] = []) -> None:
        self.cwd: Path = Path.cwd()
        # Error: mutable default value
        self.history: list[HistoryEntry] = history
        _ = None