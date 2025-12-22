from pathlib import Path
from src.core.models import HistoryEntry

class Context:
    def __init__(self) -> None:
        self.cwd: Path = Path.cwd()
        self.history: list[HistoryEntry] = []
