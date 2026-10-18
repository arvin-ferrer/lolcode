import pprint
import lexer
import tokenizer
import parser as pr
import symbol_table as st
import semantic_analyzer as sa

def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()

def main():
    symbol_table = st.SymbolTable()
    # For printing
    pp = pprint.PrettyPrinter(indent=4)

    raw_content = read_file("example.lol")
    content = lexer.run(raw_content)
    tokens = tokenizer.run(content)
    # print(content)
    parser = pr.Parser(tokens)
    semantic_analyzer = sa.SemanticAnalyzer(symbol_table)

    parse_tree = parser.parse()
    # parse_tree.display()

    semantic_analyzer.analyze(parse_tree)

    # pp.pprint(symbol_table.table)

if __name__ == "__main__":
    main()