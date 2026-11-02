# GUI Plan

Status: **draft — finalize before implementing.** Source of truth:
`01 CMSC 124 Project Specifications.pdf` §D (GUI, p.13) and §E (presentation).
Stack and UI come from a groupmate's `origin/frontend` (React + Flask); the logic below replaces theirs.

## Decisions

| Topic | Decision | Spec ref |
|---|---|---|
| Stack | React (JSX) + Vite + oxlint in `frontend/`; Flask + `flask-sock` in a root `server.py` | §D "any language" |
| Layout | Groupmate's UI: top bar (file name, Open File, Execute), editor left, lexemes + symbol table right, console bottom | §D diagram |
| Transport | One WebSocket at `/ws` (streamed output, interactive GIMMEH, live symbols) | §D 6, note (b) |
| File explorer | `<input type="file" accept=".lol,.txt">` read with `FileReader` | §D 1 |
| Editor | `<textarea>` + line-number gutter, scroll sync, Tab inserts 4 spaces (from groupmate's version) | §D 2 |
| Lexemes table | Sent **once** per run; *Lexeme \| Classification*; NEWLINE hidden; readable labels | §D 3, note (b) |
| Symbol table | Sent **every time a value is updated**; global frame only (incl. `IT`); *Identifier \| Value* | §D 4, note (b) |
| Values | Formatted on the server with `SemanticAnalyzer.to_yarn(value, explicit=True)` (WIN/FAIL, 2-dp NUMBAR); NOOB shown as `NOOB` | — |
| Input | Input field in the console, enabled only while GIMMEH waits | §D 6 |
| Errors | Console in red; tables keep whatever was produced (partial symbol table too) | — |
| Execute | Disabled while running; no Stop button | §D 5 |
| Production | `npm run build` → `frontend/dist` (gitignored), served by Flask; demo = `python server.py` | §E 1a, 2c |
| Dev | `npm run dev` (:5173) proxies `/api` and `/ws` → :8000 | — |

## Backend changes (small, not yet done)

1. `components/interpreter.py` — split `run(file_path)` into `run(file_path)` → `run_source(text)`
   (removes the groupmate's temp-file workaround). Keep a reference to the `SemanticAnalyzer`
   so the partial symbol table is available after an error. `main.py` CLI unchanged.
2. `components/semantic_analyzer.py` — optional `on_update` callback, called at the global-variable
   write (`self.frame.table.add(...)`, currently line 154) when `self.frame` is the global frame.
3. Catch-all in the server: any exception (not only `SyntaxError`/`RuntimeError`) ends in a `done` with
   `error`, so the UI never shows a blank "Connection error".

## `server.py` (new, root)

- Serves `frontend/dist` (static + `index.html`).
- `WS /ws`: on `run`, start the interpreter in a worker thread:
  - `output_fn` → send `output`.
  - `input_fn` → send `input_request`, block on a `queue.Queue` until `input` arrives.
  - `on_update` → send `symbols`.
  - Always finish with `done`.
- shortcut: an infinite loop without I/O keeps its thread alive until the server restarts.

## Protocol

```
browser → server   {type:"run",   code: string}
                   {type:"input", value: string}
server  → browser  {type:"output",        text: string}
                   {type:"input_request"}
                   {type:"symbols",       symbols: [name, value][]}
                   {type:"done", lexemes: [lexeme, classification][], symbols: [...], error: string | null}
```

## Frontend files

```
frontend/src/
  App.jsx                    state + socket; layout of §D 1–6
  App.css                    groupmate's styles (+ input field, error red)
  socket.js                  WebSocket client for the protocol above
  labels.js                  Lexeme name → readable label (Req 1 classes), fallback to the name
  components/
    TextEditor.jsx           §D 2
    LexemeTable.jsx          §D 3
    SymbolTable.jsx          §D 4
    Console.jsx              §D 6 (output + input field)
```

## Follow-ups (out of scope for the GUI)

- Lexer tags every name as `IDENTIFIER`; Req 1 / the diagram want Variable / Function / Loop Identifier.
- Submission packaging (§E 2): `contributors.txt`, `source code/` folder, `Cheat-gpt_ST-2L.zip`.
