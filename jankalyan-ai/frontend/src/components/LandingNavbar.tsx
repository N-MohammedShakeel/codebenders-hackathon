import React from "react";
import { Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import type { Locale } from "../types";

export const LandingNavbar: React.FC = () => {
  const { locale, setLocale } = useLanguage();

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex shrink-0 items-center gap-2.5">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-green-600 to-emerald-400 text-xl font-bold text-white shadow-sm">
            JK
          </span>
          <span className="text-lg font-extrabold tracking-tight text-slate-900">JanKalyan AI</span>
        </Link>

        <nav className="hidden items-center gap-5 md:flex">
          <a href="/#how-it-works" className="text-sm font-semibold text-slate-600 hover:text-slate-900">
            How it works
          </a>
          <Link to="/schemes" className="text-sm font-semibold text-slate-600 hover:text-slate-900">
            Browse schemes
          </Link>
        </nav>

        <div className="flex shrink-0 items-center gap-2 sm:gap-3">
          <select
            aria-label="Language"
            title="Language"
            value={locale}
            onChange={(event) => setLocale(event.target.value as Locale)}
            className="max-w-28 rounded-lg border border-slate-200 bg-white px-2 py-2 text-xs font-bold text-slate-800"
          >
            <option value="en">English</option>
            <option value="kn">ಕನ್ನಡ</option>
            <option value="hi">हिंदी</option>
            <option value="ta">தமிழ்</option>
            <option value="ml">മലയാളം</option>
            <option value="te">తెలుగు</option>
          </select>
          <Link
            to="/discover"
            className="rounded-xl bg-emerald-700 px-3 py-2.5 text-xs font-bold text-white transition hover:bg-emerald-800 sm:px-4 sm:text-sm"
          >
            Enter application
          </Link>
        </div>
      </div>
    </header>
  );
};
