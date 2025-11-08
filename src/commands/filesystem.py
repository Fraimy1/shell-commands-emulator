from pathlib import Path
import shutil
import time
import logging

from src.commands.base import FileSystemCommand, RmCommand
from src.config import TRASH_DIR
from src.utils.path_utils import resolve_path
from src.core.models import ParsedCommand
from src.core.services import Context

logger = logging.getLogger(__name__)

class Cp(FileSystemCommand):
    """Copies file from source to destination
    - Undo removes the copy (Calls Rm)   
    """
    
    def execute(self, cmd: ParsedCommand, ctx: Context) -> None:
        copy_from = resolve_path(cmd.positionals[0], ctx)
        copy_to = resolve_path(cmd.positionals[1], ctx)
        
        self.ensure_exists(copy_from)
        self.ensure_recursive(copy_from, cmd)

        logger.info(f"Copying {copy_from} -> {copy_to}")
        self.safe_exec(self.copy_file, copy_from, copy_to, cmd,
                       msg = f'Error during copying from {copy_from.name} to {copy_to.name}')

    @staticmethod
    def copy_file(src:Path, dst:Path, cmd:ParsedCommand):
        if hasattr(src, 'copy'):
            src.copy(dst)
        else:
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy(src, dst)
        cmd.meta["dest"] = str(dst)

    def undo(self, cmd: ParsedCommand, ctx: Context) -> None:
        rm = Rm()
        rm_cmd = ParsedCommand(
            name = 'cp_undo',
            raw = 'undo',
            flags= {'r'},
            positionals=[str(Path(cmd.meta['dest']))],
            meta = {
                'non_interactive': True,
                'fully_remove': True
            }
        )

        rm.execute(rm_cmd, ctx)

class Mv(FileSystemCommand):
    """Moves file from source to destination
    - Undo moves the files from destination to source (Calls Mv)     
    """
    
    def execute(self, cmd: ParsedCommand, ctx: Context) -> None:
        move_from = resolve_path(cmd.positionals[0], ctx)
        move_to = resolve_path(cmd.positionals[1], ctx)

        if move_to.is_dir() and move_from.name != move_to.name and not move_from.is_dir():
            move_to = move_to / move_from.name

        self.ensure_exists(move_from)
        self.ensure_recursive(move_from, cmd)

        logger.warning(f"Moving {move_from} → {move_to}")
        self.safe_exec(self.move_file, move_from, move_to, cmd,
                       msg = f'Error during moving from {move_from.name} to {move_to.name}')
    
    @staticmethod
    def move_file(src:Path, dst:Path, cmd:ParsedCommand):
        if hasattr(src, 'move'):
            src.move(dst)
        else:
            shutil.move(src, dst)
        cmd.meta['src'] = str(src)
        cmd.meta['dest'] = str(dst)

    def undo(self, cmd: ParsedCommand, ctx: Context) -> None:
            mv_cmd = ParsedCommand(
                name = 'mv_undo',
                raw = 'undo',
                flags = {'r'},
                positionals = [str(Path(cmd.meta['dest'])), str(Path(cmd.meta['src']))] # moving back to src
            )
            self.execute(mv_cmd, ctx)

class Rm(RmCommand):
    """Removes source file and moves it to trash

    It is assigned a {trash_id}_{target.name} in trash, 
    so it can be moved back to source for Undo
    
    - undo moves from trash back to source (calls Mv)
    """
    
    def execute(self, cmd: ParsedCommand, ctx: Context) -> None:
        target = resolve_path(cmd.positionals[0], ctx)
        non_interactive: bool = bool(cmd.meta.get("non_interactive", False))
        fully_remove: bool = bool(cmd.meta.get("fully_remove", False))

        self.ensure_exists(target)
        self.ensure_not_home_dir(target)
        self.ensure_recursive(target, cmd)
        
        agreed = None
        if non_interactive:
            agreed = True
        else:
            logger.warning(f"This action will move {target} to trash")
            while agreed is None:
                user_input = input(f"Are you sure you want to delete {target.name}? Y/n: ")
                if user_input.lower() == 'y':
                    agreed = True
                elif user_input.lower() == 'n':
                    agreed = False
                    return

        self.safe_exec(self.remove_file, target, cmd, fully_remove,
                       msg = f"Couldn't remove {target.name}")

    @staticmethod
    def remove_file(target:Path, cmd:ParsedCommand, fully_remove:bool):
            if fully_remove:
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                return

            trash_id = time.time_ns()
            unique_name = f"{trash_id}_{target.name}"
            trash_path = TRASH_DIR / unique_name
            cmd.meta["original_path"] = str(target)
            cmd.meta["trash_id"] = trash_id
            target.rename(trash_path)

    def undo(self, cmd: ParsedCommand, ctx: Context) -> None:
            src = Path(cmd.meta['original_path'])

            trash_id = cmd.meta['trash_id']
            unique_name = f"{trash_id}_{src.name}"
            trash_path = TRASH_DIR / unique_name

            mv = Mv()

            mv_cmd = ParsedCommand(
                name = 'rm_undo',
                raw = 'undo_rm',
                flags = {'r'},
                positionals = [str(trash_path), str(src)] # moving back to src
            )

            mv.execute(mv_cmd, ctx)
