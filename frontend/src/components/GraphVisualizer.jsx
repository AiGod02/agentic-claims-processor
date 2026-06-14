export default function GraphVisualizer({ graphPath, trace }) {
  const allNodes = [
    { id: 'document_agent', label: 'Document Agent', x: 200, y: 60, sub: 'Classify → Quality → Extract' },
    { id: 'parallel_agents', label: 'Parallel Agents', x: 200, y: 180, sub: 'Policy + Fraud (async)' },
    { id: 'policy_agent', label: 'Policy Agent', x: 80, y: 220, sub: '12 rule checks', isChild: true },
    { id: 'fraud_agent', label: 'Fraud Agent', x: 320, y: 220, sub: '5 fraud signals', isChild: true },
    { id: 'decision_agent', label: 'Decision Agent', x: 200, y: 340, sub: 'Final synthesis' },
  ]

  const executedSet = new Set(graphPath || [])
  // Also mark sub-agents if parallel_agents executed
  if (executedSet.has('parallel_agents')) {
    executedSet.add('policy_agent')
    executedSet.add('fraud_agent')
  }

  const getNodeTime = (nodeId) => {
    const step = trace?.steps?.find(s => s.node_name === nodeId)
    return step ? `${step.duration_ms?.toFixed(0)}ms` : ''
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="icon" style={{ background: 'rgba(6, 182, 212, 0.1)', color: 'var(--accent-cyan)' }}>🔀</div>
        <h2>LangGraph Execution Path</h2>
      </div>
      <div className="graph-container">
        <svg width="440" height="400" viewBox="0 0 440 400">
          {/* Edges */}
          {/* doc → parallel */}
          <line x1="200" y1="90" x2="200" y2="160" stroke={executedSet.has('parallel_agents') ? '#10b981' : '#334155'} strokeWidth="2" strokeDasharray={executedSet.has('parallel_agents') ? 'none' : '6 3'} />
          <polygon points="196,158 200,168 204,158" fill={executedSet.has('parallel_agents') ? '#10b981' : '#334155'} />

          {/* conditional edge label */}
          {!executedSet.has('parallel_agents') && executedSet.has('document_agent') && (
            <>
              <line x1="300" y1="60" x2="400" y2="60" stroke="#ef4444" strokeWidth="1.5" strokeDasharray="4 3" />
              <text x="350" y="50" textAnchor="middle" fill="#ef4444" fontSize="10" fontWeight="600">EXIT EARLY</text>
            </>
          )}

          {/* parallel → policy */}
          <line x1="180" y1="195" x2="120" y2="210" stroke={executedSet.has('policy_agent') ? '#10b981' : '#334155'} strokeWidth="1.5" />
          {/* parallel → fraud */}
          <line x1="220" y1="195" x2="280" y2="210" stroke={executedSet.has('fraud_agent') ? '#10b981' : '#334155'} strokeWidth="1.5" />

          {/* parallel → decision */}
          <line x1="200" y1="260" x2="200" y2="320" stroke={executedSet.has('decision_agent') ? '#10b981' : '#334155'} strokeWidth="2" strokeDasharray={executedSet.has('decision_agent') ? 'none' : '6 3'} />
          <polygon points="196,318 200,328 204,318" fill={executedSet.has('decision_agent') ? '#10b981' : '#334155'} />

          {/* Nodes */}
          {allNodes.map(node => {
            const active = executedSet.has(node.id)
            const w = node.isChild ? 140 : 180
            const h = node.isChild ? 40 : 50
            const rx = node.isChild ? 6 : 10

            return (
              <g key={node.id}>
                <rect
                  x={node.x - w/2} y={node.y - h/2}
                  width={w} height={h} rx={rx}
                  fill={active ? 'rgba(16, 185, 129, 0.08)' : 'rgba(30, 41, 59, 0.8)'}
                  stroke={active ? '#10b981' : '#334155'}
                  strokeWidth={active ? 2 : 1}
                />
                <text
                  x={node.x} y={node.y - (node.isChild ? 2 : 4)}
                  textAnchor="middle"
                  fill={active ? '#10b981' : '#94a3b8'}
                  fontSize={node.isChild ? 11 : 12}
                  fontWeight="600"
                >
                  {node.label}
                </text>
                {!node.isChild && (
                  <text
                    x={node.x} y={node.y + 12}
                    textAnchor="middle"
                    fill="#64748b"
                    fontSize="9"
                  >
                    {node.sub}
                  </text>
                )}
                {active && getNodeTime(node.id) && (
                  <text
                    x={node.x + w/2 + 6} y={node.y + 4}
                    fill="#10b981"
                    fontSize="10"
                    fontWeight="600"
                  >
                    {getNodeTime(node.id)}
                  </text>
                )}
              </g>
            )
          })}

          {/* END node */}
          <circle cx="200" cy="380" r="14" fill="none" stroke={executedSet.size > 0 ? '#10b981' : '#334155'} strokeWidth="2" />
          <text x="200" y="384" textAnchor="middle" fill={executedSet.size > 0 ? '#10b981' : '#64748b'} fontSize="9" fontWeight="700">END</text>
          <line x1="200" y1="365" x2="200" y2="366" stroke={executedSet.size > 0 ? '#10b981' : '#334155'} strokeWidth="2" />
        </svg>
      </div>
    </div>
  )
}
