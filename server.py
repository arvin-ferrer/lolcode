import json
from pathlib import Path
import threading
from flask import Flask
from flask_sock import Sock
from simple_websocket import ConnectionClosed

from components.interpreter import LOLCODEInterpreter
from components.semantic_analyzer import SemanticAnalyzer
from model.lexeme import Lexeme

# Path to the built frontend assets directory
DIST_DIR = Path(__file__).resolve().parent / "frontend" / "dist"

# Initialize Flask application serving static files from frontend/dist
app = Flask(__name__, static_folder=str(DIST_DIR), static_url_path="")
# Initialize WebSocket extension for Flask
sock = Sock(app)
# Shared semantic analyzer instance used to format symbol values as YARN
formatter = SemanticAnalyzer()


# Format symbol table entries into [name, value] pairs for the frontend
def format_symbols(symbol_table):
    if not symbol_table:
        return []
    # Convert each symbol value to YARN or "NOOB" when None
    return [
        [name, "NOOB" if entry["value"] is None else formatter.to_yarn(entry["value"], explicit=True)]
        for name, entry in symbol_table.table.items()
    ]


# Serve the frontend index.html at the root URL
@app.route("/")
def index():
    return app.send_static_file("index.html")


# Handle one LOLCODE execution session per WebSocket connection
@sock.route("/ws")
def ws_handler(ws):
    # Track whether the browser disconnected during an I/O callback
    disconnected = False

    # Send a JSON message over the socket and flag disconnects
    def send_msg(payload):
        nonlocal disconnected
        try:
            ws.send(json.dumps(payload))
        except ConnectionClosed:
            disconnected = True
            raise

    # Stream VISIBLE output to the browser
    def output_fn(text):
        send_msg({"type": "output", "text": text})

    # Request GIMMEH input from the browser and wait for the reply
    def input_fn():
        nonlocal disconnected
        send_msg({"type": "input_request"})
        try:
            raw = ws.receive()
        except ConnectionClosed:
            disconnected = True
            raise
        if raw is None:
            disconnected = True
            raise ConnectionClosed()
        return json.loads(raw).get("value", "")

    # Push live global symbol table updates to the browser
    def on_update(symbol_table):
        send_msg({"type": "symbols", "symbols": format_symbols(symbol_table)})

    # Receive the initial run message from the client
    try:
        raw = ws.receive()
    except ConnectionClosed:
        return
    if not raw:
        return
    msg = json.loads(raw)
    if msg.get("type") != "run":
        return

    # Create interpreter wired with WebSocket callbacks
    interpreter = LOLCODEInterpreter(output_fn=output_fn, input_fn=input_fn, on_update=on_update)
    error = None
    # Shortcut: an infinite loop with no I/O keeps its thread alive until restart
    try:
        interpreter.run_source(msg.get("code", ""))
    except Exception as exc:
        if disconnected:
            return
        error = str(exc)

    # Omit NEWLINE tokens and map token types to their Lexeme enum names
    lexemes = [
        [token.lexeme, token.type.name]
        for token in interpreter.tokens
        if token.type != Lexeme.NEWLINE
    ]

    # Send the final execution result to the client
    try:
        send_msg({
            "type": "done",
            "lexemes": lexemes,
            "symbols": format_symbols(interpreter.symbol_table),
            "error": error,
        })
        # Wait for the client to close the socket so done is flushed before teardown
        ws.receive(timeout=5)
    except ConnectionClosed:
        pass


if __name__ == "__main__":
    # Set a 64 MB thread stack size so deep recursion does not overflow Windows 1 MB server threads
    threading.stack_size(64 * 1024 * 1024)
    app.run(port=8000)
