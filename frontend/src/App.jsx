import TextEditor from './components/TextEditor.jsx'
import LexemeTable from './components/LexemeTable.jsx'
import SymbolTable from './components/SymbolTable.jsx'
import Console from './components/Console.jsx'

// Layout of spec §D parts 1–6. State, file loading and running: see PLAN.md
export default function App() {
  return (
    <div className="app">
      <header className="topbar">
        <h1>LOLCODE Interpreter</h1>
        <span className="file-name">untitled</span>
        <label className="btn">
          Open File
          <input type="file" accept=".lol,.txt" hidden />
        </label>
        <button>Execute</button>
      </header>

      <main className="workspace">
        <section className="panel editor-panel">
          <div className="panel-title">Text Editor</div>
          <TextEditor />
        </section>

        <div className="tables">
          <LexemeTable />
          <SymbolTable />
        </div>

        <Console />
      </main>
    </div>
  )
}
