import axios from "axios";

// In dev, Vite proxies "/api" -> http://localhost:8000 (see vite.config.js).
// Override with VITE_API_BASE_URL for other environments.
const baseURL = import.meta.env.VITE_API_BASE_URL || "/api";

const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${import.meta.env.VITE_API_KEY || "sk-medical-his-dev-12345"}`,
  },
  timeout: 90000,
});

/**
 * Normalise an axios error into a human-readable message, preferring the
 * backend's structured error envelope ({ error: { message, details } }).
 */
export function apiErrorMessage(err) {
  const data = err?.response?.data;
  if (data?.error?.message) {
    const details = data.error.details
      ?.map((d) => (d.field ? `${d.field}: ${d.error}` : d.error))
      .filter(Boolean);
    return details?.length
      ? `${data.error.message} (${details.join("; ")})`
      : data.error.message;
  }
  if (err?.code === "ECONNABORTED") return "Request timed out.";
  if (err?.message === "Network Error") return "Cannot reach the API. Is the backend running?";
  return err?.message || "Unexpected error";
}

export const healthAPI = {
  check: () => api.get("/health"),
};

export const patientAPI = {
  create: (data) => api.post("/patients", data),
  get: (id) => api.get(`/patients/${id}`),
  list: (params) => api.get("/patients", { params }),
};

export const consultationAPI = {
  create: (data) => api.post("/consultations", data),
  get: (id) => api.get(`/consultations/detail/${id}`),
  history: (patientId, params) => api.get(`/consultations/${patientId}`, { params }),
};

export const knowledgeAPI = {
  search: (data) => api.post("/knowledge/search", data),
  stats: () => api.get("/knowledge/stats"),
};

export default api;
