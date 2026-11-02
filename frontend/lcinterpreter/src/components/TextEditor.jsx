import { useRef } from 'react'

// A plain text area with a line-number column beside it.
export default function Editor({ code, onChange }) {
  const gutterRef = useRef(null)
  const lineCount = code.split('\n').length

  // keep the line numbers lined up while the text scrolls
  const syncScroll = (e) => {
    gutterRef.current.scrollTop = e.target.scrollTop
  }

  // pressing Tab inserts spaces instead of leaving the editor
  const handleKeyDown = (e) => {
    if (e.key !== 'Tab') return
    e.preventDefault()
    const { selectionStart, selectionEnd } = e.target
    const next = code.slice(0, selectionStart) + '    ' + code.slice(selectionEnd)
    onChange(next)
    requestAnimationFrame(() => {
      e.target.selectionStart = e.target.selectionEnd = selectionStart + 4
    })
  }

  return (
    <div className="editor">
      <div className="gutter" ref={gutterRef} aria-hidden="true">
        {Array.from({ length: lineCount }, (_, i) => (
          <div key={i}>{i + 1}</div>
        ))}
      </div>
      <textarea
        className="code-input"
        value={code}
        onChange={(e) => onChange(e.target.value)}
        onScroll={syncScroll}
        onKeyDown={handleKeyDown}
        spellCheck={false}
      />
    </div>
  )
}
