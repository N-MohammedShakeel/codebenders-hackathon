import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Sparkles, FileText, CheckCircle2, ArrowRight, ShieldCheck, Printer } from "lucide-react";
import { ConversationalIntake } from "../components/ConversationalIntake";
import { MatchedSchemeCard } from "../components/MatchedSchemeCard";
import { NearMissRoadmapCard } from "../components/NearMissRoadmapCard";
import { PolicyChatDrawer } from "../components/PolicyChatDrawer";
import { useLanguage } from "../context/LanguageContext";
import { useCitizenProfile } from "../context/CitizenProfileContext";
import { useAppState } from "../context/AppStateContext";
import { processIntake, runOrchestrator } from "../lib/api";
import { SchemeDefinition } from "../types";
import { localizedBenefit, localizedName } from "../lib/schemeText";
import localSchemes from "../data/schemes.json";

const catalogSchemeNames = new Map(
  (localSchemes as SchemeDefinition[]).map((scheme) => [scheme.id, scheme.nameEn]),
);

export const HomePage: React.FC = () => {
  const { t, locale } = useLanguage();
  const { profile, setProfile } = useCitizenProfile();
  const {
    matches,
    setMatches,
    nearMisses,
    setNearMisses,
    setTrace,
    documentEvidence,
    checkedDocs,
    discoveryHistory,
    recordDiscovery,
    clearDiscoveryHistory,
  } = useAppState();

  const [isLoading, setIsLoading] = useState(false);
  const [activeChatSchemeId, setActiveChatSchemeId] = useState<string | null>(null);
  const [defaultedFields, setDefaultedFields] = useState<string[]>([]);
  const [discoveredState, setDiscoveredState] = useState<string>("");
  const [manualReviewSchemes, setManualReviewSchemes] = useState<SchemeDefinition[]>([]);

  const handleDiscover = async (transcriptText: string, stateName: string) => {
    setIsLoading(true);
    try {
      // Step 1: Parse profile from voice/text
      const intakeRes = await processIntake(transcriptText, locale);
      const discoveryProfile = { ...intakeRes.profile, state: stateName };
      setProfile(discoveryProfile);

      // Step 2: Run multi-agent orchestrator
      const activeEvidence = Object.values(documentEvidence).filter(
        (item) =>
          checkedDocs[item.documentId] &&
          item.documentId !== "bank-passbook" &&
          item.category !== "bank",
      );
      const orchRes = await runOrchestrator(discoveryProfile, activeEvidence);
      setMatches(orchRes.matches);
      setNearMisses(orchRes.nearMisses);
      setTrace(orchRes.trace);
      setManualReviewSchemes(orchRes.manualReviewSchemes ?? []);
      setDefaultedFields(orchRes.defaultedFields ?? []);
      setDiscoveredState(stateName);
      recordDiscovery({
        state: stateName,
        matchedSchemeIds: orchRes.matches.map((match) => match.schemeId),
        nearMissSchemeIds: orchRes.nearMisses.map((nearMiss) => nearMiss.schemeId),
        manualReviewSchemeIds: (orchRes.manualReviewSchemes ?? []).map((scheme) => scheme.id),
      });
    } catch (err) {
      console.error("Discovery error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const totalIdentifiedBenefit = matches.reduce((sum, m) => sum + (m.scheme.annualValueINR || 0), 0);

  // Keep discovery results scoped to the selected state and All-India schemes.
  const hasResults = discoveredState !== "";
  const stateMatches = matches.filter((m) => m.scheme.state === discoveredState);
  const stateNearMisses = nearMisses.filter((nm) => nm.scheme.state === discoveredState);
  const nationalMatches = matches.filter((m) => m.scheme.state === "All India");
  const nationalNearMisses = nearMisses.filter((nm) => nm.scheme.state === "All India");
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Voice & Plain Language Intake Card */}
      <ConversationalIntake onDiscover={handleDiscover} isLoading={isLoading} />

      {hasResults && matches.length > 0 && (
        <div className="pt-4">
          {/* Results Header */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 bg-gradient-to-r from-emerald-900 to-green-950 text-white rounded-2xl shadow-lg border border-emerald-800">
            <div>
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest block">
                JanKalyan Swarm Analysis Complete
              </span>
              <h2 className="text-xl sm:text-2xl font-black mt-1">
                You appear likely eligible for {matches.length} Welfare Schemes!
              </h2>
              <p className="text-xs text-emerald-200 mt-1">
                Based on verified rules for {discoveredState} residents in {profile.district} district.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <div className="p-3 bg-white/10 rounded-xl backdrop-blur-xs text-right">
                <span className="text-[10px] text-emerald-300 uppercase font-semibold block">Total Potential Benefit</span>
                <span className="text-xl font-black text-white">₹{totalIdentifiedBenefit.toLocaleString("en-IN")}/yr</span>
              </div>
              <Link
                to="/passbook"
                className="inline-flex items-center gap-1.5 px-4 py-3 bg-white text-emerald-950 font-bold text-xs rounded-xl shadow-md hover:bg-emerald-50 transition"
              >
                <Printer className="w-4 h-4 text-emerald-700" />
                <span>Export Welfare Passbook</span>
              </Link>
            </div>
          </div>

          {defaultedFields.length > 0 && (
            <p className="text-xs text-amber-700 mt-2">
              Assumed values (not provided by you): {defaultedFields.join(", ")}
            </p>
          )}
        </div>
      )}

      {/* Group 1: Schemes in the selected state */}
      {hasResults && (stateMatches.length > 0 || stateNearMisses.length > 0) && (
        <div className="pt-4">
          <h3 className="text-base font-bold text-slate-800 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            Schemes in {discoveredState}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stateMatches.map((m) => (
              <MatchedSchemeCard
                key={m.schemeId}
                result={m}
                onOpenChat={(id) => setActiveChatSchemeId(id)}
              />
            ))}
            {stateNearMisses.map((nm) => (
              <NearMissRoadmapCard key={nm.schemeId} nearMiss={nm} />
            ))}
          </div>
        </div>
      )}

      {/* Group 2: All-India schemes */}
      {hasResults && (nationalMatches.length > 0 || nationalNearMisses.length > 0) && (
        <div className="pt-4">
          <h3 className="text-base font-bold text-slate-800 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            All-India schemes (apply in every state)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {nationalMatches.map((m) => (
              <MatchedSchemeCard
                key={m.schemeId}
                result={m}
                onOpenChat={(id) => setActiveChatSchemeId(id)}
              />
            ))}
            {nationalNearMisses.map((nm) => (
              <NearMissRoadmapCard key={nm.schemeId} nearMiss={nm} />
            ))}
          </div>
        </div>
      )}

      {hasResults && manualReviewSchemes.length > 0 && (
        <section className="pt-4">
          <h3 className="text-base font-bold text-slate-800 mb-3">
            {discoveredState} schemes needing official eligibility review
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {manualReviewSchemes.map((scheme) => (
              <article key={scheme.id} className="p-5 bg-white rounded-2xl border border-amber-200 shadow-sm">
                <span className="text-[10px] font-bold uppercase text-amber-800">{scheme.category} · Review required</span>
                <h4 className="mt-2 text-sm font-bold text-slate-900">{localizedName(scheme, locale)}</h4>
                <p className="mt-2 text-xs text-slate-600">{localizedBenefit(scheme, locale)}</p>
                {scheme.eligibilityNoteEn && <p className="mt-2 text-xs text-amber-900">{scheme.eligibilityNoteEn}</p>}
                <div className="mt-3 flex gap-4">
                  <Link to={`/schemes/${scheme.id}`} className="text-xs font-bold text-emerald-700 hover:underline">
                    Catalog details
                  </Link>
                  <a
                    href={scheme.officialPortalUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-bold text-emerald-700 hover:underline"
                  >
                    Official source
                  </a>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      {hasResults &&
        stateMatches.length === 0 &&
        stateNearMisses.length === 0 &&
        nationalMatches.length === 0 &&
        nationalNearMisses.length === 0 && (
          <div className="p-5 bg-white rounded-2xl border border-slate-200 text-sm text-slate-700">
            No schemes for {discoveredState} produced an automated eligibility match. This does not mean you are ineligible.
            {manualReviewSchemes.length === 0 && " Catalog coverage is not comprehensive."}
            <Link to="/schemes" className="ml-1 font-semibold text-emerald-700 hover:underline">
              Browse state schemes.
            </Link>
          </div>
        )}

      {discoveryHistory.length > 0 && (
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="font-bold text-slate-900">Recent searches</h3>
              <p className="mt-1 text-xs text-slate-500">
                Stored only in this browser: state and scheme IDs, not your description, profile, or documents.
              </p>
            </div>
            <button
              type="button"
              onClick={clearDiscoveryHistory}
              className="shrink-0 text-xs font-semibold text-slate-600 hover:text-red-700"
            >
              Clear history
            </button>
          </div>
          <ul className="mt-4 divide-y divide-slate-100">
            {discoveryHistory.map((entry) => {
              const schemeIds = [
                ...entry.matchedSchemeIds,
                ...entry.nearMissSchemeIds,
                ...entry.manualReviewSchemeIds,
              ];
              return (
                <li key={entry.id} className="py-3 first:pt-0 last:pb-0">
                  <p className="text-sm font-semibold text-slate-800">
                    {entry.state}
                    <span className="ml-2 text-xs font-normal text-slate-500">
                      {new Date(entry.searchedAt).toLocaleString()}
                    </span>
                  </p>
                  <p className="mt-1 text-xs text-slate-600">
                    {entry.matchedSchemeIds.length} likely match · {entry.nearMissSchemeIds.length} near miss · {entry.manualReviewSchemeIds.length} needing review
                  </p>
                  {schemeIds.length > 0 && (
                    <p className="mt-1 text-xs text-slate-500">
                      {schemeIds.map((id) => catalogSchemeNames.get(id) ?? id).join(", ")}
                    </p>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {/* Policy RAG Chat Drawer */}
      <PolicyChatDrawer
        schemeId={activeChatSchemeId}
        onClose={() => setActiveChatSchemeId(null)}
      />

      {/* Legal Guardrail Disclaimer Footer */}
      <div className="p-4 bg-slate-100 rounded-xl text-center text-xs text-slate-500 border border-slate-200">
        {t("disclaimer")}
      </div>
    </div>
  );
};
export default HomePage;
