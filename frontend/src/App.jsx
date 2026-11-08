import { useState } from 'react'
import TextEditor from './components/TextEditor.jsx'
import LexemeTable from './components/LexemeTable.jsx'
import SymbolTable from './components/SymbolTable.jsx'
import Console from './components/Console.jsx'

// Layout of spec §D parts 1–6. Running: see PLAN.md
export default function App() {
  const [fileName, setFileName] = useState('untitled')
  const [code, setCode] = useState('')

  // §D 1: load the selected file into the editor
  function handleOpen(e) {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      setFileName(file.name)
      setCode(reader.result)
    }
    reader.readAsText(file)
    e.target.value = '' // so re-opening the same file fires onChange again
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1>LOLCODE Interpreter</h1>
        <span className="file-name">{fileName}</span>
        <label className="btn">
          Open File
          <input type="file" accept=".lol,.txt" hidden onChange={handleOpen} />
        </label>
        <button>Execute</button>
      </header>

      <main className="workspace">
        <section className="panel editor-panel">
          <div className="panel-title">Text Editor</div>
          <TextEditor code={code} onChange={setCode} />
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
