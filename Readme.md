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

CLI: `python main.py` runs `example.lol`.

## Develop

```
python server.py            # backend on :8000
cd frontend && npm run dev  # frontend on :5173, proxies /api and /ws to :8000
```
