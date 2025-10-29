from src.commands.files import call_ls, cp, mv, rm, cat
from src.commands.navigation import cd
from src.core.models import ParsedCommand
from src.core.errors import ExecutionError
from src.core.services import Context

COMMANDS = {
    "ls": call_ls,
    "cd": cd,
    "cat": cat,
    "cp": cp,
    "mv": mv,
    "rm": rm,
}

class Dispatcher:
    @staticmethod
    def dispatch_command(cmd: ParsedCommand, ctx: Context):

        handler = COMMANDS[cmd.name]
        
        try:
            handler(cmd, ctx)
            ctx.history.append(cmd)
        except Exception as e:
            raise ExecutionError(f"Error executing {cmd.name}: {e}")