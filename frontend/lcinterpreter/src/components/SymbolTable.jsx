function formatValue(value) {
  if (value === null || value === undefined) return 'NOOB'
  if (value === true) return 'WIN'
  if (value === false) return 'FAIL'
  if (typeof value === 'string') return `"${value}"`
  return String(value)
}

// Shows every variable after the program has finished, with its value and type.
export default function SymbolTable({ symbols }) {
  return (
    <section className="panel table-panel">
      <div className="panel-title">
        <span>Symbol table</span>
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Identifier</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            {symbols.map((s) => (
              <tr key={s.name}>
                <td className="mono">{s.name}</td>
                <td className="mono">{formatValue(s.value)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
