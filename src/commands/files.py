"""
Docstring for commands.files 
ls, cat, cp, mv, rm - here
"""

from pathlib import Path
from src.config import ROOT, HOME_DIR
from datetime import datetime
from src.commands.base import Command
from tabulate import tabulate
import stat

class Ls(Command):
    def execute(self, cmd, ctx):
        directory = Path(cmd.positionals[0]).resolve() if cmd.positionals else ctx.cwd
        long = ('-l' in cmd.flags) or ('--long' in cmd.flags)
        
        data = []
        for entry in directory.iterdir():
            if long:
                info = entry.stat()
                mode = stat.filemode(info.st_mode)
                size = info.st_size
                last_modified = datetime.fromtimestamp(info.st_mtime)
                file_created = datetime.fromtimestamp(info.st_birthtime)
                is_dir = entry.is_dir()
                links = info.st_nlink
                name = entry.name + ' (DIR)' if is_dir else entry.name
                data.append((name, mode, links, size, last_modified, file_created))
            else:
                print(entry.name)

        if long: 
            headers = ['Name', 'Mode', 'Links', 'Size', 
                       'Modified', 'Created']
            print(tabulate(data, headers=headers, tablefmt='plain'))

class Cp(Command):
    def execute(self, cmd, ctx):
        return super().execute(cmd, ctx)

class Cat(Command):
    def execute(self, cmd, ctx):
        return super().execute(cmd, ctx)

class Mv(Command):
    def execute(self, cmd, ctx):
        return super().execute(cmd, ctx)

class Rm(Command):
    def execute(self, cmd, ctx):
        return super().execute(cmd, ctx)


if __name__ == "__main__":
    ...