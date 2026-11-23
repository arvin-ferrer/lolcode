# LOLCODE Interpreter — Cheat-gpt (ST-2L)

## Requirements

- Python 3.12+
- Node.js 20+ (only to build or develop the frontend)

## Install

Windows:

```
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
```

Linux/macOS: same, with `python3 -m venv .venv` and `source .venv/bin/activate`.

## Run

GUI: `python server.py`, then open http://localhost:8000.

CLI: `python main.py <filename>.lol` runs `<filename>.lol`.

## Develop

```
python server.py            # backend on :8000
cd frontend && npm run dev  # frontend on :5173, proxies /api and /ws to :8000
```

## Bonus Features implemented

| Bonus feature | Status |
|---|---|
| Soft-line/command breaks (`,`) | Implemented |
| Line continuation (`...`) | Implemented |
| `MEBBE` / else-if clauses | Implemented |
| Loop nesting | Implemented |
| If-else nesting | Implemented |
| Switch nesting | Implemented |
| Nesting of different flow-control statements | Implemented |
| Special characters in a YARN (`:)`, `:>`, etc.) | Implemented |
| Suppress the newline with `!` after `VISIBLE` | Implemented |
| Arrays | Not covered |

## Special Characters in a YARN

Escape sequences supported inside `YARN` string literals:

| Escape Sequence | Equivalent | Description | Example | Output |
|---|---|---|---|---|
| `:)` | `\n` | Newline | `"Hi:)There"` | `Hi` *(new line)* `There` |
| `:>` | `\t` | Tab | `"A:>B"` | `A` *(tab)* `B` |
| `:o` or `:O` | `\a` | Bell (alert) | `"Done:o"` | `Done` *(bell)* |
| `:"` | `"` | Literal double quote | `"Say :"Hi:""` | `Say "Hi"` |
| `::` | `:` | Literal colon | `"Ratio:: 1::2"` | `Ratio: 1:2` |
| `:(<hex>)` | Unicode char | Character from hexadecimal code point | `":(41) :(263A)"` | `A ☺` |

Unrecognized escape sequences and out-of-range hex code points are left as-is.
