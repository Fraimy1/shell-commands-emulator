import logging
from pathlib import Path

from src.config import FILE_LOG_LEVEL, CONSOLE_LOG_LEVEL

LOG_FILE = Path("logs/shell.log")
LOG_FILE.parent.mkdir(exist_ok=True)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    console.setLevel(CONSOLE_LOG_LEVEL)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(FILE_LOG_LEVEL)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)

    logging.debug("Logging initialized.")
