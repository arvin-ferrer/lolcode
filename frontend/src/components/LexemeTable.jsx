import { getLabel } from '../labels.js'

// Render the list of detected lexemes and their readable classifications
export default function LexemeTable({ lexemes = [] }) {
  // Filter out NEWLINE tokens and split YARN_LITERAL quotes into String Delimiter rows
  const rows = lexemes
    .filter(([, type]) => type !== 'NEWLINE')
    .flatMap(([lexeme, type]) =>
      type === 'YARN_LITERAL' && lexeme.startsWith('"') && lexeme.endsWith('"') && lexeme.length >= 2
        ? [['"', 'String Delimiter'], [lexeme.slice(1, -1), getLabel(type)], ['"', 'String Delimiter']]
        : [[lexeme, getLabel(type)]]
    )

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
            {rows.map(([lexeme, classification], index) => (
              <tr key={index}>
                <td className="mono">{lexeme}</td>
                <td>{classification}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
