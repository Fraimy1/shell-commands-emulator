from src.core.models import ParsedCommand
from src.core.services import Context

class Command:
    """An interface that all Commands must follow"""

    def execute(self, cmd: ParsedCommand, ctx: Context):
        """Execution of the function"""
        raise NotImplementedError

    def undo(self, cmd: ParsedCommand, ctx: Context):
        """If implemented, undos the operation. Called only from Undo class"""
        raise NotImplementedError(f"Undo not supported for {self.__class__.__name__}")
