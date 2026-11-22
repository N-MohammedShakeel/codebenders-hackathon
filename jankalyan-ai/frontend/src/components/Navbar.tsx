import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { useAppState } from "../context/AppStateContext";
import type { Locale } from "../types";
import { Globe, Users, Award, FileText, CheckCircle2, BookOpen } from "lucide-react";

export const Navbar: React.FC = () => {
  const { locale, setLocale, t } = useLanguage();
  const { isFieldWorkerMode, toggleFieldWorkerMode, isOffline } = useAppState();
  const location = useLocation();

  const navLinks = [
    { path: "/", label: t("appTitle"), icon: Award },
    { path: "/discover", label: "Discover", icon: Globe },
    { path: "/schemes", label: t("schemesTab"), icon: BookOpen },
    { path: "/documents", label: t("documentsTab"), icon: FileText },
    { path: "/tracker", label: t("trackerTab"), icon: CheckCircle2 },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-green-600 to-emerald-400 flex items-center justify-center text-white font-bold text-xl shadow-sm">
              JK
            </div>
            <div>
              <span className="font-extrabold text-xl tracking-tight text-slate-900 block leading-tight">
                {t("appTitle")}
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-semibold transition ${
                    isActive
                      ? "text-emerald-700 bg-emerald-50"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* Action Controls */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Field Worker Mode Toggle */}
            <button
              onClick={toggleFieldWorkerMode}
              className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-lg border transition ${
                isFieldWorkerMode
                  ? "bg-amber-500 text-white border-amber-600 shadow-sm"
                  : "bg-slate-50 text-slate-700 border-slate-300 hover:bg-slate-100"
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">
                {isFieldWorkerMode ? t("fieldWorkerMode") : t("citizenMode")}
              </span>
            </button>

            {/* Language Switcher */}
            <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200">
              <select
                aria-label="Language"
                title="Language"
                value={locale}
                onChange={(e) => setLocale(e.target.value as Locale)}
                className="px-2 py-1 text-xs font-bold rounded bg-white text-slate-900 shadow-xs border-0 outline-none cursor-pointer"
              >
                <option value="en">English</option>
                <option value="kn">ಕನ್ನಡ</option>
                <option value="hi">हिंदी</option>
                <option value="ta">தமிழ்</option>
                <option value="ml">മലയാളം</option>
                <option value="te">తెలుగు</option>
              </select>
            </div>

            {/* Offline Status Badge */}
            {isOffline && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">
                Offline
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
