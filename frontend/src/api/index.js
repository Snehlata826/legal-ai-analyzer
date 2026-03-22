const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

async function apiFetch(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch (err) {
    throw new Error(
      `Cannot reach the backend server at ${API_BASE_URL}. ` +
      'Make sure it is running: uvicorn app.main:app --reload --port 8001'
    );
  }
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try { const body = await response.json(); detail = body.detail || detail; } catch {}
    throw new Error(detail);
  }
  return response;
}

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiFetch('/upload', { method: 'POST', body: formData });
  return response.json();
};

export const simplifyClauses = async (requestId) => {
  const response = await apiFetch(`/simplify/${requestId}`, { method: 'POST' });
  return response.json();
};

export const askQuestion = async (requestId, question) => {
  const response = await apiFetch('/ask/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ request_id: requestId, question }),
  });
  return response.json();
};

export const evaluateDocument = async (requestId, includeShap = true) => {
  const response = await apiFetch(
    `/evaluate/${requestId}?include_shap=${includeShap}`
  );
  return response.json();
};

export const downloadReport = async (requestId) => {
  const response = await apiFetch(`/report/${requestId}`);
  const blob = await response.blob();
  const url  = window.URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = `legal_analysis_${requestId.substring(0, 8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { document.body.removeChild(a); window.URL.revokeObjectURL(url); }, 100);
};
