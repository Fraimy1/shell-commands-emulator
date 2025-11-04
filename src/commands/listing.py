from datetime import datetime
from tabulate import tabulate
import stat
import logging

from src.commands.base import Command
from src.utils.path_utils import resolve_path
from src.utils.misc_utils import has_flag
from src.core.errors import ExecutionError

logger = logging.getLogger(__name__)

class Ls(Command):
    def execute(self, cmd, ctx):
        directory = resolve_path(cmd.positionals[0], ctx) if cmd.positionals else ctx.cwd
        long = has_flag(cmd, 'l', 'long')
        
        if not directory.exists():
            raise ExecutionError(f"No such file or directory: {directory}")
        
        data = []
        logger.debug(f"Listing directory: {directory}")
        for entry in directory.iterdir():
            if long:
                info = entry.stat()
                permissions = stat.filemode(info.st_mode)[1:]
                size = info.st_size
                last_modified = datetime.fromtimestamp(info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                if hasattr(info, "st_birthtime"):
                    file_created = datetime.fromtimestamp(info.st_birthtime).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    file_created = None # Not avilable on Linux
                is_dir = entry.is_dir()
                links = info.st_nlink
                name = entry.name + ' (DIR)' if is_dir else entry.name
                
                if file_created is None:
                    data.append((name, permissions, links, size, last_modified))
                else:
                    data.append((name, permissions, links, size, last_modified, file_created))
            else:
                print(entry.name)

        if long: 
            headers = ['Name', 'Perms', 'Links', 'Size', 
                       'Modified', 'Created']
            if file_created is None:
                headers.remove('Created')

            print(tabulate(data, headers=headers, tablefmt='plain'))
        
    
    def undo(self, cmd, ctx):
        return super().undo(cmd, ctx)

class Cat(Command):
    def execute(self, cmd, ctx):
        target = resolve_path(cmd.positionals[0], ctx)

        if target.is_dir():
            raise ExecutionError(f"cat doesn't support dirrectories. ({target.name})")

        if not(target.exists()):
            raise ExecutionError(f"file doesn't exist. ({target})")
        
        try:
            with open(target, 'r') as f:
                print(f.read())
        except Exception:
            raise ExecutionError(f"cat can't read this file. ({target})")

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)