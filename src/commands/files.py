"""
Docstring for commands.files 
ls, cat, cp, mv, rm - here
"""

from pathlib import Path
from src.core.errors import ExecutionError
from datetime import datetime
from src.commands.base import Command
from tabulate import tabulate
from src.utils.path_utils import resolve_path
import stat
import shutil
import zipfile
from zipfile import ZipFile
import tarfile


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
            if hasattr(copy_from, 'copy'):
                copy_from.copy(copy_to)
            else:
                if copy_from.is_dir():
                    shutil.copytree(copy_from, copy_to)
                else:
                    shutil.copy(copy_from, copy_to)
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
        move_from = resolve_path(cmd.positionals[0], ctx)
        move_to = resolve_path(cmd.positionals[1], ctx)

        if move_to.is_dir() and move_from.name != move_to.name and not move_from.is_dir():
            move_to = move_to / move_from.name

        if (move_from.is_dir() 
            and not ('-r' in cmd.flags or '--recursive' in cmd.flags)
            and any(move_from.iterdir())
            ):
            raise ExecutionError("Unable to move non-empty directories without '--recursive' tag.")
        
        if not move_from.exists():
            raise ExecutionError(f"File doesn't exist. ({move_from})")
        try:
            if hasattr(move_from, 'move'):
                move_from.move(move_to)
            else:
                shutil.move(move_from, move_to)
        except Exception as e:
            raise ExecutionError(f'Error during moving from {move_from.name} to {move_to.name}: {e}')
         


class Rm(Command):
    def execute(self, cmd, ctx):
        target = resolve_path(cmd.positionals[0], ctx)
    
        if (target.is_dir() 
            and not ('-r' in cmd.flags or '--recursive' in cmd.flags)
            and any(target.iterdir())
            ):
            raise ExecutionError("Unable to remove non-empty directories without '--recursive' tag.")
        
        if not target.exists():
            raise ExecutionError(f"File doesn't exist. ({target})")

        agreed = None
        while agreed is None:
            user_input = input(f"Are you sure you want to delete {target.name}? Y/n: ")
            if user_input == 'Y':
                agreed = True
            elif user_input.lower() == 'n': 
                agreed = False 
                return False
        try: 
            if target.is_file():
                target.unlink()
            elif target.is_dir() and not ('-r' in cmd.flags or '--recursive' in cmd.flags):
                target.rmdir()
            else:
                shutil.rmtree(target)
        except PermissionError: 
            raise ExecutionError(f"No permission to remove {target.name}")


class Zip(Command):
    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest_zip = resolve_path(cmd.positionals[1], ctx)

        if not src.is_dir():
            raise ExecutionError(f"{src} must be a directory")

        if not dest_zip.name.endswith('.zip'):
            raise ExecutionError(f"Destination must be a .zip file. But got {dest_zip.name}")

        if not src.exists():
            raise ExecutionError(f"File doesn't exist. ({src})")
        
        try:
            self.zip_dir(src, dest_zip) 
        except Exception as e:
            raise ExecutionError(f'Error zipping the folder {src.name} into {dest_zip.name}: {e}')
    
    @staticmethod
    def zip_dir(folder: Path, dest_zip: Path):
        with ZipFile(dest_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for file in folder.rglob('*'):
                zipf.write(file, arcname=file.relative_to(folder))        


class Unzip(Command):
    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest_dir = ctx.cwd / src.name.replace('.zip', '')

        if not src.name.endswith('.zip'):
            raise ExecutionError(f"Source must be a .zip file. But got {src.name}")

        if not src.exists():
            raise ExecutionError(f"File doesn't exist. ({src})")
        
        try:
            self.unzip_dir(src, dest_dir) 
        except Exception as e:
            raise ExecutionError(f'Error unzipping the file {src.name} into {dest_dir.name}: {e}')
    
    @staticmethod
    def unzip_dir(zipfile: Path, dest_dir: Path):
        with ZipFile(zipfile, 'r') as zipf:
            zipf.extractall(dest_dir)


class Tar(Command):
    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest_tar = resolve_path(cmd.positionals[1], ctx)

        if not src.is_dir():
            raise ExecutionError(f"{src} must be a directory")

        if not dest_tar.name.endswith('.tar'):
            raise ExecutionError(f"Destination must be a .tar file. But got {dest_tar.name}")

        if not src.exists():
            raise ExecutionError(f"File doesn't exist. ({src})")
        
        try:
            self.tar_dir(src, dest_tar) 
        except Exception as e:
            raise ExecutionError(f'Error tarring the folder {src.name} into {dest_tar.name}: {e}')
            
    @staticmethod
    def tar_dir(folder: Path, dest_tar: Path):
        with tarfile.open(dest_tar, 'w:gz') as tarf:
            tarf.add(folder, arcname=folder.name)


class Untar(Command):
    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest_dir = ctx.cwd

        if not src.name.endswith('.tar'):
            raise ExecutionError(f"Source must be a .tar file. But got {src.name}")

        if not src.exists():
            raise ExecutionError(f"File doesn't exist. ({src})")
        
        try:
            self.untar_dir(src, dest_dir) 
        except Exception as e:
            raise ExecutionError(f'Error untarring the file {src.name} into {dest_dir.name}: {e}')
    
    @staticmethod
    def untar_dir(src_tar: Path, dest_dir: Path):
        with tarfile.open(src_tar, 'r:*') as tarf:
            tarf.extractall(path=dest_dir)


class Grep(Command):
    def execute(self, cmd, ctx):
        return super().execute(cmd, ctx)


class History(Command):
    def execute(self, cmd, ctx):
        return super().execute(cmd, ctx)
    

class Undo(Command):
    def execute(self, cmd, ctx):
        return super().execute(cmd, ctx)


if __name__ == "__main__":
    ...