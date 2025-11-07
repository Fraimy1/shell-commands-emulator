from pathlib import Path
from zipfile import ZipFile
import zipfile
import tarfile
import logging

from src.commands.base import ArchiveCommand
from src.utils.path_utils import resolve_path

logger = logging.getLogger(__name__)

class Zip(ArchiveCommand):
    """Compress directory/file into .zip file"""
    
    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest = resolve_path(cmd.positionals[1], ctx)

        self.ensure_exists(src)
        self.ensure_dir(src)
        self.ensure_zip(dest)

        logger.info(f"Archiving {src} -> {dest}")
        self.safe_exec(self.zip_dir, src, dest, 
                       msg = f"Error zipping the folder {src.name} into {dest.name}")

    @staticmethod
    def zip_dir(folder: Path, dest: Path):
        with ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for file in folder.rglob('*'):
                zipf.write(file, arcname=file.relative_to(folder))

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)


class Unzip(ArchiveCommand):
    """Unzip .zip file to a directory"""

    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest_dir = ctx.cwd / src.name.replace('.zip', '')

        self.ensure_exists(src)
        self.ensure_zip(src)

        logger.info(f"Unarchiving {src} -> {dest_dir}")
        self.safe_exec(self.unzip_dir, src,
                        dest_dir, msg=f"Error unzipping the file {src.name} into {dest_dir.name}")

    @staticmethod
    def unzip_dir(zipfile: Path, dest_dir: Path):
        with ZipFile(zipfile, 'r') as zipf:
            zipf.extractall(dest_dir)

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)


class Tar(ArchiveCommand):
    """Tar file/directory into a .tar file"""

    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest = resolve_path(cmd.positionals[1], ctx)

        self.ensure_exists(src)
        self.ensure_dir(src)
        self.ensure_tar(dest)

        logger.info(f"Archiving {src} -> {dest}")        
        self.safe_exec(self.tar_dir, src, dest,
                        msg = f'Error tarring the folder {src.name} into {dest.name}')
        
    @staticmethod
    def tar_dir(folder: Path, dest: Path):
        with tarfile.open(dest, 'w:gz') as tarf:
            tarf.add(folder, arcname=folder.name)

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)


class Untar(ArchiveCommand):
    """Untar .tar file to a directory"""

    def execute(self, cmd, ctx):
        src = resolve_path(cmd.positionals[0], ctx)
        dest_dir = ctx.cwd

        self.ensure_exists(src)
        self.ensure_tar(src)

        logger.info(f"Unarchiving {src} -> {dest_dir}")
        self.safe_exec(self.untar_dir, src, dest_dir,
                       msg = f'Error untarring the file {src.name} into {dest_dir.name}')

    @staticmethod
    def untar_dir(src_tar: Path, dest_dir: Path):
        with tarfile.open(src_tar, 'r:*') as tarf:
            tarf.extractall(path=dest_dir)

    def undo(self, cmd, ctx):
            return super().undo(cmd, ctx)
