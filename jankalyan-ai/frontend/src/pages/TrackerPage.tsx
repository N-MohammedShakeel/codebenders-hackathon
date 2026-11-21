import React from "react";
import { Clock, Send, CheckCircle2, AlertTriangle, ShieldCheck, FileCheck } from "lucide-react";
import { useAppState } from "../context/AppStateContext";
import { ApplicationTrackerItem } from "../types";

export const TrackerPage: React.FC = () => {
  const { applications, updateApplicationStage } = useAppState();

  const stages: Array<{ key: ApplicationTrackerItem["stage"]; label: string; color: string }> = [
    { key: "DISCOVERED", label: "1. Discovered", color: "bg-slate-100 text-slate-800" },
    { key: "DOCS_READY", label: "2. Docs Ready", color: "bg-blue-100 text-blue-800" },
    { key: "APPLIED", label: "3. Applied", color: "bg-amber-100 text-amber-800" },
    { key: "UNDER_VERIFICATION", label: "4. Under Scrutiny", color: "bg-purple-100 text-purple-800" },
    { key: "DISBURSED", label: "5. Disbursed", color: "bg-emerald-100 text-emerald-800" },
  ];


  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-900">Application Lifecycle & Deadline Tracker</h1>
        <p className="text-sm text-slate-600">Track active claims from discovery to bank fund disbursement.</p>
      </div>

      {/* Urgent Deadline Notification Card */}
      <div className="p-4 bg-amber-500 text-white rounded-2xl shadow-md flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Clock className="w-5 h-5 shrink-0" />
          <div>
            <span className="font-bold text-sm block">Upcoming Scheme Cutoff Alert!</span>
            <span className="text-xs text-amber-100">Deadlines must be confirmed on the official portal.</span>
          </div>
        </div>
        <span className="text-xs font-bold bg-white text-amber-900 px-3 py-1.5 rounded-xl shadow-xs">
          Active Cycle
        </span>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {stages.map((stage) => {
          const stageApps = applications.filter((a) => a.stage === stage.key);

          return (
            <div key={stage.key} className="bg-slate-100/70 p-4 rounded-2xl border border-slate-200 min-h-[360px] flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <span className={`text-xs font-bold px-2 py-1 rounded-md ${stage.color}`}>
                  {stage.label}
                </span>
                <span className="text-xs font-bold text-slate-400">{stageApps.length}</span>
              </div>

              <div className="space-y-3 flex-1">
                {stageApps.map((app) => (
                  <div key={app.id} className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-2">
                    <h4 className="font-bold text-xs text-slate-900 leading-snug">{app.schemeName}</h4>
                    {app.referenceNumber && (
                      <span className="text-[10px] font-mono text-slate-400 block">
                        Ref: {app.referenceNumber}
                      </span>
                    )}

                    <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-100 flex items-center justify-between">
                      <span>Deadline: {app.deadline}</span>
                    </div>

                    {/* Quick Move Stage dropdown */}
                    <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                      <select
                        value={app.stage}
                        onChange={(e) => updateApplicationStage(app.id, e.target.value as any)}
                        className="text-[10px] font-bold p-1 bg-slate-50 border border-slate-200 rounded"
                      >
                        {stages.map((s) => (
                          <option key={s.key} value={s.key}>{s.label}</option>
                        ))}
                      </select>

                      <button
                        disabled
                        className="text-[10px] text-slate-400 font-bold opacity-50 cursor-not-allowed"
                      >
                        Reminder not available yet
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
export default TrackerPage;
