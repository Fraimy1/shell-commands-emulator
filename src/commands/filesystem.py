from pathlib import Path
import shutil
import time
import logging

from src.commands.base import Command
from src.config import TRASH_DIR
from src.utils.path_utils import resolve_path
from src.utils.misc_utils import has_flag
from src.core.errors import ExecutionError
from src.core.models import ParsedCommand

logger = logging.getLogger(__name__)

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
            
            cmd.meta["dest"] = str(copy_to)
        except Exception as e:
            raise ExecutionError(f'Error during copying from {copy_from.name} to {copy_to.name}: {e}')
        
    def undo(self, cmd, ctx):
        rm = Rm()
        rm_cmd = ParsedCommand(
            name = 'cp_undo',
            raw = 'undo',
            flags= ['r'], 
            positionals=[Path(cmd.meta['dest'])],
            meta = {
                'non_interactive': True,
                'fully_remove': True
            }
        )

        rm.execute(rm_cmd, ctx) 
        

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
            cmd.meta['src'] = str(move_from)
            cmd.meta['dest'] = str(move_to)
        except Exception as e:
            raise ExecutionError(f'Error during moving from {move_from.name} to {move_to.name}: {e}')
            
    def undo(self, cmd, ctx):
            mv_cmd = ParsedCommand(
                name = 'mv_undo',
                raw = 'undo',
                flags = ['r'],
                positionals = [Path(cmd.meta['dest']), Path(cmd.meta['src'])] # moving back to src
            )
            self.execute(mv_cmd, ctx)

class Rm(Command):
    def execute(self, cmd, ctx):
        target = resolve_path(cmd.positionals[0], ctx)
        non_interactive: bool = bool(cmd.meta.get("non_interactive", False))
        fully_remove: bool = bool(cmd.meta.get("fully_remove", False))

        if (target.is_dir() 
            and not has_flag(cmd, 'r', 'recursive')
            and any(target.iterdir())
            ):
            raise ExecutionError("Unable to remove non-empty directories without '--recursive' tag.")
        
        if not target.exists():
            raise ExecutionError(f"File doesn't exist. ({target})")
        
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

        try:
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

        except PermissionError: 
            raise ExecutionError(f"No permission to remove {target.name}")
        
    def undo(self, cmd, ctx):
            src = Path(cmd.meta['original_path'])

            trash_id = cmd.meta['trash_id']
            unique_name = f"{trash_id}_{src.name}"
            trash_path = TRASH_DIR / unique_name
            
            mv = Mv()

            mv_cmd = ParsedCommand(
                name = 'rm_undo',
                raw = 'undo_rm',
                flags = ['r'],
                positionals = [trash_path, src] # moving back to src
            )

            mv.execute(mv_cmd, ctx)