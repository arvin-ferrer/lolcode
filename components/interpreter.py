from components.lexical_analyzer import LexicalAnalyzer
from components.semantic_analyzer import SemanticAnalyzer 
from components.syntax_analyzer import Parser

from model.token import Token
from model.node import Node
from model.symbol_table import SymbolTable
import pprint
class LOLCODEInterpreter:
    def __init__(self, output_fn=None, input_fn=None, debug=False):
        self.debug = debug
        self.output_fn = output_fn
        self.input_fn = input_fn if input_fn else input
        self.tokens: list[Token] = []
        self.parse_tree: Node = None
        self.symbol_table: SymbolTable = None
        
    def read_file(self, file_path):
        with open(file_path, "r") as file:
            return file.read()

    def run(self, file_path):
        pp = pprint.PrettyPrinter(indent=4)

        raw_content = self.read_file(file_path)         # Read the raw text
        lexer = LexicalAnalyzer()                       # Create the lexer object then run
        self.tokens = lexer.run(raw_content)
        if self.debug:
            pp.pprint(self.tokens)

        parser = Parser(self.tokens)                    # Create the parser object then run
        self.parse_tree = parser.parse()
        if self.debug:
            self.parse_tree.display()
        # semantic_analyzer = SemanticAnalyzer(output_fn=self.output_fn, input_fn=self.input_fn)          # Create the semantic analyzer then run
        # self.symbol_table = semantic_analyzer.run(self.parse_tree)
