from src.core.models import ParsedCommand
from src.core.services import Context
from src.core.errors import ExecutionError
from pathlib import Path
from src.utils.path_utils import resolve_path
from src.utils.misc_utils import has_flag
import logging

logger = logging.getLogger(__name__)

class Command:
    """An interface that all Commands must follow"""

    def execute(self, cmd: ParsedCommand, ctx: Context):
        """Execution of the function"""
        raise NotImplementedError

    def undo(self, cmd: ParsedCommand, ctx: Context):
        """If implemented, undos the operation. Called only from Undo class"""
        raise NotImplementedError(f"Undo not supported for {self.__class__.__name__}")

    # Helper shared functions

    def resolve(self, path_str: str, ctx) -> Path:
        """Resolve path safely within context."""
        return resolve_path(path_str, ctx)

    def ensure_exists(self, path: Path):
        """Raise ExecutionError if path doesn't exist."""
        if not path.exists():
            logger.debug(f"File or directory not found: {path}")
            raise ExecutionError(f"File or directory not found: {path}")

    def ensure_dir(self, path: Path):
        """Raise ExecutionError if path is not a directory."""
        if not path.is_dir():
            logger.debug(f"Expected directory, got: {path}")
            raise ExecutionError(f"Expected directory, got: {path}")

    def ensure_file(self, path: Path):
        """Raise ExecutionError if path is not a file."""
        if not path.is_file():
            logger.debug(f"Expected file, got: {path}")
            raise ExecutionError(f"Expected file, got: {path}")

    def safe_exec(self, func, *args, msg: str = "Execution failed", **kwargs):
        """Wrapper to handle common exceptions."""
        try:
            return func(*args, **kwargs)
        except ExecutionError:
            raise
        except Exception as e:
            logger.exception(e)
            raise ExecutionError(f"{msg}: {e}")
        
class ArchiveCommand(Command):
    """An interface for archive-related commands"""

    def ensure_zip(self, path:Path):
        if not path.name.endswith('.zip'):
            raise ExecutionError(f"Destination must be a .zip file. But got {path.name}")
        
    def ensure_tar(self, path:Path):
        if not path.name.endswith('.tar'):
            raise ExecutionError(f"Destination must be a .tar file. But got {path.name}")
        
class FileSystemCommand(Command):
    """An interface for filesystem-related commands"""

    def ensure_recursive(self, path:Path, cmd: ParsedCommand):
        if (path.is_dir()
            and not has_flag(cmd, 'r', 'recursive')
            and any(path.iterdir())
            ):
            raise ExecutionError("Unable to copy non-empty directories without --recursive/-r tag.")