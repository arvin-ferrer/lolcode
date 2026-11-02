export default function Console({ output, error, hasRun }) {
  return (
    <section className="panel console">
      <div className="panel-title">
        <span>Output</span>
      </div>
      <div className="console-body">
        {hasRun && !error && output === '' && <span className="empty">(no output)</span>}
        {output && <pre>{output}</pre>}
        {error && (
          <pre className="error">
            {error.kind}: {error.message}
          </pre>
        )}
      </div>
    </section>
  )
}
