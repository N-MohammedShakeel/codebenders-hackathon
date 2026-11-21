import React, { useState } from "react";
import { CheckSquare, Square, UploadCloud, AlertCircle } from "lucide-react";
import localSchemes from "../data/schemes.json";
import { DocumentCategoryKey, DocumentRequirement, SchemeDefinition } from "../types";
import { useAppState } from "../context/AppStateContext";
import { useLanguage } from "../context/LanguageContext";
import { PreFlightOCRModal } from "../components/PreFlightOCRModal";

export const DocumentsPage: React.FC = () => {
  const { locale } = useLanguage();
  const {
    checkedDocs,
    clearDocumentEvidence,
    toggleBankPassbookReadiness,
    saveDocumentEvidence,
    documentEvidence,
  } = useAppState();
  const [selectedOCRDoc, setSelectedOCRDoc] = useState<DocumentRequirement | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<DocumentCategoryKey | "all">("all");

  const categories: { id: DocumentCategoryKey | "all"; label: string }[] = [
    { id: "all", label: "All categories" },
    { id: "identity", label: "Identity" },
    { id: "income", label: "Income" },
    { id: "residence", label: "Residence" },
    { id: "education", label: "Education" },
    { id: "caste", label: "Caste" },
    { id: "land", label: "Land & farming" },
    { id: "bank", label: "Banking" },
    { id: "other", label: "Other" },
  ];

  const getCategory = (doc: DocumentRequirement): DocumentCategoryKey => {
    const id = doc.id.toLowerCase();
    const name = doc.nameEn.toLowerCase();
    if (id.includes("bank") || name.includes("bank")) return "bank";
    if (id.includes("aadhaar") || id.includes("identity") || name.includes("aadhaar") || name.includes("identity")) return "identity";
    if (id.includes("income") || name.includes("income")) return "income";
    if (id.includes("caste") || name.includes("caste")) return "caste";
    if (id.includes("college") || id.includes("degree") || name.includes("college") || name.includes("marks")) return "education";
    if (id.includes("land") || id.includes("farmer") || name.includes("land") || name.includes("farmer")) return "land";
    if (id.includes("domicile") || id.includes("ration") || name.includes("domicile") || name.includes("ration")) return "residence";
    return "other";
  };

  // Extract unique documents from catalog
  const allDocs: DocumentRequirement[] = [];
  const seenIds = new Set<string>();

  (localSchemes as SchemeDefinition[]).forEach((s) => {
    s.requiredDocuments.forEach((d) => {
      if (!seenIds.has(d.id)) {
        seenIds.add(d.id);
        allDocs.push(d);
      }
    });
  });

  const readyCount = allDocs.filter((d) => checkedDocs[d.id]).length;
  const readinessPercent = allDocs.length ? Math.round((readyCount / allDocs.length) * 100) : 0;
  const visibleDocs = allDocs.filter((doc) => selectedCategory === "all" || getCategory(doc) === selectedCategory);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-900">Document Readiness & Pre-Flight Hub</h1>
        <p className="text-sm text-slate-600">
          Organize the documents listed for schemes in the current catalog and review printed expiry dates.
        </p>
      </div>

      {/* Progress Card */}
      <div className="p-6 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
            Overall Document Readiness
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-black text-slate-900">{readinessPercent}%</span>
            <span className="text-xs text-slate-500">({readyCount} of {allDocs.length} marked ready)</span>
          </div>
          <div className="w-full sm:w-64 bg-slate-100 h-2 rounded-full overflow-hidden mt-3">
            <div className="bg-emerald-600 h-full rounded-full transition-all duration-500" style={{ width: `${readinessPercent}%` }} />
          </div>
        </div>

        <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900 flex items-start gap-2 max-w-sm">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <span>OCR can read selected fields and compare a printed expiry date. It does not authenticate documents or confirm official validity.</span>
        </div>
      </div>

      {/* Documents List */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-700 uppercase tracking-wider">
          Documents listed by the current scheme catalog
        </div>

        <div className="p-4 flex flex-wrap gap-2 border-b border-slate-100">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition ${
                selectedCategory === category.id
                  ? "bg-emerald-700 text-white border-emerald-700"
                  : "bg-white text-slate-600 border-slate-200 hover:border-emerald-400"
              }`}
            >
              {category.label}
              {category.id !== "all" && (
                <span className="ml-1 opacity-70">
                  ({allDocs.filter((doc) => getCategory(doc) === category.id).length})
                </span>
              )}
            </button>
          ))}
        </div>

        <p className="px-4 pt-3 text-xs text-slate-500">
          Saved OCR details are checked and sent with a scheme search. The bank passbook can be marked ready manually, but it is never uploaded or sent. Uncheck any checked item to clear its saved details or readiness.
        </p>
        <div className="divide-y divide-slate-100">
          {visibleDocs.map((doc) => {
            const evidence = documentEvidence[doc.id];
            const manualReadinessOnly = doc.id === "bank-passbook";
            const isChecked = !!checkedDocs[doc.id] && (manualReadinessOnly || !!evidence);
            const name = locale === "kn" ? doc.nameKn : (locale === "hi" ? doc.nameHi : doc.nameEn);

            return (
              <div key={doc.id} className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/60 transition">
                <div className="flex items-start gap-3">
                  <button
                    type="button"
                    onClick={() => manualReadinessOnly ? toggleBankPassbookReadiness() : clearDocumentEvidence(doc.id)}
                    disabled={!isChecked && !manualReadinessOnly}
                    aria-label={isChecked ? `Uncheck ${name}` : `Mark ${name} ready`}
                    title={isChecked ? "Uncheck to clear saved details or readiness" : "Run OCR to save details"}
                    className="mt-0.5 text-emerald-600 disabled:cursor-not-allowed"
                  >
                    {isChecked ? <CheckSquare className="w-5 h-5 fill-emerald-100" /> : <Square className="w-5 h-5 text-slate-300" />}
                  </button>
                  <div>
                    <span className="font-bold text-slate-900 text-sm block">{name}</span>
                    <span className="text-xs text-slate-500">
                      Authority: <span className="font-semibold">{doc.authority}</span> • Fee: {doc.estimatedCost} • Time: ~{doc.turnaroundDays}d
                    </span>
                    {evidence && (
                      <span className="mt-1 block text-xs text-slate-600">
                        OCR status: <strong>{evidence.validityStatus.replace("_", " ")}</strong>
                      </span>
                    )}
                    {manualReadinessOnly && isChecked && !evidence && (
                      <span className="mt-1 block text-xs text-slate-600">Marked ready manually; no document data is stored or sent.</span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center">
                  <button
                    onClick={() => setSelectedOCRDoc(doc)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-bold rounded-lg border border-emerald-200 transition"
                  >
                    <UploadCloud className="w-3.5 h-3.5" />
                    <span>{getCategory(doc) === "identity" || getCategory(doc) === "bank" ? "View OCR privacy info" : "Run Pre-Flight AI Check"}</span>
                  </button>
                </div>
              </div>
            );
          })}
          {visibleDocs.length === 0 && (
            <p className="p-5 text-sm text-slate-500">No documents in this category are listed in the current scheme catalog yet.</p>
          )}
        </div>
      </div>

      {/* OCR Modal */}
      <PreFlightOCRModal
        document={selectedOCRDoc}
        category={selectedOCRDoc ? getCategory(selectedOCRDoc) : null}
        onClose={() => setSelectedOCRDoc(null)}
        onSaveEvidence={(id, result) => {
          saveDocumentEvidence({
            documentId: id,
            category: selectedOCRDoc ? getCategory(selectedOCRDoc) : (result.extracted.documentCategory ?? "other"),
            validityStatus: result.validity.status,
            extracted: result.extracted,
            savedAt: new Date().toISOString(),
          });
        }}
      />
    </div>
  );
};
export default DocumentsPage;
