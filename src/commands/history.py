from datetime import datetime
import logging

from colorama import Fore, Style
from src.commands.base import Command
from src.utils.misc_utils import (
    get_history, remove_entry_from_file, cmd_from_history_entry
)

from src.core.errors import ExecutionError
from src.commands.filesystem import Cp, Mv, Rm

logger = logging.getLogger(__name__)

class History(Command):
    def execute(self, cmd, ctx):
        history = get_history()
        if history:
            self.display_history(history)
        else:
            logger.warning('History is empty')

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)        
    
    @staticmethod
    def display_history(history:list[dict]):
        GREEN = Fore.GREEN + Style.BRIGHT
        YELLOW = Fore.YELLOW + Style.BRIGHT
        RESET = Style.RESET_ALL
        
        for num, cmd in enumerate(history, start=1):
            dt = datetime.fromisoformat(cmd['timestamp'])
            dt_str = dt.strftime("%d %b %H:%M")
            line = (
                        f"{GREEN}{num}{RESET}:"
                        f"{YELLOW}{dt_str}{RESET}:"
                        f"{cmd['raw']}"
                    )
            print(line)

UNDOABLE_OPERATIONS = {
    'cp': Cp().undo,
    'mv': Mv().undo,
    'rm': Rm().undo
}

class Undo(Command):
    def execute(self, cmd, ctx):
        # Find the last undoable operation
        for i in range(len(ctx.history) - 1, -1, -1):
            entry = ctx.history[i]
            
            if entry.name in UNDOABLE_OPERATIONS:
                try:
                    prev_cmd = cmd_from_history_entry(entry)
                    UNDOABLE_OPERATIONS[entry.name](prev_cmd, ctx)
                except Exception as e:
                    raise ExecutionError(f"Failed to undo {entry.name}. Error: {e}")
                ctx.history.pop(i)
                remove_entry_from_file(entry.id)
                break
        else:
            print("No commands to undo")

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)        


if __name__ == "__main__":
    ...