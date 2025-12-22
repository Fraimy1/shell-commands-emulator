from src.core.models import ParsedCommand
from src.config import COMMANDS
from src.core.errors import ValidationError
from typing import cast

class Validator:
    def validate_cmd(self, cmd: ParsedCommand):
        spec = COMMANDS.get(cmd.name)

        if spec is None:
            raise ValidationError(f"Unknown command: {cmd.name}")

        min_pos = cast(int, spec['min_pos'])
        max_pos = cast(int, spec['max_pos'])
        n_pos = len(cmd.positionals)
        if not (min_pos <= n_pos <= max_pos):
            raise ValidationError(f"{cmd.name} expects from {min_pos} to {max_pos} "
                                  f"positional arguments, but {n_pos} were given")
