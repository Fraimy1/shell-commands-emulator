from src.core.models import ParsedCommand
from src.core.services import Context

class Command:
    def execute(self, cmd: ParsedCommand, ctx: Context):
        raise NotImplementedError
