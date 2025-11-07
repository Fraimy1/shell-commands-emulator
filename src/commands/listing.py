from datetime import datetime
from tabulate import tabulate
from pathlib import Path
import stat
import logging

from src.commands.base import Command
from src.utils.path_utils import resolve_path
from src.utils.misc_utils import has_flag

logger = logging.getLogger(__name__)

class Ls(Command):
    """Returns a list of files in the dir
    
    --long/-l - gives full data about files in the dir 
    """
    
    def execute(self, cmd, ctx):
        directory = resolve_path(cmd.positionals[0], ctx) if cmd.positionals else ctx.cwd
        long = has_flag(cmd, 'l', 'long')

        self.ensure_exists()
        self.ensure_dir()
        
        data = []
        logger.debug(f"Listing directory: {directory}")
        for entry in directory.iterdir():
            if long:
                data.append(self.get_file_stats(entry))
            else:
                print(entry.name)

        if long:
            headers = ['Name', 'Perms', 'Links', 'Size',
                       'Modified', 'Created']
            if data and len(data[0]) < len(headers):
                headers.remove('Created') 
                # on different systems created time might not be recorded

            print(tabulate(data, headers=headers, tablefmt='plain'))

    def get_file_stats(entry:Path):
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
            return (name, permissions, links, size, last_modified)
        else:
            return (name, permissions, links, size, last_modified, file_created)
            
    def undo(self, cmd, ctx):
        return super().undo(cmd, ctx)

class Cat(Command):
    """Reads contents of the file"""
    
    def execute(self, cmd, ctx):
        target = resolve_path(cmd.positionals[0], ctx)

        self.ensure_exists()
        self.ensure_file()

        self.safe_exec(self.read_file, target, msg=f"cat can't read this file. ({target})")
        
    def read_file(path:Path):
        with open(path, 'r') as f:
                    print(f.read())

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)
