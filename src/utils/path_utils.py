from pathlib import Path
from src.core.services import Context
from src.core.models import ParsedCommand

def resolve_path(path: str, ctx:Context) -> Path:
    """
    Resolves path as either absolute or relative path.
    """
    path = Path(path)

    if path.is_absolute():
        return path.resolve()
    else:
        return (ctx.cwd / path).expanduser().resolve()
    