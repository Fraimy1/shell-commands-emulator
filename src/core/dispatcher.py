from src.commands.files import call_ls, cp, mv, rm, cat
from src.commands.navigation import cd
from src.core.models import ParsedCommand

COMMAND_HANDLERS = {
    "ls": call_ls,
    "cd": cd,
    "cat": cat,
    "cp": cp,
    "mv": mv,
    "rm": rm,
}

def dispatch_command(cmd: ParsedCommand):
    handler = COMMAND_HANDLERS.get(cmd.name)

    if handler is None:
        print(f"Unknown command: {cmd.name}")
        return

    try:
        handler(cmd)  # pass the rest of the args
    except Exception as e:
        print(f"Error executing {cmd.name}: {e}")
