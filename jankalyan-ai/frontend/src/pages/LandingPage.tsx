import React from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  CheckCircle2,
  FileCheck2,
  Globe2,
  ShieldCheck,
  Sparkles,
  Search,
  Languages,
} from "lucide-react";

const steps = [
  {
    icon: Languages,
    title: "Tell us in your language",
    description: "Speak or type your situation in plain words.",
  },
  {
    icon: Search,
    title: "We search the right schemes",
    description: "Profile, state, catalogue, and official portal checks work together.",
  },
  {
    icon: FileCheck2,
    title: "Prepare the documents",
    description: "Review document requirements and optional OCR evidence.",
  },
];

export const LandingPage: React.FC = () => {
  return (
    <div className="overflow-hidden bg-slate-50">
      <section className="relative">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top_right,_rgba(16,185,129,0.18),_transparent_38%),radial-gradient(circle_at_bottom_left,_rgba(14,116,144,0.12),_transparent_32%)]" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <div className="grid lg:grid-cols-[1.08fr_0.92fr] items-center gap-12">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white px-3 py-1.5 text-xs font-bold text-emerald-800 shadow-sm">
                <Sparkles className="h-3.5 w-3.5" />
                Simple welfare discovery
              </div>
              <h1 className="mt-6 max-w-3xl text-4xl sm:text-6xl font-black tracking-tight text-slate-950 leading-[1.05]">
                Find government schemes
                <span className="block text-emerald-700">made for you.</span>
              </h1>
              <p className="mt-6 max-w-2xl text-base sm:text-lg leading-8 text-slate-600">
                Describe your situation in everyday language. JanKalyan AI helps
                you find likely matches, understand missing criteria, and prepare
                for the next step.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row gap-3">
                <Link
                  to="/discover"
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-700 px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-emerald-700/20 transition hover:bg-emerald-800"
                >
                  Find my entitlements
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  to="/schemes"
                  className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-6 py-3.5 text-sm font-bold text-slate-800 shadow-sm transition hover:border-emerald-400 hover:text-emerald-800"
                >
                  Browse all schemes
                </Link>
              </div>
              <div className="mt-7 flex flex-wrap gap-x-5 gap-y-2 text-xs font-semibold text-slate-600">
                <span className="inline-flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4 text-emerald-700" />
                  No Aadhaar or phone number required
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <Globe2 className="h-4 w-4 text-emerald-700" />
                  Six supported languages
                </span>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -inset-4 rounded-[2rem] bg-emerald-100/70 blur-2xl" />
              <div className="relative rounded-[2rem] border border-slate-200 bg-white p-5 sm:p-7 shadow-2xl shadow-slate-900/10">
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                      Your discovery
                    </p>
                    <p className="mt-1 font-black text-slate-900">A clear next step</p>
                  </div>
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
                    <CheckCircle2 className="h-6 w-6" />
                  </div>
                </div>
                <div className="mt-5 space-y-3">
                  {[
                    ["Profile understood", "Education, work and state"],
                    ["Schemes compared", "Official catalogue candidates"],
                    ["Documents listed", "What to prepare next"],
                  ].map(([title, subtitle], index) => (
                    <div key={title} className="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 p-3.5">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-700 text-xs font-black text-white">
                        {index + 1}
                      </div>
                      <div>
                        <p className="text-sm font-bold text-slate-900">{title}</p>
                        <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-900">
                  Results are guidance, not final sanction. Always verify on the official government portal.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid gap-8 md:grid-cols-3">
            {steps.map((step) => {
              const Icon = step.icon;
              return (
                <div key={step.title} className="flex gap-4">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="font-bold text-slate-900">{step.title}</h2>
                    <p className="mt-1 text-sm leading-6 text-slate-600">{step.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
