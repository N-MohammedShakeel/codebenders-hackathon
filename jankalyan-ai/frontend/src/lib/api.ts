import {
  CitizenProfile,
  EligibilityMatchResult,
  AgentExecutionTraceStep,
  SchemeDefinition,
  DocumentCategoryKey,
  DocumentOCRResult,
  StoredDocumentEvidence,
} from "../types";
import localSchemes from "../data/schemes.json";

const API_BASE = "/api";

export async function processIntake(text: string, language: string): Promise<{ profile: CitizenProfile; extractionMode: string; isMock?: boolean; defaultedFields?: string[] }> {
  try {
    const res = await fetch(`${API_BASE}/intake`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, language })
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {}

  // Graceful client fallback
  const textLower = text.toLowerCase();
  const profile: CitizenProfile = {
    name: "Citizen",
    state: "Karnataka",
    district: textLower.includes("mandya") ? "Mandya" : (textLower.includes("dharwad") ? "Dharwad" : "Karnataka"),
    educationLevel: textLower.includes("puc")
      ? "PUC"
      : (/\b(?:b\.?\s?sc\.?|b\.?\s?a\.?|b\.?\s?com\.?|bachelor(?:'s)?|graduate(?:d)?|degree)\b/i.test(text)
        ? "GRADUATE"
        : "PUC"),
    familyAnnualIncome: textLower.includes("1.5") || textLower.includes("onduvare") ? 150000 : 120000,
    casteCategory: "OBC",
    landHoldingAcres: 1.5,
    landType: "DRYLAND",
    occupation: textLower.includes("farmer") || textLower.includes("raitha") ? "FARMER" : (textLower.includes("unemployed") ? "UNEMPLOYED" : "STUDENT"),
    isAadhaarBankLinked: true
  };

  return {
    profile,
    extractionMode: "OFFLINE_DEMO",
    isMock: true,
    defaultedFields: ["name", "state", "district", "educationLevel", "familyAnnualIncome", "casteCategory", "landHoldingAcres", "landType", "occupation", "isAadhaarBankLinked"]
  };
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
  try {
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
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {}

  // Client-side rule evaluation fallback
  const matches: EligibilityMatchResult[] = [];
  const nearMisses: EligibilityMatchResult[] = [];
  const currentIncomeEvidence = [...documentEvidence]
    .reverse()
    .find((item) => item.category === "income" && item.validityStatus === "CURRENT" && item.extracted.annualIncomeINR !== null);
  const currentIncome = currentIncomeEvidence?.extracted.annualIncomeINR;
  const matchingProfile = typeof currentIncome === "number"
    ? { ...profile, familyAnnualIncome: currentIncome }
    : profile;

  (localSchemes as SchemeDefinition[]).forEach((scheme) => {
    if (scheme.state !== matchingProfile.state && scheme.state !== "All India") return;
    if (scheme.eligibilityMode === "MANUAL_REVIEW" || scheme.rules.length === 0) return;

    let passedCount = 0;
    const passedRules: any[] = [];
    const failedRules: any[] = [];

    scheme.rules.forEach((r) => {
      let passed = false;
      const userVal = (matchingProfile as any)[r.field];
      if (r.operator === "EQUALS") passed = String(userVal).toUpperCase() === String(r.value).toUpperCase();
      else if (r.operator === "LTE") passed = Number(userVal) <= Number(r.value);
      else if (r.operator === "GTE") passed = Number(userVal) >= Number(r.value);
      else if (r.operator === "IN") passed = Array.isArray(r.value) ? r.value.includes(userVal) : r.value === userVal;

      const detail = { predicate: r, userValue: userVal, requiredValue: r.value, passed };
      if (passed) {
        passedCount++;
        passedRules.push(detail);
      } else {
        failedRules.push(detail);
      }
    });

    const matchPercentage = (passedCount / scheme.rules.length) * 100;
    if (failedRules.length === 0) {
      matches.push({
        schemeId: scheme.id,
        scheme,
        status: "LIKELY_ELIGIBLE",
        matchPercentage: 100,
        passedRules,
        failedRules: [],
        nearMissRemediation: null
      });
    } else if (failedRules.length === 1) {
      nearMisses.push({
        schemeId: scheme.id,
        scheme,
        status: "NEAR_MISS",
        matchPercentage: Math.round(matchPercentage),
        passedRules,
        failedRules,
        nearMissRemediation: {
          actionTitleEn: `Action needed for ${failedRules[0].predicate.descriptionEn}`,
          actionTitleKn: `ಕ್ರಮ ಅಗತ್ಯವಿದೆ: ${failedRules[0].predicate.descriptionKn}`,
          actionTitleHi: `कार्रवाई आवश्यक: ${failedRules[0].predicate.descriptionHi}`,
          instructionsEn: "Update or register your qualification on the official portal to qualify.",
          instructionsKn: "ಅರ್ಹತೆ ಪಡೆಯಲು ಅಧಿಕೃತ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ನೋಂದಾಯಿಸಿ.",
          instructionsHi: "पात्रता प्राप्त करने के लिए आधिकारिक पोर्टल पर पंजीकरण करें।",
          portalUrl: scheme.officialPortalUrl
        }
      });
    }
  });

  const trace: AgentExecutionTraceStep[] = [
    { stepNumber: 1, timestamp: new Date().toLocaleTimeString(), agentRole: "ProfilerAgent", action: "[Offline demo] Prepared profile fields for local matching", input: { profileFields: Object.keys(profile) }, output: { state: profile.state, educationLevel: profile.educationLevel, occupation: profile.occupation }, durationMs: 110 },
    { stepNumber: 2, timestamp: new Date().toLocaleTimeString(), agentRole: "VectorSearch", action: "[Offline demo] Retrieved candidates from the selected-state catalog", input: { state: profile.state, concepts: [profile.educationLevel, profile.occupation] }, output: { candidates: [...matches, ...nearMisses].map((m) => m.schemeId) }, durationMs: 40 },
    { stepNumber: 3, timestamp: new Date().toLocaleTimeString(), agentRole: "RuleEngine", action: "[Offline demo] Evaluated catalog rules against the profile", input: { state: profile.state }, output: { eligible: matches.length, nearMiss: nearMisses.length }, durationMs: 65 },
    { stepNumber: 4, timestamp: new Date().toLocaleTimeString(), agentRole: "OfficialWebSearch", action: "[Offline demo] Live search unavailable; no substitute results were generated", input: { state: profile.state }, output: { status: "UNAVAILABLE", resultCount: 0 }, durationMs: 0 },
    { stepNumber: 5, timestamp: new Date().toLocaleTimeString(), agentRole: "DocConcierge", action: "[Offline demo] Assembled the checklist from local scheme matches", input: { matchedSchemeIds: matches.map((m) => m.schemeId), savedEvidenceCount: documentEvidence.length }, output: { requiredCertificates: new Set(matches.flatMap((m) => m.scheme.requiredDocuments.map((doc) => doc.id))).size }, durationMs: 50 }
  ];

  const manualReviewSchemes = (localSchemes as SchemeDefinition[]).filter(
    (scheme) => scheme.state === matchingProfile.state && scheme.eligibilityMode === "MANUAL_REVIEW",
  );
  return { matches, nearMisses, manualReviewSchemes, trace, isMock: true };
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
