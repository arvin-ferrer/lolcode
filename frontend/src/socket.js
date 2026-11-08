// One WebSocket per run, so a restarted server just works on the next Execute.
// Protocol: PLAN.md. `handlers` is keyed by message type: output, input_request, symbols, done.
export function run(code, handlers, url = `ws://${location.host}/ws`) {
  const ws = new WebSocket(url)
  let finished = false

  ws.onopen = () => ws.send(JSON.stringify({ type: 'run', code }))
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data)
    if (msg.type === 'done') {
      finished = true
      ws.close()
    }
    handlers[msg.type]?.(msg)
  }
  // fires after a failed connect too, so this covers "server not running"
  ws.onclose = () => {
    if (!finished) {
      handlers.done?.({ type: 'done', error: 'Lost connection to the interpreter server. Is `python server.py` running?' })
    }
  }

  return { sendInput: (value) => ws.send(JSON.stringify({ type: 'input', value })) }
}
