import pprint
from lexical_analyzer import LexicalAnalyzer
from semantic_analyzer import SemanticAnalyzer 
from syntax_analyzer import Parser

def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()

def main():
    raw_content = read_file("full_spec_test.lol")          # Read the raw text

    lexer = LexicalAnalyzer()                       # Create the lexer object then run
    tokens = lexer.run(raw_content)
    parser = Parser(tokens)                         # Create the parser object then run
    parse_tree = parser.parse()

    semantic_analyzer = SemanticAnalyzer()          # Create the semantic analyzer then run
    semantic_analyzer.run(parse_tree)


if __name__ == "__main__":
    main()