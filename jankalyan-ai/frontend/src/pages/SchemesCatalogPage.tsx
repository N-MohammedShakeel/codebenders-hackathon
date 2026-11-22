import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Search, ExternalLink } from "lucide-react";
import localSchemes from "../data/schemes.json";
import { SchemeDefinition } from "../types";
import { useLanguage } from "../context/LanguageContext";
import { hasLocalizedBenefit, localizedName, localizedBenefit } from "../lib/schemeText";
import { categoryLabels } from "../data/dictionaries";
import { INDIAN_STATES_AND_UTS } from "../data/states";

export const SchemesCatalogPage: React.FC = () => {
  const { locale, t } = useLanguage();
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [selectedState, setSelectedState] = useState("ALL");

  const categoryLabel = (category: string) =>
    category === "ALL"
      ? t("allCategories")
      : categoryLabels[locale][category] ?? category.replace(/_/g, " ");

  const categories = [
    "ALL",
    ...Array.from(new Set((localSchemes as SchemeDefinition[]).map((scheme) => scheme.category))).sort(),
  ];

  const filteredSchemes = (localSchemes as SchemeDefinition[]).filter((s) => {
    const matchesCat = selectedCategory === "ALL" || s.category === selectedCategory;
    const matchesState = selectedState === "ALL" || s.state === selectedState;
    const name = localizedName(s, locale);
    const benefit = localizedBenefit(s, locale);
    const query = search.trim().toLocaleLowerCase(locale);
    const matchesSearch = !query ||
      name.toLocaleLowerCase(locale).includes(query) ||
      benefit.toLocaleLowerCase(locale).includes(query) ||
      s.department.toLocaleLowerCase(locale).includes(query);
    return matchesCat && matchesState && matchesSearch;
  });
  const untranslatedCount = locale === "en"
    ? 0
    : filteredSchemes.filter((scheme) => !hasLocalizedBenefit(scheme, locale)).length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-900">{t("catalogTitle")}</h1>
        <p className="text-sm text-slate-600">{t("catalogDescription")}</p>
        {locale !== "en" && (
          <p className="mt-2 text-xs text-slate-500">{t("catalogTitleTranslationNotice")}</p>
        )}
        {untranslatedCount > 0 && (
          <p className="mt-2 text-xs text-amber-800" role="status">
            {t("catalogTranslationNotice").replace("{count}", String(untranslatedCount))}
          </p>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("searchCatalogPlaceholder")}
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:ring-1 focus:ring-emerald-500 focus:outline-none"
          />
        </div>

        <select
          aria-label={t("filterByState")}
          value={selectedState}
          onChange={(e) => setSelectedState(e.target.value)}
          className="w-full sm:w-56 px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold"
        >
          <option value="ALL">{t("allStatesAndUts")}</option>
          <option value="All India">{t("allIndiaSchemes")}</option>
          {INDIAN_STATES_AND_UTS.map((state) => (
            <option key={state} value={state}>{state}</option>
          ))}
        </select>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setSelectedCategory(c)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition shrink-0 ${
                selectedCategory === c
                  ? "bg-emerald-600 text-white shadow-xs"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              {categoryLabel(c)}
            </button>
          ))}
        </div>
      </div>

      {filteredSchemes.length === 0 && (
        <div className="p-6 bg-white rounded-2xl border border-slate-200 text-sm text-slate-600">
          {t("noCatalogMatches")}
        </div>
      )}

      {/* Schemes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredSchemes.map((s) => {
          const schemeName = localizedName(s, locale);
          const benefitSummary = localizedBenefit(s, locale);

          return (
            <div key={s.id} className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col justify-between hover:border-emerald-300 transition">
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                    {categoryLabel(s.category)}
                  </span>
                  <span className="text-[10px] text-slate-400 font-semibold">
                    {t("sourceChecked")}: {s.lastVerifiedDate}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 leading-snug">{schemeName}</h3>
                <p className="text-xs text-slate-500 mt-1">{s.department}</p>

                {s.annualValueINR !== null && s.annualValueINR > 0 && (
                  <div className="mt-3 p-3 bg-emerald-50 rounded-xl border border-emerald-100">
                    <span className="text-[10px] text-emerald-800 font-bold block">{t("annualValue")}</span>
                    <span className="text-base font-black text-emerald-700">₹{s.annualValueINR.toLocaleString("en-IN")}/yr</span>
                  </div>
                )}

                <p className="text-xs text-slate-600 mt-3 line-clamp-3">{benefitSummary}</p>
                {s.eligibilityMode === "MANUAL_REVIEW" && (
                  <p className="mt-3 p-2.5 rounded-lg border border-amber-200 bg-amber-50 text-xs text-amber-900">
                    {t("eligibilityNotAutomated")}
                  </p>
                )}
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                <Link
                  to={`/schemes/${s.id}`}
                  className="text-xs font-bold text-emerald-700 hover:text-emerald-800"
                >
                  {t("viewEligibilityRulesDocs")}
                </Link>
                <a
                  href={s.officialPortalUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition"
                  title={t("officialPortal")}
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
export default SchemesCatalogPage;
