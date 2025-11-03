from pathlib import Path
from zipfile import ZipFile
import zipfile
import tarfile
import logging

from src.commands.base import Command
from src.utils.path_utils import resolve_path
from src.core.errors import ExecutionError

logger = logging.getLogger(__name__)

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