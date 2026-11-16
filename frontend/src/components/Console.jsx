import { useEffect, useRef } from 'react'

export default function Console({ output = '', error = null, waitingInput = false, onInput }) {
  const bodyRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bodyRef.current.scrollTop = bodyRef.current.scrollHeight
  }, [output, error])

  useEffect(() => {
    if (waitingInput) inputRef.current.focus()
  }, [waitingInput])

  const handleKeyDown = (e) => {
    if (e.key !== 'Enter') return
    onInput(e.target.value)
    e.target.value = ''
  }

  return (
    <section className="panel console">
      <div className="panel-title">
        <span>Output</span>
      </div>
      <div className="console-body" ref={bodyRef}>
        <pre>{output}</pre>
        {error && <pre className="error">{error}</pre>}
      </div>
      <input
        ref={inputRef}
        className="console-input"
        aria-label="Program input"
        placeholder={waitingInput ? 'GIMMEH: type a value and press Enter' : ''}
        disabled={!waitingInput}
        onKeyDown={handleKeyDown}
      />
    </section>
  )
}
