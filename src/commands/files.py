"""
Docstring for commands.files 
ls, cat, cp, mv, rm - here
"""

import enum
from pathlib import Path
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style

from src.core.errors import ExecutionError
from src.core.models import ParsedCommand
from src.config import TRASH_DIR
from src.commands.base import Command
from src.utils.path_utils import resolve_path
from src.utils.misc_utils import has_flag, get_history, update_history_from_file
from src.utils.misc_utils import append_history

import stat
import shutil
import zipfile
from zipfile import ZipFile
import tarfile
import re
import logging

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


class Cp(Command):
    def execute(self, cmd, ctx):
        copy_from = resolve_path(cmd.positionals[0], ctx)
        copy_to = resolve_path(cmd.positionals[1], ctx)
        if (copy_from.is_dir() 
            and not has_flag(cmd, 'r', 'recursive')
            and any(copy_from.iterdir())
            ):
            raise ExecutionError("Unable to copy non-empty directories without '--recursive' tag.")
        
        if not copy_from.exists():
            raise ExecutionError(f"File doesn't exist. ({copy_from})")
        
        try:
            logger.info(f"Copying {copy_from} -> {copy_to}")
            if hasattr(copy_from, 'copy'):
                copy_from.copy(copy_to)
            else:
                if copy_from.is_dir():
                    shutil.copytree(copy_from, copy_to)
                else:
                    shutil.copy(copy_from, copy_to)
        except Exception as e:
            raise ExecutionError(f'Error during copying from {copy_from.name} to {copy_to.name}: {e}')
    
    def undo(self, cmd, ctx):
        rm = Rm()
        rm_cmd = ParsedCommand(
            name = 'cp_undo',
            flags= cmd.flags, 
            positionals=[cmd.positionals[1]]
        )

        rm.execute(rm_cmd, ctx) 

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


class Mv(Command):
    def execute(self, cmd, ctx):
        move_from = resolve_path(cmd.positionals[0], ctx)
        move_to = resolve_path(cmd.positionals[1], ctx)

        if move_to.is_dir() and move_from.name != move_to.name and not move_from.is_dir():
            move_to = move_to / move_from.name

        if (move_from.is_dir() 
            and not has_flag(cmd, 'r', 'recursive')
            and any(move_from.iterdir())
            ):
            raise ExecutionError("Unable to move non-empty directories without '--recursive' tag.")
        
        if not move_from.exists():
            raise ExecutionError(f"File doesn't exist. ({move_from})")
        try:
            logger.warning(f"Moving {move_from} → {move_to}")
            if hasattr(move_from, 'move'):
                move_from.move(move_to)
            else:
                shutil.move(move_from, move_to)
        except Exception as e:
            raise ExecutionError(f'Error during moving from {move_from.name} to {move_to.name}: {e}')
        
    def undo(self, cmd, ctx):
            src, dest = cmd.positionals 
            mv_cmd = ParsedCommand(
                name = 'mv_undo',
                flags = cmd.flags,
                positionals = [dest, src] # moving back to src
            )

            self.execute(mv_cmd, ctx)

class Rm(Command):
    def execute(self, cmd, ctx):
        target = resolve_path(cmd.positionals[0], ctx)
        # relative_path = target.relative_to(ctx.cwd)

        if (target.is_dir() 
            and not has_flag(cmd, 'r', 'recursive')
            and any(target.iterdir())
            ):
            raise ExecutionError("Unable to remove non-empty directories without '--recursive' tag.")
        
        if not target.exists():
            raise ExecutionError(f"File doesn't exist. ({target})")

        agreed = None
        logger.warning(f"This action will move {target} to trash")
        while agreed is None:
            user_input = input(f"Are you sure you want to delete {target.name}? Y/n: ")
            if user_input.lower() == 'y':
                agreed = True
            elif user_input.lower() == 'n': 
                agreed = False 
                return False
            
        try: 
            unique_name = f"{target.name}_{len(ctx.history)}"
            trash_path = TRASH_DIR / unique_name
            target.rename(trash_path)

        except PermissionError: 
            raise ExecutionError(f"No permission to remove {target.name}")
    
    def undo(self, cmd, ctx):
            cmd = ctx.history[-1]
            src = cmd.positionals[0]
            unique_name = f"{src.name}_{len(ctx.history)-1}"
            trash_path = TRASH_DIR / unique_name
            
            mv = Mv()

            mv_cmd = ParsedCommand(
                name = 'rm_undo',
                flags = cmd.flags,
                positionals = [trash_path, src] # moving back to src
            )

            mv.execute(mv_cmd, ctx)


