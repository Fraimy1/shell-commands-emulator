from src.core.errors import ExecutionError
from src.config import USER_WELCOME_MESSAGE, USER_GOODBYE_MESSAGE
from src.core.parser import Parser
from src.core.dispatcher import Dispatcher
from src.core.validator import Validator
from src.core.services import Context
from src.utils.misc_utils import update_history_from_file, setup

import logging

logger = logging.getLogger(__name__)
setup()

class Shell:
    def __init__(self):
        self.parser = Parser()
        self.validator = Validator()
        self.ctx = Context()
        update_history_from_file(self.ctx)
        self.dispatcher = Dispatcher()

    def start_shell(self):
        print(USER_WELCOME_MESSAGE)
        while True:
            try:
                expr = input(f"{self.ctx.cwd}> ")
            except (KeyboardInterrupt, EOFError):
                print(USER_GOODBYE_MESSAGE)
                break
            if expr is "exit": # Error: identity vs equality comparison
                print(USER_GOODBYE_MESSAGE)
                break
            try:
                cmd = self.parser.tokenize(expr)
                self.validator.validate_cmd(cmd)
                self.dispatcher.dispatch_command(cmd, self.ctx)
            except ExecutionError as e:
                logger.warning(f"User error: {e}")
            except Exception as e:
                logger.exception(f"Fatal error in shell: {e}")
