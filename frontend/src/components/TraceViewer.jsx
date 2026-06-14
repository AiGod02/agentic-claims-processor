import { useState } from 'react'

export default function TraceViewer({ result }) {
  const trace = result.trace
  const steps = trace?.steps || []
  const [expanded, setExpanded] = useState({})
  const [showJson, setShowJson] = useState(false)

  const toggle = (idx) => {
    setExpanded(prev => ({ ...prev, [idx]: !prev[idx] }))
  }

  const statusBadge = (status) => {
    const map = {
      PASSED: { bg: 'var(--green-bg)', color: 'var(--green)', icon: '✅' },
      FAILED: { bg: 'var(--red-bg)', color: 'var(--red)', icon: '❌' },
      WARNING: { bg: 'var(--amber-bg)', color: 'var(--amber)', icon: '⚠️' },
      DEGRADED: { bg: 'var(--orange-bg)', color: 'var(--orange)', icon: '🔶' },
      SKIPPED: { bg: 'rgba(100,116,139,0.1)', color: 'var(--text-muted)', icon: '⏭️' },
    }
    const s = map[status] || map.SKIPPED
    return (
      <span className="badge" style={{ background: s.bg, color: s.color, border: 'none', fontSize: 11 }}>
        {s.icon} {status}
      </span>
    )
  }

  const copyTrace = () => {
    const text = trace?.to_readable || JSON.stringify(trace, null, 2)
    navigator.clipboard?.writeText(typeof text === 'string' ? text : JSON.stringify(trace, null, 2))
  }

  return (
    <div style={{ marginTop: 16 }}>
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div className="icon" style={{ background: 'rgba(139, 92, 246, 0.1)', color: 'var(--accent-purple)' }}>📊</div>
          <h2>Execution Trace</h2>
        </div>

        {/* Pipeline visualization */}
        <div className="trace-pipeline">
          {(trace?.graph_path || []).map((node, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <div className="trace-node active">{node}</div>
              {i < (trace?.graph_path?.length || 0) - 1 && <span className="trace-arrow">→</span>}
            </div>
          ))}
        </div>

        {/* Confidence timeline */}
        {trace?.confidence_log?.length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>📈 Confidence Timeline</h3>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 16, height: 80, padding: '0 8px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                <div style={{
                  width: 40,
                  height: `${trace.initial_confidence * 70}px`,
                  background: 'linear-gradient(to top, var(--accent-blue), var(--accent-cyan))',
                  borderRadius: 4,
                }} />
                <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Start</span>
                <span style={{ fontSize: 11, fontWeight: 600 }}>{trace.initial_confidence.toFixed(2)}</span>
              </div>
              {trace.confidence_log.map((entry, i) => (
                <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                  <div style={{
                    width: 40,
                    height: `${entry.new_confidence * 70}px`,
                    background: entry.delta < 0
                      ? 'linear-gradient(to top, var(--red), var(--orange))'
                      : 'linear-gradient(to top, var(--green), var(--accent-cyan))',
                    borderRadius: 4,
                  }} />
                  <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{entry.after}</span>
                  <span style={{ fontSize: 11, fontWeight: 600, color: entry.delta < 0 ? 'var(--red)' : 'var(--green)' }}>
                    {entry.delta > 0 ? '+' : ''}{entry.delta.toFixed(2)}
                  </span>
                </div>
              ))}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                <div style={{
                  width: 40,
                  height: `${trace.final_confidence * 70}px`,
                  background: 'linear-gradient(to top, var(--accent-purple), var(--accent-blue))',
                  borderRadius: 4,
                }} />
                <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Final</span>
                <span style={{ fontSize: 11, fontWeight: 600 }}>{trace.final_confidence.toFixed(2)}</span>
              </div>
            </div>
          </div>
        )}

        {/* Agent steps accordion */}
        <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>🔍 Agent Steps</h3>
        {steps.map((step, idx) => (
          <div className="accordion" key={idx}>
            <div className="accordion-header" onClick={() => toggle(idx)}>
              <div className="left">
                {statusBadge(step.status)}
                <span className="agent-name">{step.agent_name}</span>
                <span className="node-name">[{step.node_name}]</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <span className="duration">{step.duration_ms?.toFixed(0)}ms</span>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{expanded[idx] ? '▲' : '▼'}</span>
              </div>
            </div>
            {expanded[idx] && (
              <div className="accordion-body">
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>Input</div>
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{step.input_summary}</div>
                </div>
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>Output</div>
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{step.output_summary}</div>
                </div>

                {step.confidence_impact !== 0 && (
                  <div style={{ marginBottom: 16, fontSize: 13 }}>
                    <span style={{ color: 'var(--text-muted)' }}>Confidence impact: </span>
                    <span style={{ color: step.confidence_impact < 0 ? 'var(--red)' : 'var(--green)', fontWeight: 600 }}>
                      {step.confidence_impact > 0 ? '+' : ''}{step.confidence_impact.toFixed(2)}
                    </span>
                  </div>
                )}

                {/* Checks */}
                {step.checks_performed?.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Checks Performed</div>
                    {step.checks_performed.map((c, ci) => (
                      <div className="check-item" key={ci}>
                        <span className={`check-icon ${c.passed ? 'pass' : 'fail'}`}>
                          {c.passed ? '✓' : '✗'}
                        </span>
                        <div>
                          <div style={{ fontWeight: 500 }}>{c.check_name}</div>
                          <div className="check-detail">{c.detail}</div>
                          {c.rule_source && <div className="check-source">📖 {c.rule_source}</div>}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* LLM calls */}
                {step.llm_calls?.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>LLM Calls</div>
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Model</th>
                          <th>Latency</th>
                          <th>Tokens</th>
                        </tr>
                      </thead>
                      <tbody>
                        {step.llm_calls.map((call, li) => (
                          <tr key={li}>
                            <td>{call.model || 'unknown'}</td>
                            <td>{call.latency_ms?.toFixed(0)}ms</td>
                            <td>{call.prompt_tokens || '—'} / {call.completion_tokens || '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Errors */}
                {step.errors?.length > 0 && (
                  <div>
                    <div style={{ fontSize: 12, color: 'var(--red)', marginBottom: 8 }}>Errors</div>
                    {step.errors.map((err, ei) => (
                      <div key={ei} className="alert alert-error" style={{ marginBottom: 4, fontSize: 12 }}>
                        {err}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {/* Actions */}
        <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
          <button className="btn btn-secondary" onClick={() => setShowJson(!showJson)}>
            {showJson ? '📋 Hide' : '📋 Show'} Raw JSON
          </button>
          <button className="btn btn-secondary" onClick={copyTrace}>
            📎 Copy Trace
          </button>
        </div>

        {showJson && (
          <div className="json-block" style={{ marginTop: 16 }}>
            {JSON.stringify(trace, null, 2)}
          </div>
        )}
      </div>
    </div>
  )
}
