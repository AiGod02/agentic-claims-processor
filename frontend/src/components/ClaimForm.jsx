import { useState, useRef } from 'react'
import { submitClaim } from '../api/client'

const MEMBERS = [
  { id: 'EMP001', name: 'Rajesh Kumar' },
  { id: 'EMP002', name: 'Priya Singh' },
  { id: 'EMP003', name: 'Amit Verma' },
  { id: 'EMP004', name: 'Sneha Reddy' },
  { id: 'EMP005', name: 'Vikram Joshi' },
  { id: 'EMP006', name: 'Kavita Nair' },
  { id: 'EMP007', name: 'Suresh Patil' },
  { id: 'EMP008', name: 'Ravi Menon' },
  { id: 'EMP009', name: 'Anita Desai' },
  { id: 'EMP010', name: 'Deepak Shah' },
]

const CATEGORIES = [
  'CONSULTATION', 'DIAGNOSTIC', 'PHARMACY',
  'DENTAL', 'VISION', 'ALTERNATIVE_MEDICINE'
]

export default function ClaimForm({ onResult }) {
  const [form, setForm] = useState({
    member_id: 'EMP001',
    policy_id: 'PLUM_GHI_2024',
    claim_category: 'CONSULTATION',
    treatment_date: '',
    claimed_amount: '',
    hospital_name: '',
    ytd_claims_amount: 0,
    simulate_component_failure: false,
  })
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const fileRef = useRef()

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm(prev => ({ ...prev, [e.target.name]: value }))
  }

  const handleFiles = async (e) => {
    const newFiles = Array.from(e.target.files)
    const withBase64 = await Promise.all(
      newFiles.map(file => new Promise((resolve) => {
        const reader = new FileReader()
        reader.onload = () => {
          const base64 = reader.result.split(',')[1]
          resolve({
            file_id: `F_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
            file_name: file.name,
            file_content_base64: base64,
          })
        }
        reader.readAsDataURL(file)
      }))
    )
    setFiles(prev => [...prev, ...withBase64])
  }

  const removeFile = (idx) => {
    setFiles(prev => prev.filter((_, i) => i !== idx))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const submission = {
        ...form,
        claimed_amount: parseFloat(form.claimed_amount),
        ytd_claims_amount: parseFloat(form.ytd_claims_amount || 0),
        documents: files,
      }
      const result = await submitClaim(submission)
      onResult(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {loading && (
        <div className="spinner-overlay">
          <div className="spinner"></div>
          <div className="spinner-text">Processing claim through multi-agent pipeline...</div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <div className="icon" style={{ background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-blue)' }}>📋</div>
          <h2>Submit Insurance Claim</h2>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>⚠️</span>
            <div>{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label>Member</label>
              <select name="member_id" value={form.member_id} onChange={handleChange}>
                {MEMBERS.map(m => (
                  <option key={m.id} value={m.id}>{m.id} — {m.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Category</label>
              <select name="claim_category" value={form.claim_category} onChange={handleChange}>
                {CATEGORIES.map(c => (
                  <option key={c} value={c}>{c.replace('_', ' ')}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Treatment Date</label>
              <input type="date" name="treatment_date" value={form.treatment_date}
                     onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label>Claimed Amount (₹)</label>
              <input type="number" name="claimed_amount" value={form.claimed_amount}
                     onChange={handleChange} placeholder="e.g. 1500" required min="1" step="0.01" />
            </div>

            <div className="form-group">
              <label>Hospital Name (Optional)</label>
              <input type="text" name="hospital_name" value={form.hospital_name}
                     onChange={handleChange} placeholder="e.g. Apollo Hospitals" />
            </div>

            <div className="form-group">
              <label>YTD Claims Amount (₹)</label>
              <input type="number" name="ytd_claims_amount" value={form.ytd_claims_amount}
                     onChange={handleChange} placeholder="0" min="0" step="0.01" />
            </div>

            <div className="form-group" style={{ display: 'flex', alignItems: 'center', marginTop: 'auto', paddingBottom: 8 }}>
              <input type="checkbox" id="simulate_component_failure" name="simulate_component_failure" 
                     checked={form.simulate_component_failure} onChange={handleChange} 
                     style={{ width: 'auto', marginRight: 10, cursor: 'pointer', height: '1.2rem' }} />
              <label htmlFor="simulate_component_failure" style={{ marginBottom: 0, cursor: 'pointer', userSelect: 'none', fontWeight: 'normal' }}>
                Simulate Component Failure
              </label>
            </div>

            <div className="form-group full-width">
              <label>Documents</label>
              <div className="file-upload-zone" onClick={() => fileRef.current?.click()}>
                <div className="icon">📄</div>
                <div className="text">Click to upload documents</div>
                <div className="subtext">Supports JPG, PNG, PDF — Prescriptions, Bills, Reports</div>
              </div>
              <input ref={fileRef} type="file" multiple accept=".jpg,.jpeg,.png,.pdf"
                     onChange={handleFiles} style={{ display: 'none' }} />
              {files.length > 0 && (
                <div className="file-list">
                  {files.map((f, i) => (
                    <div key={i} className="file-chip">
                      📎 {f.file_name}
                      <span className="remove" onClick={() => removeFile(i)}>✕</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div style={{ marginTop: 28, display: 'flex', justifyContent: 'flex-end' }}>
            <button type="submit" className="btn btn-primary"
                    disabled={loading || !form.treatment_date || !form.claimed_amount}>
              🚀 Submit Claim
            </button>
          </div>
        </form>
      </div>
    </>
  )
}
