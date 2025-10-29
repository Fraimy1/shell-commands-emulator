from pathlib import Path 

HOME_DIR = Path.home()
ROOT = Path(__file__).resolve().parent.parent

LOGS_FILENAME = 'shell.log'
LOGS_FILE = ROOT / "logs" / LOGS_FILENAME
HISTORY_FILE = ROOT / ".history"

USER_WELCOME_MESSAGE = ""
USER_GOODBYE_MESSAGE = ""

COMMANDS = {
    'cp': {'flags': ['--recursive'], 'options': [], 'positionals': 2},
    'mv': {'flags': [], 'options': [], 'positionals': 2},
    'rm': {'flags': ['--recursive'], 'options': [], 'positionals': 1},
    'ls': {'flags': ['-l', '--long'], 'options': [], 'positionals': 1},
}
if __name__ == "__main__":
    print(ROOT)