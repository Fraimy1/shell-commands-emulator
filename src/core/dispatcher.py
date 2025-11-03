from src.commands.listing import Ls, Cat
from src.commands.filesystem import Cp, Mv, Rm
from src.commands.navigation import Cd
from src.commands.archive import Zip, Unzip, Tar, Untar
from src.commands.search import Grep
from src.commands.history import History, Undo
from src.core.models import HistoryEntry, ParsedCommand
from src.core.errors import ExecutionError
from src.core.services import Context
from src.utils.misc_utils import append_history


from datetime import datetime
import time
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
            entry = HistoryEntry(
                id = time.time_ns(),
                raw = cmd.raw,
                name = cmd.name,
                flags = set(cmd.flags),
                positionals = list(cmd.positionals),
                cwd = ctx.cwd,
                timestamp = datetime.now().isoformat(),
                meta = dict(cmd.meta)
            )
            append_history(ctx, entry)
            logger.debug(f"Success: {cmd.name}")
        
        except ExecutionError as e:
            logger.warning(f"{cmd.name}: {e}")
            raise
        
        except KeyboardInterrupt as e:
            logger.info(f'Command {cmd.name} execution was interrupted.')

        except Exception as e:
            logger.exception(f"Unexpected error in {cmd.name}")
            raise ExecutionError(f"Unexpected error in {cmd.name}: {e}")