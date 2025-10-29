from pathlib import Path
from src.core.errors import ExecutionError
from src.commands.base import Command
from src.config import HOME_DIR
from src.utils.path_utils import resolve_path

class Cd(Command):
    def execute(self, cmd, ctx):

        if cmd.positionals[0] == '~':
            ctx.cwd = HOME_DIR.resolve()
            return True

        target = resolve_path(cmd.positionals[0], ctx)

        if target.is_dir():
            ctx.cwd = target
        else:
            raise ExecutionError(f"Not a directory: {target}")