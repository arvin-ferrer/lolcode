import { useState } from 'react'
import TextEditor from './components/TextEditor.jsx'
import LexemeTable from './components/LexemeTable.jsx'
import SymbolTable from './components/SymbolTable.jsx'
import Console from './components/Console.jsx'

export default function App() {
  const [fileName, setFileName] = useState('untitled')
  const [code, setCode] = useState('')

  const [lexemes, setLexemes] = useState([])
  const [symbols, setSymbols] = useState([])
  const [output, setOutput] = useState('')
  const [error, setError] = useState(null)
  const [hasRun, setHasRun] = useState(false)
  const [running, setRunning] = useState(false)

  function clearResults() {
    setLexemes([])
    setSymbols([])
    setOutput('')
    setError(null)
    setHasRun(false)
  }

  // read a .lol file from the user's computer into the editor
  function handleOpen(e) {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      setFileName(file.name)
      setCode(reader.result)
      clearResults()
    }
    reader.readAsText(file)
    e.target.value = ''
  }

  // POST /api/run returns { lexemes, symbols, output, error }
  async function handleExecute() {
    setRunning(true)
    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({ code }),
      })
      const result = await res.json()
      if (!res.ok) throw new Error(result.error)

        setLexemes(result.lexemes)
        setSymbols(result.symbols)
        setOutput(result.output)
        setError(result.error)
        setHasRun(true)
    } catch (err) {
      setHasRun(true)
      setError({
        kind: 'Connection error',
      })
    } finally {
      setRunning(false)
    }
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
        <button onClick={handleExecute} disabled={running}>
          {running ? 'Running...' : 'Execute'}
        </button>
      </header>
 
      <main className="workspace">
        <section className="panel editor-panel">
          <div className="panel-title">Text Editor</div>
          <TextEditor code={code} onChange={setCode} />
        </section>
 
        <div className="tables">
          <LexemeTable lexemes={lexemes} />
          <SymbolTable symbols={symbols} />
        </div>
 
        <Console output={output} error={error} hasRun={hasRun} />
      </main>
    </div>
  )
}
