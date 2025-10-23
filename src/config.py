from pathlib import Path 

HOME_DIR = Path.home()
ROOT = Path(__file__).resolve().parent.parent

LOGS_FILENAME = 'shell.log'
LOGS_FILE = ROOT / "logs" / LOGS_FILENAME
HISTORY_FILE = ROOT / ".history"

if __name__ == "__main__":
    print(ROOT)