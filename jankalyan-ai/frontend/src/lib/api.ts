import {
  CitizenProfile,
  EligibilityMatchResult,
  AgentExecutionTraceStep,
  SchemeDefinition,
  DocumentCategoryKey,
  DocumentOCRResult,
  StoredDocumentEvidence,
} from "../types";

const API_BASE = "/api";

export async function processIntake(text: string, language: string): Promise<{ profile: CitizenProfile; extractionMode: string; isMock?: boolean; defaultedFields?: string[] }> {
  const res = await fetch(`${API_BASE}/intake`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language })
  });
  if (!res.ok) {
    let message = `Profile extraction failed (${res.status}).`;
    try {
      const errorBody = await res.json();
      if (typeof errorBody.detail === "string") message = errorBody.detail;
    } catch {
      // Keep the HTTP status message when the server does not return JSON.
    }
    throw new Error(message);
  }
  return await res.json();
}

export async function runOrchestrator(
  profile: CitizenProfile,
  documentEvidence: StoredDocumentEvidence[] = [],
): Promise<{
  matches: EligibilityMatchResult[];
  nearMisses: EligibilityMatchResult[];
  manualReviewSchemes: SchemeDefinition[];
  trace: AgentExecutionTraceStep[];
  isMock?: boolean;
  defaultedFields?: string[];
}> {
  const res = await fetch(`${API_BASE}/orchestrator`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      profile,
      documentEvidence: documentEvidence.map(({ documentId, category, validityStatus, extracted, savedAt }) => ({
        documentId,
        category,
        validityStatus,
        extracted,
        savedAt,
      })),
    })
  });
  if (!res.ok) {
    let message = `Scheme discovery failed (${res.status}).`;
    try {
      const errorBody = await res.json();
      if (typeof errorBody.detail === "string") message = errorBody.detail;
    } catch {
      // Keep the HTTP status message when the server does not return JSON.
    }
    throw new Error(message);
  }
  return await res.json();
}

export async function runDocumentOCR(
  file: File,
  category: DocumentCategoryKey,
): Promise<DocumentOCRResult> {
  const body = new FormData();
  body.append("file", file);
  body.append("category", category);

  const response = await fetch(`${API_BASE}/document-ocr`, { method: "POST", body });
  if (!response.ok) {
    let message = `Document OCR failed (${response.status}).`;
    try {
      const errorBody = await response.json();
      if (typeof errorBody.detail === "string") message = errorBody.detail;
    } catch {
      // Keep the HTTP status message when the server does not return JSON.
    }
    throw new Error(message);
  }
  return (await response.json()) as DocumentOCRResult;
}

export async function checkTavilyUpdates(query: string, schemeId?: string) {
  try {
    const res = await fetch(`${API_BASE}/tavily-search?query=${encodeURIComponent(query)}&schemeId=${encodeURIComponent(schemeId || "")}`);
    if (res.ok) return await res.json();
  } catch (e) {}

  return {
    query,
    results: [],
    isMock: true,
    note: "Live government search is unavailable. No substitute results were generated.",
    verifiedAt: new Date().toISOString()
  };
}

export interface TavilySearchResult {
  title?: string;
  url?: string;
  content?: string;
  snippet?: string;
  [key: string]: any;
}

export interface TavilySearchResponse {
  query: string;
  results: TavilySearchResult[];
  isMock: boolean;
  note: string;
  verifiedAt: string;
}

export async function fetchWebResults(query: string): Promise<TavilySearchResponse> {
  try {
    const res = await fetch(`${API_BASE}/tavily-search?query=${encodeURIComponent(query)}`);
    if (res.ok) return (await res.json()) as TavilySearchResponse;
  } catch (err) {}

  return {
    query,
    results: [],
    isMock: true,
    note: "Live web results are unavailable right now.",
    verifiedAt: new Date().toISOString()
  };
}


export async function askPolicyQuestion(question: string, schemeId?: string, language: string = "en") {
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, schemeId, language })
    });
    if (res.ok) return await res.json();
  } catch (e) {}

  return {
    answer: "The assistant is unavailable right now. Please confirm details on the official portal.",
    sources: [],
    mode: "UNAVAILABLE",
    isMock: true
  };
}
