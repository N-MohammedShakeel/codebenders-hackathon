import React, { useState } from "react";
import { Plus, Edit2, Trash2, CheckCircle2 } from "lucide-react";
import localSchemes from "../data/schemes.json";
import { SchemeDefinition } from "../types";

export const AdminSchemesPage: React.FC = () => {
  const [schemes, setSchemes] = useState<SchemeDefinition[]>(localSchemes as SchemeDefinition[]);
  const [editingScheme, setEditingScheme] = useState<SchemeDefinition | null>(null);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-900">Scheme Knowledge Base & Rule Editor</h1>
          <p className="text-sm text-slate-600">Edit income cutoffs, deadlines, and predicates without modifying code.</p>
        </div>

        <button
          disabled
          title="Editing is not available in this version"
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs transition opacity-50 cursor-not-allowed"
        >
          + Add New Scheme
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
            <tr>
              <th className="p-4">ID</th>
              <th className="p-4">Scheme Name</th>
              <th className="p-4">Department</th>
              <th className="p-4">Category</th>
              <th className="p-4">Annual Benefit</th>
              <th className="p-4">Last Verified</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-800">
            {schemes.map((s) => (
              <tr key={s.id} className="hover:bg-slate-50">
                <td className="p-4 font-mono text-slate-400">{s.id}</td>
                <td className="p-4 font-bold text-slate-900">{s.nameEn}</td>
                <td className="p-4 text-slate-500 max-w-xs truncate">{s.department}</td>
                <td className="p-4"><span className="px-2 py-0.5 bg-slate-100 rounded font-semibold">{s.category}</span></td>
                <td className="p-4 font-bold text-emerald-700">{s.annualValueINR !== null && s.annualValueINR > 0 ? `₹${s.annualValueINR.toLocaleString("en-IN")}` : "Not quantified"}</td>
                <td className="p-4 text-slate-400">{s.lastVerifiedDate}</td>
                <td className="p-4 text-right">
                  <button
                    disabled
                    title="Editing is not available in this version"
                    className="p-1.5 hover:bg-slate-100 rounded text-slate-600 mr-1 opacity-50 cursor-not-allowed"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
export default AdminSchemesPage;
