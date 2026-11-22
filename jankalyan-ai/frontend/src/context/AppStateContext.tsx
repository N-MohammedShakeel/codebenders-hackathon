import React, { createContext, useContext, useState, useEffect } from "react";
import {
  EligibilityMatchResult,
  AgentExecutionTraceStep,
  ApplicationTrackerItem,
  StoredDocumentEvidence,
  DiscoveryHistoryEntry,
  SchemeDefinition,
} from "../types";
import localSchemes from "../data/schemes.json";

interface AppStateContextType {
  matches: EligibilityMatchResult[];
  setMatches: (m: EligibilityMatchResult[]) => void;
  nearMisses: EligibilityMatchResult[];
  setNearMisses: (nm: EligibilityMatchResult[]) => void;
  trace: AgentExecutionTraceStep[];
  setTrace: (t: AgentExecutionTraceStep[]) => void;
  applications: ApplicationTrackerItem[];
  updateApplicationStage: (id: string, stage: ApplicationTrackerItem["stage"]) => void;
  checkedDocs: Record<string, boolean>;
  clearDocumentEvidence: (id: string) => void;
  toggleBankPassbookReadiness: () => void;
  documentEvidence: Record<string, StoredDocumentEvidence>;
  saveDocumentEvidence: (evidence: StoredDocumentEvidence) => void;
  discoveryHistory: DiscoveryHistoryEntry[];
  recordDiscovery: (entry: Omit<DiscoveryHistoryEntry, "id" | "searchedAt">) => void;
  clearDiscoveryHistory: () => void;
  matchedSchemeIdsForDiscovery: string[];
  markSchemeDetailsReviewed: (scheme: SchemeDefinition) => void;
  isFieldWorkerMode: boolean;
  toggleFieldWorkerMode: () => void;
  isOffline: boolean;
}

const APPLICATIONS_KEY = "jankalyan_apps";
const MATCHED_SCHEMES_KEY = "jankalyan_discovery_matched_scheme_ids";

const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

const DISCOVERY_HISTORY_KEY = "jankalyan_discovery_history";
const DISCOVERY_HISTORY_LIMIT = 20;

function loadDiscoveryHistory(): DiscoveryHistoryEntry[] {
  try {
    const saved = localStorage.getItem(DISCOVERY_HISTORY_KEY);
    if (!saved) return [];
    const entries: unknown = JSON.parse(saved);
    if (!Array.isArray(entries)) return [];
    return entries.filter((entry): entry is DiscoveryHistoryEntry =>
      entry !== null &&
      typeof entry === "object" &&
      typeof entry.id === "string" &&
      typeof entry.searchedAt === "string" &&
      typeof entry.state === "string" &&
      Array.isArray(entry.matchedSchemeIds) &&
      entry.matchedSchemeIds.every((id: unknown) => typeof id === "string") &&
      Array.isArray(entry.nearMissSchemeIds) &&
      entry.nearMissSchemeIds.every((id: unknown) => typeof id === "string") &&
      Array.isArray(entry.manualReviewSchemeIds) &&
      entry.manualReviewSchemeIds.every((id: unknown) => typeof id === "string")
    ).slice(0, DISCOVERY_HISTORY_LIMIT);
  } catch (error) {
    console.warn("Could not load discovery history from this browser.", error);
    return [];
  }
}

