from components.interpreter import LOLCODEInterpreter

# TODO: Add your backend code here
#       You can use the LOLCODEInterpreter class to run your LOLCODE programs.
#       Only provide the file_location in the run method of the interpreter.

if __name__ == "__main__":
    interpreter = LOLCODEInterpreter()
    interpreter.run("example.lol")

    # print("Tokens:", interpreter.tokens)
    # print("Parse Tree:", interpreter.parse_tree.display())
    # print("Symbol Table:", interpreter.symbol_table)