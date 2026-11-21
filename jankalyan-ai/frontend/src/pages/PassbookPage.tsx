import React from "react";
import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { WelfarePassbookCard } from "../components/WelfarePassbookCard";
import { useCitizenProfile } from "../context/CitizenProfileContext";
import { useAppState } from "../context/AppStateContext";

export const PassbookPage: React.FC = () => {
  const { profile } = useCitizenProfile();
  const { matches } = useAppState();

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="no-print">
        <Link to="/" className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-800">
          <ArrowLeft className="w-4 h-4" />
          Back to Discovery Dashboard
        </Link>
      </div>

      <WelfarePassbookCard profile={profile} matches={matches} />
    </div>
  );
};
export default PassbookPage;
