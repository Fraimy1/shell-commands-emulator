from pathlib import Path
from src.core.errors import ExecutionError
from src.commands.base import Command

class Cd(Command):
    def execute(self, cmd, ctx):
        raw_target = Path(cmd.positionals[0])

        if raw_target.is_absolute():
            target = raw_target.resolve()
        else:
            target = (ctx.cwd / raw_target).expanduser().resolve() 

        if target.is_dir():
            ctx.cwd = target
        else:
            raise ExecutionError(f"Not a directory: {target}")