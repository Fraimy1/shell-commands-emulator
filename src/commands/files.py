"""
Docstring for commands.files 
ls, cat, cp, mv, rm - here
"""

import typer
from pathlib import Path
from src.config import ROOT, HOME_DIR
from datetime import datetime

app = typer.Typer(help="File management commands")

@app.command()
def ls(
    directory: str = Path.cwd(),
    l: bool = False
):
    path = Path(directory).resolve()
    for file in Path.iterdir(path):
        if l:
            info = Path(path/file).stat()
            print(info)

            return True
        
        print(file)
        return True

if __name__ == "__main__":
    app()