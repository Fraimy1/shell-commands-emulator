from pathlib import Path 

HOME_DIR = Path.home()
ROOT = Path(__file__).resolve().parent.parent

LOGS_FILENAME = 'shell.log'
LOGS_FILE = ROOT / "logs" / LOGS_FILENAME
HISTORY_FILE = ROOT / ".history"

USER_WELCOME_MESSAGE = ""
USER_GOODBYE_MESSAGE = ""

COMMANDS = {
    'cp': {'flags': {'--recursive',}, 'max_pos': 2, 'min_pos': 2},
    'mv': {'flags': set(), 'max_pos': 2, 'min_pos': 2},
    'rm': {'flags': {'--recursive',}, 'max_pos': 1, 'min_pos': 1},
    'ls': {'flags': {'-l', '--long'}, 'max_pos': 1, 'min_pos': 0},
    'cd': {'flags': set(), 'max_pos': 1, 'min_pos': 1},
}
if __name__ == "__main__":
    print(ROOT)