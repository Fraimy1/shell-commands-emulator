from pathlib import Path 
import logging

HOME_DIR = Path.home()
ROOT = Path(__file__).resolve().parent.parent

LOGS_FILENAME = 'shell.log'
LOGS_FILE = ROOT / "logs" / LOGS_FILENAME
HISTORY_FILE = ROOT / ".history.json"
TRASH_DIR = ROOT / ".trash"

USER_WELCOME_MESSAGE = ""
USER_GOODBYE_MESSAGE = ""

CONSOLE_LOG_LEVEL = logging.DEBUG
FILE_LOG_LEVEL = logging.DEBUG

COMMANDS = {
    'cp': {'flags': {'recursive', 'r'}, 'max_pos': 2, 'min_pos': 2},
    'mv': {'flags': {'recursive','r'}, 'max_pos': 2, 'min_pos': 2},
    'rm': {'flags': {'recursive', 'r',}, 'max_pos': 1, 'min_pos': 1},
    'ls': {'flags': {'l', 'long'}, 'max_pos': 1, 'min_pos': 0},
    'cd': {'flags': set(), 'max_pos': 1, 'min_pos': 1},
    'cat': {'flags': set(), 'max_pos': 1, 'min_pos': 1},

    'zip': {'flags': set(), 'max_pos': 2, 'min_pos': 2},
    'unzip': {'flags': set(), 'max_pos': 1, 'min_pos': 1},
    'tar': {'flags': set(), 'max_pos': 2, 'min_pos': 2},
    'untar': {'flags': set(), 'max_pos': 1, 'min_pos': 1},

    'grep': {'flags': {'r', 'recursive', 'i', 'ignore-case'}, 'max_pos': 2, 'min_pos': 2},
    
    'history': {'flags': set(), 'max_pos': 0, 'min_pos': 0},
    'undo': {'flags': set(), 'max_pos': 0, 'min_pos': 0},
}


if __name__ == "__main__":
    print(ROOT)