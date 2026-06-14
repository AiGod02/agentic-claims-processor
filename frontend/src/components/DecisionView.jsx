export default function DecisionView({ result, onViewTrace }) {
  const decision = result.decision
  const badgeClass = decision ? `badge badge-${decision.toLowerCase()}` : 'badge'
  const isRejected = decision === 'REJECTED'
  const isBlocking = !decision && result.reason

  const bd = result.financial_breakdown || {}

  return (
    <div style={{ marginTop: 16 }}>
      {/* Degraded warning banner */}
      {result.degraded && (
        <div className="alert alert-warning">
          <span>⚠️</span>
          <div>
            <strong>Pipeline ran in degraded mode.</strong> Failed agents: {result.failed_agents?.join(', ') || 'unknown'}.
            Manual review is recommended.
          </div>
        </div>
      )}

      {/* Blocking error (TC001-TC003) */}
      {isBlocking && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="alert alert-error" style={{ margin: 0 }}>
            <span>🚫</span>
            <div>
              <strong>Document Issue — Claim Not Processed</strong>
              <div style={{ marginTop: 8, whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                {result.reason}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Decision card */}
      {decision && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="decision-header">
            <div>
              <div className={badgeClass}>
                {decision === 'APPROVED' && '✅'}
                {decision === 'PARTIAL' && '⚡'}
                {decision === 'REJECTED' && '❌'}
                {decision === 'MANUAL_REVIEW' && '👁️'}
                {decision}
              </div>
              <div className={`decision-amount ${isRejected ? 'rejected' : ''}`} style={{ marginTop: 12 }}>
                ₹{(result.approved_amount || 0).toLocaleString('en-IN')}
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 4 }}>
                of ₹{result.claimed_amount.toLocaleString('en-IN')} claimed
              </div>
            </div>
            <button className="btn btn-secondary" onClick={onViewTrace}>
              📊 View Full Trace
            </button>
          </div>

          {/* Stats */}
          <div className="stat-grid">
            <div className="stat-card">
              <div className="label">Claim ID</div>
              <div className="value" style={{ fontSize: 14, fontFamily: 'monospace' }}>{result.claim_id}</div>
            </div>
            <div className="stat-card">
              <div className="label">Confidence Score</div>
              <div className="value">{(result.confidence_score * 100).toFixed(1)}%</div>
              <div className="confidence-bar">
                <div
                  className={`fill ${result.confidence_score > 0.8 ? 'high' : result.confidence_score > 0.5 ? 'medium' : 'low'}`}
                  style={{ width: `${result.confidence_score * 100}%` }}
                />
              </div>
            </div>
            <div className="stat-card">
              <div className="label">Pipeline</div>
              <div className="value" style={{ fontSize: 12, fontFamily: 'monospace' }}>
                {result.graph_path?.join(' → ') || 'N/A'}
              </div>
            </div>
          </div>

          {/* Reason */}
          <div className="card" style={{ background: 'var(--bg-glass)', marginBottom: 20 }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
              Decision Reason
            </div>
            <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7, fontSize: 14, color: 'var(--text-secondary)' }}>
              {result.reason}
            </div>
          </div>

          {/* Financial breakdown */}
          {Object.keys(bd).length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>💰 Financial Breakdown</h3>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th style={{ textAlign: 'right' }}>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {bd.claimed != null && <tr><td>Claimed Amount</td><td style={{ textAlign: 'right' }}>₹{bd.claimed?.toLocaleString('en-IN')}</td></tr>}
                  {bd.network_discount > 0 && <tr><td>Network Discount</td><td style={{ textAlign: 'right', color: 'var(--green)' }}>-₹{bd.network_discount?.toLocaleString('en-IN')}</td></tr>}
                  {bd.post_discount != null && bd.network_discount > 0 && <tr><td>After Discount</td><td style={{ textAlign: 'right' }}>₹{bd.post_discount?.toLocaleString('en-IN')}</td></tr>}
                  {bd.copay > 0 && <tr><td>Co-pay Deduction</td><td style={{ textAlign: 'right', color: 'var(--amber)' }}>-₹{bd.copay?.toLocaleString('en-IN')}</td></tr>}
                  <tr style={{ fontWeight: 700 }}><td>Approved Amount</td><td style={{ textAlign: 'right', color: 'var(--green)' }}>₹{bd.approved?.toLocaleString('en-IN')}</td></tr>
                </tbody>
              </table>
            </div>
          )}

          {/* Line items */}
          {result.line_items?.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>📝 Line Items</h3>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Description</th>
                    <th style={{ textAlign: 'right' }}>Claimed</th>
                    <th style={{ textAlign: 'right' }}>Approved</th>
                    <th>Status</th>
                    <th>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {result.line_items.map((li, i) => (
                    <tr key={i}>
                      <td>{li.description}</td>
                      <td style={{ textAlign: 'right' }}>₹{li.claimed_amount?.toLocaleString('en-IN')}</td>
                      <td style={{ textAlign: 'right' }}>₹{li.approved_amount?.toLocaleString('en-IN')}</td>
                      <td className={li.status === 'APPROVED' ? 'status-approved' : 'status-rejected'}>
                        {li.status}
                      </td>
                      <td style={{ color: 'var(--text-muted)' }}>{li.reason || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Rejection reasons */}
          {result.rejection_reasons?.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--red)' }}>❌ Rejection Reasons</h3>
              {result.rejection_reasons.map((r, i) => (
                <div key={i} className="alert alert-error" style={{ marginBottom: 8 }}>
                  <span>•</span>
                  <div>{r}</div>
                </div>
              ))}
            </div>
          )}

          {/* Fraud signals */}
          {result.fraud_signals?.length > 0 && (
            <div>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--orange)' }}>🚨 Fraud Signals</h3>
              {result.fraud_signals.map((s, i) => (
                <div key={i} className="alert alert-warning" style={{ marginBottom: 8 }}>
                  <span>🔍</span>
                  <div>{s}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
