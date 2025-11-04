from src.core.models import ParsedCommand
from src.core.services import Context

class Command:
    def execute(self, cmd: ParsedCommand, ctx: Context):
        raise NotImplementedError

    def undo(self, cmd: ParsedCommand, ctx: Context):
        raise NotImplementedError(f"Undo not supported for {self.__class__.__name__}")
