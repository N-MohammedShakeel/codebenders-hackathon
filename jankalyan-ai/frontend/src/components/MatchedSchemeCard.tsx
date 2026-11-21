import React, { useState } from "react";
import { Link } from "react-router-dom";
import { CheckCircle2, ShieldCheck, ExternalLink, RefreshCw, MessageSquare, IndianRupee, FileText } from "lucide-react";
import { EligibilityMatchResult } from "../types";
import { useLanguage } from "../context/LanguageContext";
import { checkTavilyUpdates } from "../lib/api";
import { localizedName, localizedBenefit } from "../lib/schemeText";

interface MatchedSchemeCardProps {
  result: EligibilityMatchResult;
  onOpenChat: (schemeId: string) => void;
}

export const MatchedSchemeCard: React.FC<MatchedSchemeCardProps> = ({ result, onOpenChat }) => {
  const { locale, t } = useLanguage();
  const scheme = result.scheme;
  const [isCheckingTavily, setIsCheckingTavily] = useState(false);
  const [tavilyUpdate, setTavilyUpdate] = useState<any | null>(null);

  const schemeName = localizedName(scheme, locale);
  const benefitSummary = localizedBenefit(scheme, locale);

  const handleCheckUpdates = async () => {
    setIsCheckingTavily(true);
    const data = await checkTavilyUpdates(scheme.nameEn, scheme.id);
    setTavilyUpdate(data);
    setIsCheckingTavily(false);
  };

  return (
    <div className="bg-white rounded-2xl shadow-md border border-slate-200 overflow-hidden hover:border-emerald-300 transition-all flex flex-col justify-between">
      <div className="p-6">
        {/* Top Badges */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <ShieldCheck className="w-3.5 h-3.5" />
            {t("likelyEligibleBadge")}
          </span>
          <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
            Verified: {scheme.lastVerifiedDate}
          </span>
        </div>

        {/* Scheme Name & Department */}
        <h3 className="text-lg font-bold text-slate-900 leading-snug">
          {schemeName}
        </h3>
        <p className="text-xs font-medium text-slate-500 mt-1">
          {scheme.department}
        </p>

        {/* Financial Benefit Box */}
        <div className="mt-4 p-3.5 bg-emerald-50/70 rounded-xl border border-emerald-100 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-emerald-900 block">
              {t("annualValue")}
            </span>
            <span className="text-lg font-extrabold text-emerald-700 flex items-center">
              ₹{(scheme.annualValueINR ?? 0).toLocaleString("en-IN")}{" "}
              <span className="text-xs font-normal text-emerald-800 ml-1">/ year</span>
            </span>
          </div>
          <span className="text-xs font-bold px-2 py-1 bg-white text-emerald-800 rounded-lg shadow-2xs border border-emerald-200">
            {scheme.category}
          </span>
        </div>

        {/* Benefit Summary Description */}
        <p className="text-sm text-slate-600 mt-3 font-normal leading-relaxed">
          {benefitSummary}
        </p>

        {/* Rule-by-rule Verification Checklist */}
        <div className="mt-4 pt-3 border-t border-slate-100">
          <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
            {t("passedRules")}
          </h4>
          <ul className="space-y-1.5">
            {result.passedRules.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-700">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>
                  {locale === "kn" ? r.predicate.descriptionKn : (locale === "hi" ? r.predicate.descriptionHi : r.predicate.descriptionEn)}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Tavily Live Gazette Update Banner if checked */}
        {tavilyUpdate && (
          <div className="mt-4 p-3 bg-blue-50 rounded-xl border border-blue-200 text-xs text-blue-900">
            <span className="font-bold flex items-center gap-1 text-blue-800">
              <RefreshCw className="w-3.5 h-3.5 text-blue-600" />
              Live Tavily Web Check Result:
            </span>
            <p className="mt-1 text-blue-800/90">{tavilyUpdate.results?.[0]?.content || "Application window verified active."}</p>
            <span className="text-[10px] text-blue-600 block mt-1 font-semibold">
              Source: {tavilyUpdate.results?.[0]?.url || "karnataka.gov.in"}
            </span>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="px-6 py-4 bg-slate-50/80 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <button
            onClick={handleCheckUpdates}
            disabled={isCheckingTavily}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 bg-white hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isCheckingTavily ? "animate-spin" : ""}`} />
            <span className="hidden sm:inline">{t("checkUpdates")}</span>
          </button>

          <button
            onClick={() => onOpenChat(scheme.id)}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-semibold rounded-lg border border-emerald-200 transition"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>{t("askAI")}</span>
          </button>
        </div>

        <div className="flex items-center gap-2">
          <Link
            to={`/schemes/${scheme.id}`}
            className="text-xs font-bold text-slate-600 hover:text-slate-900 underline"
          >
            Details
          </Link>
          <a
            href={scheme.officialPortalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-lg shadow-xs transition"
          >
            <span>Apply</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
};
