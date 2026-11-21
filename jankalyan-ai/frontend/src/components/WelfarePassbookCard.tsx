import React, { useEffect, useState } from "react";
import QRCode from "qrcode";
import { Printer, Share2, ShieldCheck, IndianRupee, QrCode } from "lucide-react";
import { CitizenProfile, EligibilityMatchResult } from "../types";

interface WelfarePassbookCardProps {
  profile: CitizenProfile;
  matches: EligibilityMatchResult[];
}

export const WelfarePassbookCard: React.FC<WelfarePassbookCardProps> = ({ profile, matches }) => {
  const [qrDataUrl, setQrDataUrl] = useState<string>("");

  const totalBenefit = matches.reduce((sum, m) => sum + (m.scheme.annualValueINR || 0), 0);

  useEffect(() => {
    const deepLink = `https://jankalyan-ai.vercel.app/tracker?name=${encodeURIComponent(profile.name || "Citizen")}`;
    QRCode.toDataURL(deepLink, { width: 140, margin: 1 }, (err, url) => {
      if (!err && url) setQrDataUrl(url);
    });
  }, [profile]);

  const handlePrint = () => {
    window.print();
  };

  const handleWhatsAppShare = () => {
    const text = `*JanKalyan Welfare Entitlement Passbook for ${profile.name || "Citizen"}*\n\n` +
      `Eligible Schemes: ${matches.map((m) => m.scheme.nameEn).join(", ")}\n` +
      `Estimated Annual Benefit: ₹${totalBenefit.toLocaleString("en-IN")}\n\n` +
      `Track online: https://jankalyan-ai.vercel.app/tracker`;
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, "_blank");
  };

  return (
    <div className="space-y-4">
      {/* Action Buttons (Hidden on Print) */}
      <div className="flex items-center justify-end gap-3 no-print">
        <button
          onClick={handlePrint}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl shadow-xs transition"
        >
          <Printer className="w-4 h-4" />
          <span>Print Passbook (PDF)</span>
        </button>

        <button
          onClick={handleWhatsAppShare}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-xs transition"
        >
          <Share2 className="w-4 h-4" />
          <span>Share to WhatsApp</span>
        </button>
      </div>

      {/* The Printable Entitlement Passbook Card */}
      <div className="bg-white p-8 rounded-2xl border-2 border-slate-300 shadow-md text-slate-900 print:border-none print:shadow-none">
        {/* Header */}
        <div className="flex items-start justify-between border-b-2 border-emerald-600 pb-4 mb-6">
          <div>
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-emerald-800 block">
              Government of Karnataka • Digital Citizen Public Service
            </span>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">
              Family Welfare Entitlement Passbook
            </h1>
            <span className="text-xs text-slate-500">
              Verified Cycle 2026-27 • Direct Benefit Transfer (DBT) Ready
            </span>
          </div>

          <div className="text-right">
            <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-800 bg-emerald-100 px-3 py-1 rounded-full border border-emerald-200">
              <ShieldCheck className="w-3.5 h-3.5" />
              Likely Eligible
            </span>
            <span className="text-[10px] text-slate-400 block mt-1">
              Ref: JK-KA-{Math.floor(100000 + Math.random() * 900000)}
            </span>
          </div>
        </div>

        {/* Beneficiary Profile Box */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs mb-6">
          <div>
            <span className="text-slate-400 block">Beneficiary Name</span>
            <span className="font-bold text-slate-900 text-sm">{profile.name || "Citizen"}</span>
          </div>
          <div>
            <span className="text-slate-400 block">District / State</span>
            <span className="font-bold text-slate-900">{profile.district}, {profile.state}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Annual Income Bracket</span>
            <span className="font-bold text-slate-900">₹{profile.familyAnnualIncome?.toLocaleString("en-IN") || "1,20,000"}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Category / Course</span>
            <span className="font-bold text-slate-900">{profile.casteCategory || "OBC"} • {profile.educationLevel || "PUC"}</span>
          </div>
        </div>

        {/* Highlight Benefit Box */}
        <div className="p-4 bg-gradient-to-r from-emerald-600 to-green-600 rounded-xl text-white flex items-center justify-between mb-6 shadow-xs">
          <div>
            <span className="text-xs font-medium text-emerald-100 uppercase tracking-wider block">
              Total Identified Annual Benefit
            </span>
            <span className="text-2xl font-black">
              ₹{totalBenefit.toLocaleString("en-IN")}{" "}
              <span className="text-sm font-normal text-emerald-100">/ year</span>
            </span>
          </div>
          <span className="text-xs font-bold bg-white text-emerald-900 px-3 py-1.5 rounded-lg shadow-xs">
            {matches.length} Schemes Matched
          </span>
        </div>

        {/* Matched Schemes Table */}
        <div className="mb-6">
          <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 mb-2">
            Entitled Welfare Schemes
          </h3>
          <div className="border border-slate-200 rounded-xl overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                <tr>
                  <th className="p-3">Scheme Name</th>
                  <th className="p-3">Department</th>
                  <th className="p-3">Annual Benefit</th>
                  <th className="p-3">Official Portal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800">
                {matches.map((m) => (
                  <tr key={m.schemeId} className="hover:bg-slate-50">
                    <td className="p-3 font-bold text-slate-900">{m.scheme.nameEn}</td>
                    <td className="p-3 text-slate-600">{m.scheme.department}</td>
                    <td className="p-3 font-bold text-emerald-700">₹{(m.scheme.annualValueINR ?? 0).toLocaleString("en-IN")}</td>
                    <td className="p-3 text-slate-500 font-mono text-[11px]">{m.scheme.officialPortalUrl.replace("https://", "")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer with QR Code */}
        <div className="pt-6 border-t-2 border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-slate-500 max-w-md">
            <span className="font-bold text-slate-800 block mb-1">How to Claim:</span>
            <p>1. Present this passbook at your local Grama One or Bangalore One center.</p>
            <p>2. Keep Nadakacheri Income Certificate (15-digit RD Number) ready.</p>
            <p>3. Do NOT pay any unofficial processing fees to middlemen.</p>
            <span className="text-[10px] text-slate-400 block mt-2">
              Official Helpline: 1902 • Verified by JanKalyan AI Engine
            </span>
          </div>

          {qrDataUrl && (
            <div className="text-center shrink-0">
              <img src={qrDataUrl} alt="Passbook QR Code" className="w-24 h-24 mx-auto border border-slate-200 p-1 rounded-lg" />
              <span className="text-[9px] font-bold text-slate-500 block mt-1">Scan to Track on Mobile</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
