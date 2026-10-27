from components.interpreter import LOLCODEInterpreter
import pprint

# TODO: Add your backend code here
#       You can use the LOLCODEInterpreter class to run your LOLCODE programs.
#       Only provide the file_location in the run method of the interpreter.

if __name__ == "__main__":
    interpreter = LOLCODEInterpreter(debug=True)
    interpreter.run("example.lol")
