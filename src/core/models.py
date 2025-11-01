from dataclasses import dataclass

@dataclass
class ParsedCommand:
    name: str
    flags: set[str]
    positionals: list[str]
    meta: dict