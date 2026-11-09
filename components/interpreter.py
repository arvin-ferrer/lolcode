from components.lexical_analyzer import LexicalAnalyzer
from components.semantic_analyzer import SemanticAnalyzer 
from components.syntax_analyzer import Parser

from model.token import Token
from model.node import Node
from model.symbol_table import SymbolTable
import pprint
class LOLCODEInterpreter:
    def __init__(self, output_fn=None, input_fn=None, debug=False, on_update=None):
        self.debug = debug
        self.output_fn = output_fn
        self.input_fn = input_fn if input_fn else input
        self.on_update = on_update
        self.tokens: list[Token] = []
        self.lexemes: list[str] = []
        self.parse_tree: Node = None
        self.symbol_table: SymbolTable = None
        self.semantic_analyzer: SemanticAnalyzer = None
        
    def read_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def run_source(self, text):
        pp = pprint.PrettyPrinter(indent=4)

        lexer = LexicalAnalyzer()                       # Create the lexer object then run
        self.lexemes, self.tokens = lexer.run(text)
        if self.debug:
            print(self.lexemes)
            pp.pprint(self.tokens)

        parser = Parser(self.tokens)                    # Create the parser object then run
        self.parse_tree = parser.parse()
        if self.debug:
            self.parse_tree.display()
        self.semantic_analyzer = SemanticAnalyzer(output_fn=self.output_fn, input_fn=self.input_fn, on_update=self.on_update)          # Create the semantic analyzer then run
        try:
            self.symbol_table = self.semantic_analyzer.run(self.parse_tree)
        finally:
            if self.semantic_analyzer and self.semantic_analyzer.symbol_table:
                self.symbol_table = self.semantic_analyzer.symbol_table
        if self.debug:
            pp.pprint(self.symbol_table.table)
        return self.symbol_table

    def run(self, file_path):
        return self.run_source(self.read_file(file_path))
