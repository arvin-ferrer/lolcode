import pprint
from lexical_analyzer import LexicalAnalyzer
from semantic_analyzer import SemanticAnalyzer 
from syntax_analyzer import Parser

def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()

def main():
    pp = pprint.PrettyPrinter(indent=4)             # object for printing the symbol table neatly

    raw_content = read_file("example.lol")          # Read the raw text

    lexer = LexicalAnalyzer()                       # Create the lexer object then run
    tokens = lexer.run(raw_content)
    # pp.pprint(tokens)
    parser = Parser(tokens)                         # Create the parser object then run
    parse_tree = parser.parse()
    # parse_tree.display()                            # Display the parse tree

    semantic_analyzer = SemanticAnalyzer()          # Create the semantic analyzer then run
    symbol_table = semantic_analyzer.run(parse_tree)

    # pp.pprint(symbol_table.table)                   # Print the symbol table

if __name__ == "__main__":
    main()