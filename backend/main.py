from components.interpreter import LOLCODEInterpreter
import pprint

import os
import tempfile
from flask import Flask, jsonify, request

# TODO: Add your backend code here
#       You can use the LOLCODEInterpreter class to run your LOLCODE programs.
#       Only provide the file_location in the run method of the interpreter.

app = Flask(__name__)

@app.post("/api/run")
def run_code():
    """
    Run the .lol program sent by the frontend and return its results.
    """
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    output = []     # To store lines that will be outputted by VISIBLE

    interpreter = LOLCODEInterpreter(output_fn=output.append, input_fn=lambda: "",) # New interpreter instance for every request
    path = None
    error = None

    try:
        # Write the text in the text editor in a temporary file first then run
        with tempfile.NamedTemporaryFile("w", suffix=".lol", delete=False, encoding="utf-8") as file:
            file.write(code)
            path = file.name
        interpreter.run(path)
    except SyntaxError as e:
        error = {"kind": "Syntax error", "message": str(e)}
    except RuntimeError as e: 
        error = {"kind": "Runtime error", "message": str(e)}
    finally:
        if path:
            os.remove(path)

    # List to store lexemes, one row per token (lexeme and classification type)
    # NEWLINE tokens are skipped
    lexemes = []
    for token in interpreter.tokens:
        if token.type.name != "NEWLINE":
            lexemes.append({"lexeme": token.lexeme, "type": token.type.name})

    # List for the symbol table, one row per variable (identifier and value)
    symbols = []
    table = {}
    if interpreter.symbol_table:
        table = interpreter.symbol_table.table
    for name, entry in table.items():
        symbols.append({"name": name, "value": entry["value"]})

    return jsonify({
        "lexemes": lexemes,
        "symbols": symbols,
        "output": "".join(output),
        "error": error
    })

if __name__ == "__main__":
    app.run(port=8000, debug=True)
