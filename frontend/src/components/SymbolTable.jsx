// §D 4. Rows of { identifier, value }, updated live: see PLAN.md
export default function SymbolTable() {
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
          <tbody />
        </table>
      </div>
    </section>
  )
}
