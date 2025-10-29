"""
Docstring for commands.files 
ls, cat, cp, mv, rm - here
"""

# import typer
from pathlib import Path
from src.config import ROOT, HOME_DIR
from datetime import datetime
from src.core.models import ParsedCommand

# app = typer.Typer(help="File management commands")

# @app.command()
def ls(directory = Path.cwd(),long: bool = False):
    path = Path(directory).resolve()
    for entry in path.iterdir():
        if long:
            info = entry.stat()
            print(info)
        else:        
            print(entry.name)
    return True

def call_ls(cmd: ParsedCommand):
    directory = Path(cmd.positionals[0]) if cmd.positionals else Path.cwd()
    long = ('-l' in cmd.flags) or ('--long' in cmd.flags)
    ls(directory, long)

def cp():
    ...

def cat():
    ...

def mv():
    ...

def rm():
    ...



if __name__ == "__main__":
    ls(long=True)