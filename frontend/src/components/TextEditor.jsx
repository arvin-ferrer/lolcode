// §D 2. Editable code + line-number gutter. Scroll sync, Tab key: see PLAN.md
export default function TextEditor() {
  return (
    <div className="editor">
      <div className="gutter" aria-hidden="true">
        <div>1</div>
      </div>
      <textarea className="code-input" spellCheck={false} />
    </div>
  )
}
