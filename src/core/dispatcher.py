from src.commands.files import Ls, Cat, Cp, Mv, Rm
from src.commands.navigation import Cd
from src.core.models import ParsedCommand
from src.core.errors import ExecutionError
from src.core.services import Context

COMMANDS = {
    "ls": Ls().execute,
    "cd": Cd().execute,
    "cat": Cat().execute,
    "cp": Cp().execute,
    "mv": Mv().execute,
    "rm": Rm().execute,
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