from pathlib import Path
import re
import logging
from colorama import Fore, Style

from src.commands.base import Command
from src.utils.path_utils import resolve_path
from src.utils.misc_utils import has_flag
from src.core.errors import ExecutionError

logger = logging.getLogger(__name__)

class Grep(Command):
    """Returns all lines of the file matching pattern 
    
    --recursive/-r - to look inside folder
    --ignore-case/-i - to ignore case when matching pattern
    """
    
    def execute(self, cmd, ctx):
        pattern_raw = cmd.positionals[0]
        path = resolve_path(cmd.positionals[1], ctx)
        recursive = has_flag(cmd, 'r', 'recursive')
        case_insensitive = has_flag(cmd, 'i', 'ignore-case')

        flags = 0
        if case_insensitive:
            flags |= re.IGNORECASE

        pattern = re.compile(pattern_raw, flags)
        display_path = path.relative_to(ctx.cwd)

        logger.debug(f"Searching pattern '{pattern_raw}' in {path}")

        if path.is_dir():
            if not recursive:
                raise ExecutionError(f'--recursive/-r flag required for grepping dir {path.name}')
            self.find_in_dir(pattern, path, display_path, ctx)
        else:
            self.grep_file(pattern, path, ignore_open_errors=True, display_path = display_path)


    @staticmethod
    def grep_file(pattern:re.Pattern, path:Path, ignore_open_errors:bool, display_path:Path):
        # colors to mimic real grep
        GREEN = Fore.GREEN + Style.BRIGHT
        YELLOW = Fore.YELLOW + Style.BRIGHT
        RED = Fore.RED + Style.BRIGHT
        RESET = Style.RESET_ALL

        try:
            with path.open('r', encoding='utf-8') as f:

                for line_num, line in enumerate(f, start=1):
                    found = re.search(pattern, line)
                    if found:
                        found_highlighted = pattern.sub(RED + r"\g<0>" + RESET, line.rstrip())
                        line = (
                                    f"{GREEN}{display_path}{RESET}:"
                                    f"{YELLOW}{line_num}{RESET}:"
                                    f"{found_highlighted}"
                                )
                        print(line)

        except Exception: # TODO: add handling for all errors.
            if not ignore_open_errors:
                raise ExecutionError(f"Failed to read file {path.name}")

    def find_in_dir(self, pattern:re.Pattern, path:Path, display_path, ctx):
        for file_path in path.iterdir():
            display_path = file_path.relative_to(ctx.cwd)

            if file_path.is_dir():
                self.find_in_dir(pattern, file_path, display_path, ctx) # Goes recursively through each file
            else:
                self.grep_file(pattern, file_path, ignore_open_errors = True, display_path = display_path)

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)
