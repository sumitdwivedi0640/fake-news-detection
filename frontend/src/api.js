import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";
export const api = axios.create({
  baseURL: BASE_URL,
  // LLM + evidence retrieval can take longer on local setups.
  timeout: 120000
});

export async function analyzeNews(news) {
  const response = await api.post("/analyze", { news });
  return response.data;
}

export async function analyzeUrl(url) {
  const response = await api.post("/analyze_url", { url });
  return response.data;
}
