"""
Docstring for commands.files 
ls, cat, cp, mv, rm - here
"""

from pathlib import Path
from src.config import ROOT, HOME_DIR
from src.core.errors import ExecutionError
from datetime import datetime
from src.commands.base import Command
from tabulate import tabulate
from src.utils.path_utils import resolve_path
import stat

class Ls(Command):
    def execute(self, cmd, ctx):
        directory = resolve_path(cmd.positionals[0], ctx) if cmd.positionals else ctx.cwd
        long = ('-l' in cmd.flags) or ('--long' in cmd.flags)
        
        data = []
        for entry in directory.iterdir():
            if long:
                info = entry.stat()
                permissions = stat.filemode(info.st_mode)[1:]
                size = info.st_size
                last_modified = datetime.fromtimestamp(info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                file_created = datetime.fromtimestamp(info.st_birthtime).strftime("%Y-%m-%d %H:%M:%S")
                is_dir = entry.is_dir()
                links = info.st_nlink
                name = entry.name + ' (DIR)' if is_dir else entry.name
                data.append((name, permissions, links, size, last_modified, file_created))
            else:
                print(entry.name)

        if long: 
            headers = ['Name', 'Perms', 'Links', 'Size', 
                       'Modified', 'Created']
            print(tabulate(data, headers=headers, tablefmt='plain'))

class Cp(Command):
    def execute(self, cmd, ctx):
        copy_from = resolve_path(cmd.positionals[0], ctx)
        copy_to = resolve_path(cmd.positionals[1], ctx)
        if (copy_from.is_dir() 
            and not ('-r' in cmd.flags or '--recursive' in cmd.flags)
            and any(copy_from.iterdir())
            ):
            raise ExecutionError("Unable to copy non-empty directories without '--recursive' tag.")
        
        if not copy_from.exists():
            raise ExecutionError(f"File doesn't exist. ({copy_from})")
        
        try:
            copy_from.copy(copy_to)
        except Exception as e:
            raise ExecutionError(f'Error during copying from {copy_from.name} to {copy_to.name}: {e}')
        
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

class Mv(Command):
    def execute(self, cmd, ctx):
        return super().execute(cmd, ctx)

class Rm(Command):
    def execute(self, cmd, ctx):
        return super().execute(cmd, ctx)


if __name__ == "__main__":
    ...