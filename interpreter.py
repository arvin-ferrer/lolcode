import pprint
from lexical_analyzer import LexicalAnalyzer
from semantic_analyzer import SemanticAnalyzer 
from syntax_analyzer import Parser

def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()

def main():
    # For printing
    pp = pprint.PrettyPrinter(indent=4)

    raw_content = read_file("example.lol")
    lexer = LexicalAnalyzer()
    tokens = lexer.run(raw_content)

    parser = Parser(tokens)
    parse_tree = parser.parse()
    # parse_tree.display()

    semantic_analyzer = SemanticAnalyzer()
    symbol_table = semantic_analyzer.analyze(parse_tree)

    # pp.pprint(symbol_table.table)

if __name__ == "__main__":
    main()