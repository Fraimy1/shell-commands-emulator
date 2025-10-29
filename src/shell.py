from src.config import USER_WELCOME_MESSAGE, USER_GOODBYE_MESSAGE
from src.core.parser import Parser
from pathlib import Path
from src.core.dispatcher import dispatch_command

def start_shell():
    parser = Parser()

    print(USER_WELCOME_MESSAGE)
    while True:
        try:
            current_path = Path().cwd()
            expr = input(f"{current_path}> ")
        except KeyboardInterrupt:
            print("\n", USER_GOODBYE_MESSAGE)
            break
        if expr == "exit":
            print(USER_GOODBYE_MESSAGE)
            break
        try:
            cmd = parser.tokenize(expr)
            dispatch_command(cmd)
        except Exception as e:
            print(f"Error: {e}\n")