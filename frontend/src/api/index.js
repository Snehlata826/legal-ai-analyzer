/**
 * API client for backend communication
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Upload PDF document
 */
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }

  return response.json();
};

/**
 * Simplify and analyze clauses
 */
export const simplifyClauses = async (requestId) => {
  const response = await fetch(`${API_BASE_URL}/simplify/${requestId}`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Simplification failed');
  }

  return response.json();
};

/**
 * Download PDF report
 */
export const downloadReport = async (requestId) => {
  const response = await fetch(`${API_BASE_URL}/report/${requestId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Report generation failed');
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `legal_analysis_${requestId.substring(0, 8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};
