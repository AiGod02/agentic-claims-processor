const API_BASE = '/api/v1';

export async function submitClaim(submission) {
  const response = await fetch(`${API_BASE}/claims/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(submission),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export async function getClaim(claimId) {
  const response = await fetch(`${API_BASE}/claims/${claimId}`);
  if (!response.ok) throw new Error(`Claim not found`);
  return response.json();
}

export async function getTrace(claimId) {
  const response = await fetch(`${API_BASE}/claims/${claimId}/trace`);
  if (!response.ok) throw new Error(`Trace not found`);
  return response.json();
}

export async function listClaims() {
  const response = await fetch(`${API_BASE}/claims`);
  if (!response.ok) throw new Error(`Failed to list claims`);
  return response.json();
}
