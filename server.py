import json
import os
import threading
from flask import Flask, send_from_directory
from flask_sock import Sock
from simple_websocket import ConnectionClosed

from components.interpreter import LOLCODEInterpreter
from components.semantic_analyzer import SemanticAnalyzer
from model.lexeme import Lexeme

# Set thread stack size to 64 MB to handle recursion limit on Windows
threading.stack_size(64 * 1024 * 1024)

DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")

app = Flask(__name__, static_folder=DIST_DIR, static_url_path="")
sock = Sock(app)

# Format symbol table entries for WebSocket protocol
def format_symbol_table(symbol_table, analyzer=None):
    if not symbol_table or not getattr(symbol_table, "table", None):
        return []
    to_yarn_fn = analyzer.to_yarn if analyzer else SemanticAnalyzer().to_yarn
    return [
        [name, "NOOB" if info.get("value") is None else to_yarn_fn(info.get("value"), explicit=True)]
        for name, info in symbol_table.table.items()
    ]

# Format tokens into lexeme-type pairs, omitting NEWLINE tokens
def format_lexemes(tokens):
    if not tokens:
        return []
    return [
        [t.lexeme, t.type.name]
        for t in tokens
        if t.type != Lexeme.NEWLINE
    ]

# WebSocket handler for one run per connection
@sock.route("/ws")
def ws_handler(ws):
    raw = ws.receive()
    if not raw:
        return
    try:
        msg = json.loads(raw)
    except Exception:
        return
    if msg.get("type") != "run":
        return

    code = msg.get("code", "")
    disconnected = False

    # Send program output to client
    def output_fn(text):
        nonlocal disconnected
        if disconnected:
            return
        try:
            ws.send(json.dumps({"type": "output", "text": text}))
        except Exception:
            disconnected = True

    # Request and wait for user input from client
    def input_fn(prompt=""):
        nonlocal disconnected
        if disconnected:
            raise RuntimeError("Client disconnected")
        try:
            ws.send(json.dumps({"type": "input_request"}))
            reply = ws.receive()
            if reply is None:
                disconnected = True
                raise RuntimeError("Client disconnected")
            data = json.loads(reply)
            if data.get("type") == "input":
                return data.get("value", "")
            return ""
        except Exception:
            disconnected = True
            raise

    # Send live symbol updates on variable changes
    def on_update(st):
        nonlocal disconnected
        if disconnected:
            return
        symbols = format_symbol_table(st, interpreter.semantic_analyzer)
        try:
            ws.send(json.dumps({"type": "symbols", "symbols": symbols}))
        except Exception:
            disconnected = True

    interpreter = LOLCODEInterpreter(
        output_fn=output_fn,
        input_fn=input_fn,
        on_update=on_update,
    )

    error_msg = None
    try:
        interpreter.run_source(code)
    except Exception as e:
        if disconnected:
            return
        error_msg = str(e)

    # Shortcut: an infinite loop with no I/O keeps its thread alive until restart.
    st = interpreter.symbol_table or (
        interpreter.semantic_analyzer.symbol_table
        if interpreter.semantic_analyzer
        else None
    )
    symbols = format_symbol_table(st, interpreter.semantic_analyzer)
    lexemes = format_lexemes(interpreter.tokens)

    done_msg = {
        "type": "done",
        "lexemes": lexemes,
        "symbols": symbols,
        "error": error_msg,
    }

    try:
        ws.send(json.dumps(done_msg))
        ws.receive(timeout=5)
    except (ConnectionClosed, Exception):
        pass

# Serve frontend static assets and index.html
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path == "ws":
        return "", 404
    target = os.path.join(DIST_DIR, path)
    if path and os.path.exists(target):
        return send_from_directory(DIST_DIR, path)
    if os.path.exists(os.path.join(DIST_DIR, "index.html")):
        return send_from_directory(DIST_DIR, "index.html")
    return "frontend/dist not found. Run 'npm run build' inside frontend/.", 404

# Run development server
if __name__ == "__main__":
    threading.stack_size(64 * 1024 * 1024)
    app.run(host="0.0.0.0", port=8000)

