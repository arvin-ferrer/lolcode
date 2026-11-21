import sys
from components.interpreter import LOLCODEInterpreter

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <filename>", file=sys.stderr)
        sys.exit(1)

    interpreter = LOLCODEInterpreter(debug=False)
    try:
        interpreter.run(sys.argv[1])
    except OSError as e:
        print(f"Cannot read '{sys.argv[1]}': {e.strerror}", file=sys.stderr)
        sys.exit(1)
    except SyntaxError as e:
        # Lexical and syntax errors raised by the lexer/parser
        message = str(e)
        if not message.startswith("Lexical error"):
            message = f"Syntax error: {message}"
        print(message, file=sys.stderr)
        sys.exit(1)
    except RecursionError:
        # Must come before RuntimeError, which it subclasses
        print("Error: the program is too large or too deeply nested to parse", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        # Semantic errors already carry their own "Semantic error:" prefix
        print(e, file=sys.stderr)
        sys.exit(1)
    except EOFError:
        print("Error: GIMMEH reached the end of input", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
