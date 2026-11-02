// §D 3. Rows of { lexeme, classification }: see PLAN.md
export default function LexemeTable() {
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
          <tbody />
        </table>
      </div>
    </section>
  )
}
