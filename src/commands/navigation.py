from pathlib import Path
from src.core.errors import ExecutionError

def cd(cmd, ctx):
    target = Path(cmd.positionals[0]).expanduser().resolve()
    if target.is_dir():
        ctx.cwd = target
    else:
        raise ExecutionError(f"Not a directory: {target}")