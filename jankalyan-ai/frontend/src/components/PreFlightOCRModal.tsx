import React, { useEffect, useState } from "react";
import { X, Upload, FileText, AlertCircle } from "lucide-react";
import { DocumentCategoryKey, DocumentOCRResult, DocumentRequirement } from "../types";
import { runDocumentOCR } from "../lib/api";

interface PreFlightOCRModalProps {
  document: DocumentRequirement | null;
  category: DocumentCategoryKey | null;
  onClose: () => void;
  onSaveEvidence: (docId: string, result: DocumentOCRResult) => void;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/heic", "application/pdf"];

export const PreFlightOCRModal: React.FC<PreFlightOCRModalProps> = ({ document, category, onClose, onSaveEvidence }) => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<DocumentOCRResult | null>(null);
  const [error, setError] = useState("");
  const sensitiveCategory = category === "identity" || category === "bank";

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  useEffect(() => {
    setFile(null);
    setPreview(null);
    setScanResult(null);
    setError("");
  }, [document?.id]);

  if (!document) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    setError("");
    setScanResult(null);
    setFile(null);
    setPreview(null);
    if (!ACCEPTED_TYPES.includes(selected.type)) {
      setError("Choose a JPG, PNG, WEBP, HEIC, or PDF file.");
      return;
    }
    if (selected.size > MAX_FILE_SIZE) {
      setError("The file must be 10 MB or smaller.");
      return;
    }
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
  };

  const handleRunPreFlightCheck = async () => {
    if (!file || !category) return;
    setIsScanning(true);
    setError("");
    try {
      setScanResult(await runDocumentOCR(file, category));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Document OCR could not be completed.");
    } finally {
      setIsScanning(false);
    }
  };

  const handleSaveEvidence = () => {
    if (!scanResult) return;
    onSaveEvidence(document.id, scanResult);
    onClose();
  };

  const statusStyles: Record<string, string> = {
    CURRENT: "bg-emerald-50 border-emerald-200 text-emerald-900",
    EXPIRED: "bg-red-50 border-red-200 text-red-900",
    TYPE_MISMATCH: "bg-amber-50 border-amber-200 text-amber-900",
    REVIEW_REQUIRED: "bg-amber-50 border-amber-200 text-amber-900",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full overflow-hidden shadow-2xl border border-slate-200">
        <div className="p-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-emerald-400" />
            <h3 className="font-bold text-sm">AI Pre-Flight Document Check</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          <div className="mb-4">
            <span className="text-xs font-semibold text-slate-500 block">Target Certificate:</span>
            <h4 className="text-base font-bold text-slate-900">{document.nameEn}</h4>
            <span className="text-xs text-slate-500">Issuing Authority: {document.authority}</span>
          </div>

          {/* Upload Dropzone */}
          {sensitiveCategory ? (
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900">
              OCR is disabled for identity and bank documents to protect sensitive numbers. Do not upload Aadhaar cards or bank records.
            </div>
          ) : !preview ? (
            <label className="border-2 border-dashed border-slate-300 hover:border-emerald-500 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer bg-slate-50 transition">
              <Upload className="w-8 h-8 text-slate-400 mb-2" />
              <span className="text-xs font-bold text-slate-700">Upload a document image or PDF (10 MB max)</span>
              <span className="text-[11px] text-slate-400 mt-1">The image is sent to Gemini for OCR; only selected OCR fields are saved in this browser.</span>
              <input type="file" accept=".jpg,.jpeg,.png,.webp,.heic,.pdf" onChange={handleFileChange} className="hidden" />
            </label>
          ) : (
            <div className="space-y-4">
              <div className="relative rounded-xl overflow-hidden max-h-48 bg-slate-100 flex items-center justify-center border border-slate-200">
                {file?.type === "application/pdf" ? (
                  <iframe src={preview} title="Document preview" className="h-48 w-full" />
                ) : (
                  <img src={preview} alt="Document preview" className="object-contain h-48 w-full" />
                )}
              </div>

              {!scanResult ? (
                <button
                  onClick={handleRunPreFlightCheck}
                  disabled={isScanning || !category}
                  className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow transition flex items-center justify-center gap-2"
                >
                  {isScanning ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Extracting document details...</span>
                    </>
                  ) : (
                    <span>Run Pre-Flight AI Check</span>
                  )}
                </button>
              ) : (
                <div className={`p-4 border rounded-xl space-y-2 ${statusStyles[scanResult.validity.status]}`}>
                  <div className="text-xs font-bold">
                    OCR status: {scanResult.validity.status.replace("_", " ")}
                  </div>
                  <p className="text-xs">{scanResult.validity.detail}</p>
                  <div className="text-[11px] pt-1 border-t border-current/10 space-y-1">
                    {scanResult.extracted.documentType && <div>Document type: <strong>{scanResult.extracted.documentType}</strong></div>}
                    {scanResult.extracted.issueDate && <div>Issue date: <strong>{scanResult.extracted.issueDate}</strong></div>}
                    {scanResult.extracted.expiryDate && <div>Printed expiry date: <strong>{scanResult.extracted.expiryDate}</strong></div>}
                    {scanResult.extracted.annualIncomeINR !== null && <div>Printed annual income: <strong>₹{scanResult.extracted.annualIncomeINR.toLocaleString("en-IN")}</strong></div>}
                  </div>
                  <p className="text-[11px]">{scanResult.note}</p>
                  <button
                    onClick={handleSaveEvidence}
                    className="w-full mt-2 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-xs transition"
                  >
                    Save extracted details
                  </button>
                </div>
              )}
            </div>
          )}
          {error && (
            <div className="mt-3 p-3 rounded-lg bg-red-50 border border-red-200 text-xs text-red-800 flex gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}
          <p className="mt-4 text-[11px] text-slate-500">
            OCR is not identity verification and does not determine authenticity. An expiry date is assessed only when explicitly printed on the document.
          </p>
        </div>
      </div>
    </div>
  );
};
