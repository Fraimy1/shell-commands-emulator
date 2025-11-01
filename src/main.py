from src.shell import Shell
from src.utils.log_utils import setup_logging

setup_logging()

shell = Shell()

def main():
    shell.start_shell()


if __name__ == '__main__':
    main()