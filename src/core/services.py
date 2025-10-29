from pathlib import Path
from src.core.models import ParsedCommand

class Context:
    def __init__(self):
        self.cwd: Path = Path.cwd()
        self.history: list[ParsedCommand] = []