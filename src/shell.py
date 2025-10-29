from src.config import USER_WELCOME_MESSAGE, USER_GOODBYE_MESSAGE
from src.core.parser import Parser
from pathlib import Path
from src.core.dispatcher import Dispatcher
from src.core.validator import Validator
from src.core.services import Context

class Shell:
    def __init__(self):
        self.parser = Parser()
        self.validator = Validator()
        self.ctx = Context()
        self.dispatcher = Dispatcher

    def start_shell(self):
        print(USER_WELCOME_MESSAGE)
        while True:
            try:
                expr = input(f"{self.ctx.cwd}> ")
            except KeyboardInterrupt:
                print("\n", USER_GOODBYE_MESSAGE)
                break
            if expr == "exit":
                print(USER_GOODBYE_MESSAGE)
                break
            try:
                cmd = self.parser.tokenize(expr)
                self.validator.validate_cmd(cmd)
                self.dispatcher.dispatch_command(cmd, self.ctx)
            except Exception as e:
                print(f"Error: {e}\n")