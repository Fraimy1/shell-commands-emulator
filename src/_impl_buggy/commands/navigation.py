from src.commands.base import Command
from src.config import HOME_DIR
from src.utils.path_utils import resolve_path

class Cd(Command):
    """Moves current directory to the one specified

    has special ~ that returns to home directory
    """

    def execute(self, cmd, ctx):
        if cmd.positionals[0] == '~':
            ctx.cwd = HOME_DIR.resolve()
            return True

        target = resolve_path(cmd.positionals[0], ctx)
        self.ensure_exists(target)
        self.ensure_dir(target)

        ctx.cwd = target
