export default function SymbolTable({ symbols = [] }) {
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
            {symbols.map(([name, value]) => (
              <tr key={name}>
                <td className="mono">{name}</td>
                <td className="mono">{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
