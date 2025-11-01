import re
from src.config import COMMANDS
from src.core.models import ParsedCommand
from src.core.errors import ParsingError
TOKEN_PATTERN = r"--?\w+|'[^']*'|\S+"

PATTERN = re.compile(TOKEN_PATTERN)

class Parser: 
    @staticmethod
    def parse_command(string:str):
        words = PATTERN.findall(string)
        return words

    def tokenize(self, string:str):
        words = self.parse_command(string)
        if not words:
            raise ParsingError("Empty command")
        
        name = words.pop(0)
        spec = COMMANDS.get(name)
        
        if not spec:
            raise ParsingError(f"Command '{name}' is not supported")
        
        flags, pos = set(), []
        for w in words:
            if w.startswith('--') or w.startswith('-'):
                if w not in spec['flags']:
                    raise ParsingError(f"No flag '{w}' for '{name}'")
                flags.add(w)
            else:
                pos.append(w.strip("'"))
        
        return ParsedCommand(name=name, flags=flags, 
                             positionals=pos, raw=self._advanced_strip(string))
    
    def _advanced_strip(string:str):
        return re.sub(r'\s+', ' ', string.strip())

if __name__ == "__main__":
    parser = Parser()
    while True:
        command = input("Enter command: ")
        print(parser.tokenize(command))