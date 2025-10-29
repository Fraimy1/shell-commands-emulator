from pathlib import Path
from src.core.errors import ExecutionError
from src.commands.base import Command

class Cd(Command):
    def execute(self, cmd, ctx):
        target = Path(cmd.positionals[0]).expanduser().resolve()
        if target.is_dir():
            ctx.cwd = target
        else:
            raise ExecutionError(f"Not a directory: {target}")