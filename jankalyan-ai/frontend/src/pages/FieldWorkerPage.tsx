import React, { useState } from "react";
import { Users, UserPlus, Printer, Share2, CheckCircle2 } from "lucide-react";
import { Link } from "react-router-dom";

export const FieldWorkerPage: React.FC = () => {
  const [queue, setQueue] = useState([
    { id: "1", name: "Karthik Gowda", village: "Keregodu, Mandya", income: "₹1,20,000", category: "OBC", eligibleCount: 2, totalBenefit: "₹30,000/yr" },
    { id: "2", name: "Manjula Bai", village: "Besagarahalli, Mandya", income: "₹85,000", category: "SC", eligibleCount: 3, totalBenefit: "₹3,84,000/yr" },
    { id: "3", name: "Basavaraj Patil", village: "Alnavar, Dharwad", income: "₹1,40,000", category: "General", eligibleCount: 1, totalBenefit: "₹10,000/yr" },
  ]);

  const [newName, setNewName] = useState("");
  const [newVillage, setNewVillage] = useState("");
  const [newIncome, setNewIncome] = useState("120000");

  const handleAddCitizen = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName) return;
    setQueue((prev) => [
      ...prev,
      {
        id: String(Date.now()),
        name: newName,
        village: newVillage || "Mandya",
        income: `₹${Number(newIncome).toLocaleString("en-IN")}`,
        category: "OBC",
        eligibleCount: 2,
        totalBenefit: "₹30,000/yr"
      }
    ]);
    setNewName("");
    setNewVillage("");
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold text-amber-800 bg-amber-100 px-2.5 py-1 rounded-full uppercase">
            Field Worker / VLE Portal (CSC & Panchayat)
          </span>
          <h1 className="text-2xl font-black text-slate-900 mt-2">Village Rapid Screening Queue</h1>
          <p className="text-sm text-slate-600">Screen rural families in 60 seconds and print their Family Entitlement Passbook.</p>
        </div>

        <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-xs text-right">
          <span className="text-[10px] text-slate-400 uppercase font-bold block">Screened Today</span>
          <span className="text-xl font-black text-emerald-700">{queue.length} Families</span>
        </div>
      </div>

      {/* Rapid Intake Form */}
      <form onSubmit={handleAddCitizen} className="p-6 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
          <UserPlus className="w-4 h-4 text-emerald-600" />
          Rapid Citizen Intake (under 60s)
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Citizen Full Name (e.g. Ramesh K)"
            className="text-xs p-3 bg-slate-50 border border-slate-300 rounded-xl focus:ring-1 focus:ring-emerald-500"
            required
          />
          <input
            type="text"
            value={newVillage}
            onChange={(e) => setNewVillage(e.target.value)}
            placeholder="Village / Gram Panchayat"
            className="text-xs p-3 bg-slate-50 border border-slate-300 rounded-xl focus:ring-1 focus:ring-emerald-500"
          />
          <input
            type="number"
            value={newIncome}
            onChange={(e) => setNewIncome(e.target.value)}
            placeholder="Annual Family Income (INR)"
            className="text-xs p-3 bg-slate-50 border border-slate-300 rounded-xl focus:ring-1 focus:ring-emerald-500"
          />
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-xs transition"
          >
            + Add to Screening Queue & Match
          </button>
        </div>
      </form>

      {/* Queue Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
            <tr>
              <th className="p-4">Citizen Name</th>
              <th className="p-4">Village</th>
              <th className="p-4">Income Bracket</th>
              <th className="p-4">Eligible Schemes</th>
              <th className="p-4">Annual Benefit</th>
              <th className="p-4 text-right">Passbook Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-800">
            {queue.map((item) => (
              <tr key={item.id} className="hover:bg-slate-50/70">
                <td className="p-4 font-bold text-slate-900">{item.name}</td>
                <td className="p-4 text-slate-500">{item.village}</td>
                <td className="p-4 font-semibold">{item.income}</td>
                <td className="p-4">
                  <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold">
                    {item.eligibleCount} Schemes
                  </span>
                </td>
                <td className="p-4 font-bold text-emerald-700">{item.totalBenefit}</td>
                <td className="p-4 text-right">
                  <Link
                    to="/passbook"
                    state={{ citizen: item }}
                    className="inline-flex items-center gap-1 px-3 py-1.5 bg-slate-900 text-white font-bold rounded-lg hover:bg-slate-800 transition"
                  >
                    <Printer className="w-3.5 h-3.5" />
                    <span>Print</span>
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
export default FieldWorkerPage;
