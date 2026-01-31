import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return axios.post(`${API_BASE}/upload/`, formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
};

export const simplifyDoc = (requestId) => {
  return axios.post(`${API_BASE}/simplify/${requestId}`);
};