export const AppStateProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [matches, setMatches] = useState<EligibilityMatchResult[]>([]);
  const [nearMisses, setNearMisses] = useState<EligibilityMatchResult[]>([]);
  const [trace, setTrace] = useState<AgentExecutionTraceStep[]>([]);
  const [isFieldWorkerMode, setIsFieldWorkerMode] = useState<boolean>(false);
  const [isOffline, setIsOffline] = useState<boolean>(!navigator.onLine);
  const [discoveryHistory, setDiscoveryHistory] = useState<DiscoveryHistoryEntry[]>(loadDiscoveryHistory);
  const [matchedSchemeIdsForDiscovery, setMatchedSchemeIdsForDiscovery] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem(MATCHED_SCHEMES_KEY);
      const parsed = saved ? JSON.parse(saved) : [];
      return Array.isArray(parsed) ? parsed.filter((id): id is string => typeof id === "string") : [];
    } catch (error) {
      console.warn("Could not load discovery matches from this browser.", error);
      return [];
    }
  });

  const [applications, setApplications] = useState<ApplicationTrackerItem[]>(() => {
    try {
      const saved = localStorage.getItem(APPLICATIONS_KEY);
      if (!saved) return [];
      const parsed = JSON.parse(saved);
      if (!Array.isArray(parsed)) return [];
      const cleaned = parsed.filter(
        (application): application is ApplicationTrackerItem =>
          application &&
          typeof application === "object" &&
          application.id !== "app-1" &&
          application.id !== "app-2",
      );
      if (cleaned.length !== parsed.length) {
        localStorage.setItem(APPLICATIONS_KEY, JSON.stringify(cleaned));
      }
      return cleaned;
    } catch (e) {
      return [];
    }
  });

  const [documentEvidence, setDocumentEvidence] = useState<Record<string, StoredDocumentEvidence>>(() => {
    try {
      const saved = localStorage.getItem("jankalyan_document_evidence");
      return saved ? JSON.parse(saved) : {};
    } catch (e) {
      return {};
    }
  });
  const [checkedDocs, setCheckedDocs] = useState<Record<string, boolean>>(() => {
    const evidenceChecks = Object.fromEntries(
      Object.keys(documentEvidence).map((documentId) => [documentId, true]),
    );
    try {
      const saved = localStorage.getItem("jankalyan_docs");
      const savedChecks = saved ? JSON.parse(saved) : {};
      return {
        ...evidenceChecks,
        ...(savedChecks["bank-passbook"] === true ? { "bank-passbook": true } : {}),
      };
    } catch (error) {
      console.warn("Could not load saved document readiness from this browser.", error);
      return evidenceChecks;
    }
  });

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  const updateApplicationStage = (id: string, stage: ApplicationTrackerItem["stage"]) => {
    setApplications((prev) => {
      const updated = prev.map((a) => (a.id === id ? { ...a, stage } : a));
      localStorage.setItem(APPLICATIONS_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  const recalculateDocumentReadiness = (currentCheckedDocs: Record<string, boolean>) => {
    setApplications((previous) => {
      const updated = previous.map((application) => {
        if (application.stage !== "DISCOVERED" && application.stage !== "DOCS_READY") {
          return application;
        }
        const scheme = (localSchemes as SchemeDefinition[]).find(
          (item) => item.id === application.schemeId,
        );
        if (!scheme) return application;

        const requiredDocuments = scheme.requiredDocuments || [];
        const mandatoryDocuments = requiredDocuments.filter((document) => document.mandatory !== false);
        const documentsToCheck = mandatoryDocuments.length > 0 ? mandatoryDocuments : requiredDocuments;
        const documentsReady = documentsToCheck.length > 0 &&
          documentsToCheck.every((document) => !!currentCheckedDocs[document.id]);
        const nextStage: ApplicationTrackerItem["stage"] =
          documentsReady ? "DOCS_READY" : "DISCOVERED";

        return {
          ...application,
          stage: nextStage,
        };
      });
      localStorage.setItem(APPLICATIONS_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  const markSchemeDetailsReviewed = (scheme: SchemeDefinition) => {
    if (!matchedSchemeIdsForDiscovery.includes(scheme.id)) return;
    setApplications((previous) => {
      if (previous.some((application) => application.schemeId === scheme.id)) {
        return previous;
      }
      const requiredDocuments = scheme.requiredDocuments || [];
      const mandatoryDocuments = requiredDocuments.filter((document) => document.mandatory !== false);
      const documentsToCheck = mandatoryDocuments.length > 0 ? mandatoryDocuments : requiredDocuments;
      const documentsReady = documentsToCheck.length > 0 &&
        documentsToCheck.every((document) => !!checkedDocs[document.id]);
      const initialStage: ApplicationTrackerItem["stage"] =
        documentsReady ? "DOCS_READY" : "DISCOVERED";
      const newApplication: ApplicationTrackerItem = {
        id: `discovered-${scheme.id}`,
        schemeId: scheme.id,
        schemeName: scheme.nameEn,
        stage: initialStage,
        deadline: scheme.deadline || "Check official portal",
      };
      const updated = [...previous, newApplication];
      localStorage.setItem(APPLICATIONS_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  const clearDocumentEvidence = (id: string) => {
    if (!documentEvidence[id]) return;
    const remainingEvidence = { ...documentEvidence };
    delete remainingEvidence[id];
    const remainingChecks = { ...checkedDocs };
    delete remainingChecks[id];
    setDocumentEvidence(remainingEvidence);
    setCheckedDocs(remainingChecks);
    localStorage.setItem("jankalyan_document_evidence", JSON.stringify(remainingEvidence));
    localStorage.setItem("jankalyan_docs", JSON.stringify(remainingChecks));
    recalculateDocumentReadiness(remainingChecks);
  };

  const toggleBankPassbookReadiness = () => {
    const updatedChecks = {
      ...checkedDocs,
      "bank-passbook": !checkedDocs["bank-passbook"],
    };
    const updatedEvidence = { ...documentEvidence };
    delete updatedEvidence["bank-passbook"];
    setCheckedDocs(updatedChecks);
    setDocumentEvidence(updatedEvidence);
    localStorage.setItem("jankalyan_docs", JSON.stringify(updatedChecks));
    localStorage.setItem("jankalyan_document_evidence", JSON.stringify(updatedEvidence));
    recalculateDocumentReadiness(updatedChecks);
  };

  const saveDocumentEvidence = (evidence: StoredDocumentEvidence) => {
    const updatedEvidence = { ...documentEvidence, [evidence.documentId]: evidence };
    const updatedChecks = { ...checkedDocs, [evidence.documentId]: true };
    setDocumentEvidence(updatedEvidence);
    setCheckedDocs(updatedChecks);
    localStorage.setItem("jankalyan_document_evidence", JSON.stringify(updatedEvidence));
    localStorage.setItem("jankalyan_docs", JSON.stringify(updatedChecks));
    recalculateDocumentReadiness(updatedChecks);
  };

  const recordDiscovery = (entry: Omit<DiscoveryHistoryEntry, "id" | "searchedAt">) => {
    const candidateIds = Array.from(new Set([
      ...entry.matchedSchemeIds,
      ...entry.nearMissSchemeIds,
      ...entry.manualReviewSchemeIds,
    ]));
    setMatchedSchemeIdsForDiscovery(candidateIds);
    try {
      localStorage.setItem(MATCHED_SCHEMES_KEY, JSON.stringify(candidateIds));
    } catch (error) {
      console.error("Could not save discovery matches in this browser.", error);
    }
    const next = [{
      ...entry,
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      searchedAt: new Date().toISOString(),
    }, ...discoveryHistory].slice(0, DISCOVERY_HISTORY_LIMIT);
    setDiscoveryHistory(next);
    try {
      localStorage.setItem(DISCOVERY_HISTORY_KEY, JSON.stringify(next));
    } catch (error) {
      console.error("Could not save discovery history in this browser.", error);
    }
  };

  const clearDiscoveryHistory = () => {
    setDiscoveryHistory([]);
    try {
      localStorage.removeItem(DISCOVERY_HISTORY_KEY);
    } catch (error) {
      console.error("Could not clear discovery history from this browser.", error);
    }
  };

  const toggleFieldWorkerMode = () => {
    setIsFieldWorkerMode((prev) => !prev);
  };

  return (
    <AppStateContext.Provider
      value={{
        matches,
        setMatches,
        nearMisses,
        setNearMisses,
        trace,
        setTrace,
        applications,
        updateApplicationStage,
        checkedDocs,
        clearDocumentEvidence,
        toggleBankPassbookReadiness,
        documentEvidence,
        saveDocumentEvidence,
        discoveryHistory,
        recordDiscovery,
        clearDiscoveryHistory,
        matchedSchemeIdsForDiscovery,
        markSchemeDetailsReviewed,
        isFieldWorkerMode,
        toggleFieldWorkerMode,
        isOffline
      }}
    >
      {children}
    </AppStateContext.Provider>
  );
};

export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) throw new Error("useAppState must be used within AppStateProvider");
  return context;
};
