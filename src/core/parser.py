import re
from src.config import COMMANDS
from src.core.models import ParsedCommand
from src.core.errors import ParsingError

import shlex
import logging 

logger = logging.getLogger(__name__)

class Parser: 
    @staticmethod
    def parse_command(string:str):
        words = shlex.split(string)
        return words

    def tokenize(self, string:str):
        words = self.parse_command(string)
        logger.debug(f"Got these words after parsing {string}: {words}")
        if not words:
            raise ParsingError("Empty command")
        name = words.pop(0)
        spec = COMMANDS.get(name)
        
        if not spec:
            raise ParsingError(f"Command '{name}' is not supported")
        
        flags, pos = set(), []
        for w in words:
            if not w.startswith('-'):
                pos.append(w.strip("'"))
                if len(pos) > spec['max_pos']:
                    raise ParsingError('Too many positional arguments: ' 
                                       f'Must be from {spec['min_pos']} to {spec['max_pos']} '
                                       f'But {len(pos)} were given')
                continue
                
            if w.startswith('--'):
                w = w.lstrip('-')
                if w not in spec['flags']:
                    raise ParsingError(f"No flag '--{w}' for '{name}'")    
                flags.add(w)
            else:
                w = w.lstrip('-')
                for flag in w:
                    if flag not in spec['flags']:
                        raise ParsingError(f"No flag '-{flag}' for '{name}'")
                    flags.add(flag)
        cmd = ParsedCommand(name=name, flags=flags, 
                             positionals=pos, raw=self._advanced_strip(string))
        logger.debug(f'{cmd=}')
        return cmd 
    
    @staticmethod
    def _advanced_strip(string:str):
        return re.sub(r'\s+', ' ', string.strip())

if __name__ == "__main__":
    parser = Parser()
    while True:
        command = input("Enter command: ")
        print(parser.tokenize(command))