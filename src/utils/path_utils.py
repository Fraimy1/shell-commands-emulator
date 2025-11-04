from pathlib import Path
from src.core.services import Context

def resolve_path(path_str: str, ctx:Context) -> Path:
    """
    Resolves path as either absolute or relative path.
    """
    path = Path(path_str)

    if path.is_absolute():
        return path.resolve()
    else:
        return (ctx.cwd / path).expanduser().resolve()
