/**
 * Axios API client for communicating with the LexIndia FastAPI backend.
 * Configures base URL, timeouts, and error handling.
 */

import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "https://lex-india-backend.onrender.com/api",
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
  draftable?: boolean;
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

export interface DraftGenerateResponse {
  document_type: string;
  draft_text: string;
  language: string;
  disclaimer: string;
}

export async function queryLaws(
  issue: string,
  language: string,
  mode: "citizen" | "lawyer" = "citizen"
): Promise<QueryResponse> {
  const response = await api.post<QueryResponse>("/query", {
    issue,
    language,
    mode,
  });
  
  // Fallback for unexpected response structures (e.g. during partial Lawyer Mode implementation)
  const data = response.data;
  if (!data.laws && (data as any).applicable_sections) {
    data.laws = (data as any).applicable_sections;
  }
  if (!data.laws) {
    data.laws = [];
  }
  
  return data;

}

export async function browseLaws(params: {
  act_code?: string;
  search?: string;
  severity?: string;
  page?: number;
  per_page?: number;
  language?: string;
}): Promise<LawListResponse> {
  const response = await api.get<LawListResponse>("/laws", { params });
  return response.data;
}

export async function generateDraft(payload: any): Promise<DraftGenerateResponse> {
  const response = await api.post<DraftGenerateResponse>("/draft/generate", payload);
  return response.data;
}

export async function exportDraftPdf(payload: {
  document_type: string;
  draft_text: string;
  title?: string;
}): Promise<Blob> {
  const response = await api.post("/draft/export", payload, {
    responseType: "blob",
  });
  return response.data;
}

export async function healthCheck(): Promise<any> {
  const response = await api.get("/health");
  return response.data;
}

// ── Court Judgments API ──────────────────────────────────────────────────

export interface JudgmentCard {
  title: string;
  court: string;
  date: string;
  snippet: string;
  doc_id: string;
  url: string;
}

export interface JudgmentSearchResponse {
  query: string;
  total_found: number;
  page: number;
  judgments: JudgmentCard[];
}

export interface SimilarCasesResponse {
  query: string;
  cases: JudgmentCard[];
}

export interface SingleOutcome {
  doc_id: string;
  outcome: "petitioner_won" | "respondent_won" | "partial" | "unclear";
  petitioner_type: string;
  respondent_type: string;
  key_reason: string;
}

export interface OutcomeAnalysisResponse {
  total_cases: number;
  petitioner_wins: number;
  respondent_wins: number;
  partial: number;
  unclear: number;
  win_percentage: number;
  favour_label: string;
  outcomes: SingleOutcome[];
}

export async function searchJudgments(params: {
  query: string;
  language?: string;
  mode?: "citizen" | "lawyer";
  court?: string;
  category?: string;
  page?: number;
}): Promise<JudgmentSearchResponse> {
  const response = await api.post<JudgmentSearchResponse>("/judgments/search", {
    query: params.query,
    language: params.language || "en",
    mode: params.mode || "citizen",
    court: params.court || null,
    category: params.category || null,
    page: params.page || 0,
  });
  return response.data;
}

export async function getSimilarCases(
  query: string,
  mode: "citizen" | "lawyer" = "citizen"
): Promise<SimilarCasesResponse> {
  const response = await api.get<SimilarCasesResponse>("/judgments/similar", {
    params: { query, mode },
  });
  return response.data;
}

export async function getOutcomeAnalysis(
  query: string,
  docIds: string[]
): Promise<OutcomeAnalysisResponse> {
  const response = await api.post<OutcomeAnalysisResponse>(
    "/judgments/outcome-analysis",
    { query, doc_ids: docIds }
  );
  return response.data;
}

export default api;
