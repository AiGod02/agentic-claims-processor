import { useState } from 'react'
import ClaimForm from './components/ClaimForm'
import DecisionView from './components/DecisionView'
import TraceViewer from './components/TraceViewer'
import GraphVisualizer from './components/GraphVisualizer'

function App() {
  const [view, setView] = useState('form') // form | decision | trace
  const [result, setResult] = useState(null)

  const handleResult = (data) => {
    setResult(data)
    setView('decision')
  }

  const handleBack = () => {
    setView('form')
    setResult(null)
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo">P</div>
        <div>
          <h1>Plum Claims Processor</h1>
          <div className="subtitle">Multi-Agent Health Insurance Claims Processing System</div>
        </div>
      </header>

      {view === 'form' && (
        <ClaimForm onResult={handleResult} />
      )}

      {view === 'decision' && result && (
        <>
          <button className="btn-back" onClick={handleBack}>← Back to New Claim</button>
          <DecisionView result={result} onViewTrace={() => setView('trace')} />
          <div style={{ marginTop: 32 }}>
            <GraphVisualizer graphPath={result.graph_path} trace={result.trace} />
          </div>
        </>
      )}

      {view === 'trace' && result && (
        <>
          <button className="btn-back" onClick={() => setView('decision')}>← Back to Decision</button>
          <TraceViewer result={result} />
        </>
      )}
    </div>
  )
}

export default App
