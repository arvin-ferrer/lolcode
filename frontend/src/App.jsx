import { useRef, useState } from 'react'
import { run } from './socket.js'
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
  const [running, setRunning] = useState(false)
  const [waitingInput, setWaitingInput] = useState(false)
  const session = useRef(null)

  function handleExecute() {
    setLexemes([])
    setSymbols([])
    setOutput('')
    setError(null)
    setRunning(true)
    session.current = run(code, {
      output: (msg) => setOutput((prev) => prev + msg.text),
      input_request: () => setWaitingInput(true),
      symbols: (msg) => setSymbols(msg.symbols),
      done: (msg) => {
        // a lost connection has no lexemes/symbols: keep what already arrived
        if (msg.lexemes) setLexemes(msg.lexemes)
        if (msg.symbols) setSymbols(msg.symbols)
        setError(msg.error)
        setWaitingInput(false)
        setRunning(false)
      },
    })
  }

  function sendInput(value) {
    session.current.sendInput(value)
    setWaitingInput(false)
  }

  function handleOpen(e) {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      setFileName(file.name)
      setCode(reader.result)
    }
    reader.readAsText(file)
    e.target.value = '' 
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

        <Console output={output} error={error} waitingInput={waitingInput} onInput={sendInput} />
      </main>
    </div>
  )
}
