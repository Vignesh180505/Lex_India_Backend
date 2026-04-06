/**
 * Axios API client for communicating with the LexIndia FastAPI backend.
 * Configures base URL, timeouts, and error handling.
 */

import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api",
  timeout: 90000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ── Response interceptor for error handling ─────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error(
        `API Error: ${error.response.status} - ${JSON.stringify(error.response.data)}`
      );
    } else if (error.request) {
      console.error("API Error: No response received");
    } else {
      console.error(`API Error: ${error.message}`);
    }
    return Promise.reject(error);
  }
);

// ── API Functions ───────────────────────────────────────────────────────

export interface LawResult {
  section_id: string;
  act_name: string;
  act_code?: string;
  section_number: string;
  section_title: string;
  original_text?: string;
  section_text?: string;
  simplified?: string;
  simplified_en?: string;
  severity: "low" | "medium" | "high";
  punishment?: string | null;
  filing_link?: string | null;
  relevance_score?: number;
}

export interface QueryResponse {
  query_id: string;
  detected_language: string;
  ai_summary: string;
  laws: LawResult[];
  response_ms: number;
}

export interface LawListResponse {
  laws: any[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export async function queryLaws(
  issue: string,
  language: string
): Promise<QueryResponse> {
  const response = await api.post<QueryResponse>("/query", {
    issue,
    language,
  });
  return response.data;
}

export async function browseLaws(params: {
  act_code?: string;
  search?: string;
  severity?: string;
  page?: number;
  per_page?: number;
}): Promise<LawListResponse> {
  const response = await api.get<LawListResponse>("/laws", { params });
  return response.data;
}

export async function healthCheck(): Promise<any> {
  const response = await api.get("/health");
  return response.data;
}

export default api;
