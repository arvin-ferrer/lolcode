import sys
from components.interpreter import LOLCODEInterpreter, format_error

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
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except (SyntaxError, RuntimeError, EOFError) as e:
        # Lexical, syntax and semantic errors: one clean line instead of a traceback
        print(format_error(e), file=sys.stderr)
        sys.exit(1)
