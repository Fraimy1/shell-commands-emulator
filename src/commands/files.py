"""
Docstring for commands.files 
ls, cat, cp, mv, rm - here
"""

from pathlib import Path
from src.config import ROOT, HOME_DIR
from datetime import datetime
from src.commands.base import Command

class Ls(Command):
    def execute(self, cmd, ctx):
        directory = Path(cmd.positionals[0]).resolve() if cmd.positionals else ctx.cwd
        long = ('-l' in cmd.flags) or ('--long' in cmd.flags)
        for entry in directory.iterdir():
            if long:
                info = entry.stat()
                print(info)
            else:        
                print(entry.name)

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