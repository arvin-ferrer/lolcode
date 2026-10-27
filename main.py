from components.interpreter import LOLCODEInterpreter
import pprint

# TODO: Add your backend code here
#       You can use the LOLCODEInterpreter class to run your LOLCODE programs.
#       Only provide the file_location in the run method of the interpreter.

# For printing the output in a more readable format

if __name__ == "__main__":
    interpreter = LOLCODEInterpreter(debug=True)
    interpreter.run("example.lol")

    # print("Tokens")
    # print("\nParse Tree")
    # interpreter.parse_tree.display()
    # # print("Symbol Table:", interpreter.symbol_table)