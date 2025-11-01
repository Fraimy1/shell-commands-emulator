from src.commands.files import Ls, Cat, Cp, Mv, Rm, Zip, Unzip
from src.commands.files import Tar, Untar, Grep, History, Undo
from src.commands.navigation import Cd
from src.core.models import ParsedCommand
from src.core.errors import ExecutionError
from src.core.services import Context

import logging 

logger = logging.getLogger(__name__)

COMMANDS = {
    "ls": Ls().execute,
    "cd": Cd().execute,
    "cat": Cat().execute,
    "cp": Cp().execute,
    "mv": Mv().execute,
    "rm": Rm().execute,
    "zip": Zip().execute,
    "unzip": Unzip().execute,
    "tar": Tar().execute,
    "untar": Untar().execute,
    "grep": Grep().execute,
    "history": History().execute,
    "undo": Undo().execute
}

class Dispatcher:
    @staticmethod
    def dispatch_command(cmd: ParsedCommand, ctx: Context):

        handler = COMMANDS[cmd.name]
        
        try:
            logger.debug(f"Executing: {cmd.name}")
            handler(cmd, ctx)
            ctx.history.append(cmd)
            logger.debug(f"Success: {cmd.name}")
        
        except ExecutionError as e:
            logger.warning(f"{cmd.name}: {e}")
            raise
        
        except KeyboardInterrupt as e:
            logger.info(f'Command {cmd.name} execution was interrupted.')

        except Exception as e:
            logger.exception(f"Unexpected error in {cmd.name}")
            raise ExecutionError(f"Unexpected error in {cmd.name}: {e}")