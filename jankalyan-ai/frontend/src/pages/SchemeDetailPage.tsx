import React, { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, ExternalLink, ShieldCheck, CheckCircle2, Phone, MessageSquare, FileCheck } from "lucide-react";
import localSchemes from "../data/schemes.json";
import { SchemeDefinition } from "../types";
import { useLanguage } from "../context/LanguageContext";
import { PolicyChatDrawer } from "../components/PolicyChatDrawer";
import { localizedName, localizedBenefit, localizedSteps } from "../lib/schemeText";

export const SchemeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { locale } = useLanguage();
  const [isChatOpen, setIsChatOpen] = useState(false);

  const scheme = (localSchemes as SchemeDefinition[]).find((s) => s.id === id);

  if (!scheme) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <h2 className="text-xl font-bold">Scheme not found</h2>
        <Link to="/schemes" className="text-emerald-600 font-bold mt-4 inline-block">
          ← Back to Catalog
        </Link>
      </div>
    );
  }

  const schemeName = localizedName(scheme, locale);
  const benefitSummary = localizedBenefit(scheme, locale);
  const steps = localizedSteps(scheme, locale);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <Link to="/schemes" className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-800">
        <ArrowLeft className="w-4 h-4" />
        Back to Schemes Catalog
      </Link>

      {/* Main Banner Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <span className="text-xs font-bold px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full border border-emerald-200">
            {scheme.category}
          </span>
          <span className="text-xs text-slate-400">
            Source checked: {scheme.lastVerifiedDate}
          </span>
        </div>

        <h1 className="text-2xl sm:text-3xl font-black text-slate-900">{schemeName}</h1>
        <p className="text-sm text-slate-500 mt-1">{scheme.department}</p>

        {/* Financial Benefit Card */}
        <div className="mt-6 p-4 bg-emerald-50 rounded-xl border border-emerald-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            {scheme.annualValueINR !== null && scheme.annualValueINR > 0 ? (
              <>
                <span className="text-xs font-bold text-emerald-900 block">Annual Benefit</span>
                <span className="text-2xl font-black text-emerald-700">₹{scheme.annualValueINR.toLocaleString("en-IN")}/year</span>
              </>
            ) : (
              <span className="text-xs text-emerald-900">No annual cash amount is quantified in the catalog.</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsChatOpen(true)}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-xs transition"
            >
              <MessageSquare className="w-4 h-4" />
              <span>Ask AI Policy Assistant</span>
            </button>
            <a
              href={scheme.officialPortalUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl shadow-xs transition"
            >
              <span>Official Portal</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>

        <p className="text-sm text-slate-700 mt-4 leading-relaxed">{benefitSummary}</p>
      </div>

      {/* Eligibility Rules Predicate Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-base font-bold text-slate-900 mb-4">Eligibility Assessment</h2>
        {scheme.eligibilityMode === "MANUAL_REVIEW" && (
          <p className="mb-4 p-3 rounded-lg border border-amber-200 bg-amber-50 text-sm text-amber-900">
            {scheme.eligibilityNoteEn || "Eligibility is not fully represented in the app. Confirm all conditions on the official source."}
          </p>
        )}
        <div className="divide-y divide-slate-100">
          {scheme.rules.map((r, i) => (
            <div key={i} className="py-3 flex items-start gap-3 text-xs">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-slate-800">
                  {locale === "kn" ? r.descriptionKn : (locale === "hi" ? r.descriptionHi : r.descriptionEn)}
                </span>
                <span className="text-slate-400 block font-mono mt-0.5 text-[11px]">
                  Predicate: {r.field} {r.operator} {JSON.stringify(r.value)}
                </span>
              </div>
            </div>
          ))}
          {scheme.rules.length === 0 && (
            <p className="py-3 text-xs text-slate-500">The official source does not provide app-verified eligibility predicates for this entry.</p>
          )}
        </div>
      </div>

      {/* Required Documents Section */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-base font-bold text-slate-900 mb-4">Required Documents & Issuing Centers</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {scheme.requiredDocuments.map((d) => (
            <div key={d.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs">
              <span className="font-bold text-slate-900 block text-sm">
                {locale === "kn" ? d.nameKn : (locale === "hi" ? d.nameHi : d.nameEn)}
              </span>
              <span className="text-slate-500 block mt-1">Issuing Authority: <span className="font-semibold">{d.authority}</span></span>
              <div className="flex items-center justify-between text-[11px] text-slate-400 mt-3 pt-2 border-t border-slate-200">
                <span>Fee: {d.estimatedCost}</span>
                <span>Time: ~{d.turnaroundDays} days</span>
              </div>
            </div>
          ))}
          {scheme.requiredDocuments.length === 0 && (
            <p className="text-xs text-slate-500">Document requirements are not listed here; check the official source before applying.</p>
          )}
        </div>
      </div>

      {/* Step by Step Guide */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-base font-bold text-slate-900 mb-4">Step-by-Step Application Process</h2>
        <ol className="space-y-3">
          {steps.map((st, i) => (
            <li key={i} className="flex items-start gap-3 text-xs text-slate-700">
              <span className="w-6 h-6 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-[11px] shrink-0">
                {i + 1}
              </span>
              <span className="mt-0.5 leading-relaxed">{st}</span>
            </li>
          ))}
        </ol>
      </div>

      {/* Policy Chat Drawer */}
      <PolicyChatDrawer schemeId={isChatOpen ? scheme.id : null} onClose={() => setIsChatOpen(false)} />
    </div>
  );
};
export default SchemeDetailPage;
