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
  timeout: 60000,
});

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
  history: (patientId, params) =>
    api.get(`/consultations/${patientId}`, { params }),
};

export default api;
