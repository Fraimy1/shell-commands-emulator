from src.core.models import ParsedCommand
from src.core.services import Context
from src.config import HISTORY_FILE

def has_flag(cmd:ParsedCommand, *flags):
    return any(f in cmd.flags for f in flags)

def append_history(cmd:ParsedCommand, ctx:Context, append_to_file:bool = True):
    ctx.history.append(cmd)
    if append_to_file:
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(cmd + '\n')
            
def update_history_from_file(ctx:Context):
    commands = []
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            commands.append(exec(line.strip()))
    
    ctx.history.insert(commands)
    ctx.history = commands + ctx.history
