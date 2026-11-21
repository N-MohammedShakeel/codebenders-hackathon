import React from "react";
import { AlertCircle, ArrowRight, ExternalLink } from "lucide-react";
import { EligibilityMatchResult } from "../types";
import { useLanguage } from "../context/LanguageContext";
import { localizedName } from "../lib/schemeText";

interface NearMissRoadmapCardProps {
  nearMiss: EligibilityMatchResult;
}

export const NearMissRoadmapCard: React.FC<NearMissRoadmapCardProps> = ({ nearMiss }) => {
  const { locale, t } = useLanguage();
  const scheme = nearMiss.scheme;
  const rem = nearMiss.nearMissRemediation;

  const schemeName = localizedName(scheme, locale);
  const actionTitle = rem ? (locale === "kn" ? rem.actionTitleKn : (locale === "hi" ? rem.actionTitleHi : rem.actionTitleEn)) : "";
  const instructions = rem ? (locale === "kn" ? rem.instructionsKn : (locale === "hi" ? rem.instructionsHi : rem.instructionsEn)) : "";

  return (
    <div className="bg-amber-50/70 border border-amber-200 rounded-2xl p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="p-1.5 bg-amber-100 text-amber-800 rounded-lg">
            <AlertCircle className="w-5 h-5 text-amber-700" />
          </span>
          <div>
            <span className="text-xs font-bold text-amber-800 uppercase tracking-wider block">
              {t("nearMissBadge")} ({nearMiss.matchPercentage}% Matched)
            </span>
            <h4 className="text-base font-bold text-slate-900">{schemeName}</h4>
          </div>
        </div>

        <span className="text-xs font-bold text-emerald-800 bg-emerald-100 px-3 py-1 rounded-full border border-emerald-200">
          Potential: ₹{(scheme.annualValueINR ?? 0).toLocaleString("en-IN")}/yr
        </span>
      </div>

      <div className="mt-4 p-4 bg-white rounded-xl border border-amber-100">
        <h5 className="text-xs font-bold text-amber-900 uppercase tracking-wide">
          1-Step Resolution Plan:
        </h5>
        <p className="text-sm font-semibold text-slate-800 mt-1">{actionTitle}</p>
        <p className="text-xs text-slate-600 mt-1">{instructions}</p>

        {rem?.portalUrl && (
          <a
            href={rem.portalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-700 hover:text-emerald-800 mt-3"
          >
            <span>Open Official Registration Portal</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        )}
      </div>
    </div>
  );
};
