import { useRef } from 'react'

export default function TextEditor({ code, onChange }) {
  const gutterRef = useRef(null)
  const lineCount = code.split('\n').length

  const syncScroll = (e) => {
    gutterRef.current.scrollTop = e.target.scrollTop
  }

  const handleKeyDown = (e) => {
    if (e.key !== 'Tab') return
    e.preventDefault()
    e.target.setRangeText('    ', e.target.selectionStart, e.target.selectionEnd, 'end')
    onChange(e.target.value)
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
        aria-label="LOLCODE source"
        value={code}
        onChange={(e) => onChange(e.target.value)}
        onScroll={syncScroll}
        onKeyDown={handleKeyDown}
        spellCheck={false}
      />
    </div>
  )
}
