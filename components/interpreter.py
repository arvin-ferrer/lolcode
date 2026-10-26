from components.lexical_analyzer import LexicalAnalyzer
from components.semantic_analyzer import SemanticAnalyzer 
from components.syntax_analyzer import Parser

from model.token import Token
from model.node import Node
from model.symbol_table import SymbolTable

class LOLCODEInterpreter:
    def __init__(self, output_fn=print, input_fn=input):
        self.output_fn = output_fn
        self.input_fn = input_fn
        self.tokens: list[Token] = []
        self.parse_tree: Node = None
        self.symbol_table: SymbolTable = None
        
    def read_file(self, file_path):
        with open(file_path, "r") as file:
            return file.read()

    def run(self, file_path):
        raw_content = self.read_file(file_path)         # Read the raw text

        lexer = LexicalAnalyzer()                       # Create the lexer object then run
        self.tokens = lexer.run(raw_content)
        parser = Parser(self.tokens)                    # Create the parser object then run
        self.parse_tree = parser.parse()

        semantic_analyzer = SemanticAnalyzer()          # Create the semantic analyzer then run
        self.symbol_table = semantic_analyzer.run(self.parse_tree)