class Zip(Command):
    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest = resolve_path(cmd.positionals[1], ctx)

        if not src.is_dir():
            raise ExecutionError(f"{src} must be a directory")

        if not dest.name.endswith('.zip'):
            raise ExecutionError(f"Destination must be a .zip file. But got {dest.name}")

        if not src.exists():
            raise ExecutionError(f"File doesn't exist. ({src})")
        
        try:
            logger.info(f"Archiving {src} -> {dest}")
            self.zip_dir(src, dest) 
        except Exception as e:
            raise ExecutionError(f'Error zipping the folder {src.name} into {dest.name}: {e}')
    
    @staticmethod
    def zip_dir(folder: Path, dest: Path):
        with ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for file in folder.rglob('*'):
                zipf.write(file, arcname=file.relative_to(folder))        

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)        


class Unzip(Command):
    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest_dir = ctx.cwd / src.name.replace('.zip', '')

        if not src.name.endswith('.zip'):
            raise ExecutionError(f"Source must be a .zip file. But got {src.name}")

        if not src.exists():
            raise ExecutionError(f"File doesn't exist. ({src})")
        
        try:
            logger.info(f"Unarchiving {src} -> {dest_dir}")
            self.unzip_dir(src, dest_dir) 
        except Exception as e:
            raise ExecutionError(f'Error unzipping the file {src.name} into {dest_dir.name}: {e}')
    
    @staticmethod
    def unzip_dir(zipfile: Path, dest_dir: Path):
        with ZipFile(zipfile, 'r') as zipf:
            zipf.extractall(dest_dir)

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)        


class Tar(Command):
    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest = resolve_path(cmd.positionals[1], ctx)

        if not src.is_dir():
            raise ExecutionError(f"{src} must be a directory")

        if not dest.name.endswith('.tar'):
            raise ExecutionError(f"Destination must be a .tar file. But got {dest.name}")

        if not src.exists():
            raise ExecutionError(f"File doesn't exist. ({src})")
        
        try:
            logger.info(f"Archiving {src} -> {dest}")
            self.tar_dir(src, dest) 
        except Exception as e:
            raise ExecutionError(f'Error tarring the folder {src.name} into {dest.name}: {e}')
            
    @staticmethod
    def tar_dir(folder: Path, dest: Path):
        with tarfile.open(dest, 'w:gz') as tarf:
            tarf.add(folder, arcname=folder.name)

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)        


class Untar(Command):
    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest_dir = ctx.cwd

        if not src.name.endswith('.tar'):
            raise ExecutionError(f"Source must be a .tar file. But got {src.name}")

        if not src.exists():
            raise ExecutionError(f"File doesn't exist. ({src})")
        
        try:
            logger.info(f"Unarchiving {src} -> {dest_dir}")
            self.untar_dir(src, dest_dir) 
        except Exception as e:
            raise ExecutionError(f'Error untarring the file {src.name} into {dest_dir.name}: {e}')
    
    @staticmethod
    def untar_dir(src_tar: Path, dest_dir: Path):
        with tarfile.open(src_tar, 'r:*') as tarf:
            tarf.extractall(path=dest_dir)

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)        


class Grep(Command):
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


class History(Command):
    def execute(self, cmd, ctx):
        history = get_history()
        if history:
            self.display_history(history)
        else:
            logger.warning('History is empty')

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)        
    
    def display_history(history:list[dict]):
        GREEN = Fore.GREEN + Style.BRIGHT
        YELLOW = Fore.YELLOW + Style.BRIGHT
        RESET = Style.RESET_ALL
        
        
        for num, cmd in enumerate(history, start=1):
            dt = datetime.fromisoformat(cmd['timestamp'])
            dt_str = dt.strftime("%d %b %H:%M")
            line = (
                        f"{GREEN}{num}{RESET}:"
                        f"{YELLOW}{dt_str}{RESET}:"
                        f"{cmd['raw']}"
                    )
            print(line)

    
class Undo(Command):
    def execute(self, cmd, ctx):
        return super().execute(cmd, ctx)

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)        


if __name__ == "__main__":
    ...