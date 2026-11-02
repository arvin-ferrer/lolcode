export default function LexemeTable({ lexemes }) {
  return (
    <section className="panel table-panel">
      <div className="panel-title">
        <span>Lexemes</span>
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Lexeme</th>
              <th>Classification</th>
            </tr>
          </thead>
          <tbody>
            {lexemes.map((item, i) => (
              <tr key={i}>
                <td className="mono">{item.lexeme}</td>
                <td><span className="tag">{item.type}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
