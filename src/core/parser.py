import re
from src.config import COMMANDS
from src.core.models import ParsedCommand
TOKEN_PATTERN = r"--\w+|-\w+|\w+|'\w+'"

PATTERN = re.compile(TOKEN_PATTERN)

class ParserError(Exception):
    pass

class Parser: 
    @staticmethod
    def parse_command(string:str):
        words = PATTERN.findall(string)
        return words

    def tokenize(self, string:str):
        words = self.parse_command(string)
        if not words:
            raise ParserError("Empty command")
        
        name = words.pop()
        spec = COMMANDS.get(name)
        
        if not spec:
            raise ParserError(f"Command '{name}' is not supported")
        
        flags, pos = set(), []
        for i, word in enumerate(words):
            if word.startswith('--') or word.startswith('-'):
                if word not in spec['flags']:
                    raise ParserError(f"No flag '{word}' for '{name}'")
                flags.add(word)
            else:
                word = word.strip("'")
                if word.isdigit():
                    word = int(word)
                
                pos.append(word)
        
        return ParsedCommand(name=name, flags=flags, positionals=pos)

if __name__ == "__main__":
    parser = Parser()
    while True:
        command = input("Enter command: ")
        print(parser.tokenize(command))