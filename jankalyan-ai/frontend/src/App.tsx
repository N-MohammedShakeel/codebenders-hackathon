import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LanguageProvider } from "./context/LanguageContext";
import { CitizenProfileProvider } from "./context/CitizenProfileContext";
import { AppStateProvider } from "./context/AppStateContext";
import { Navbar } from "./components/Navbar";
import { OfflineBanner } from "./components/OfflineBanner";

import HomePage from "./pages/HomePage";
import SchemesCatalogPage from "./pages/SchemesCatalogPage";
import SchemeDetailPage from "./pages/SchemeDetailPage";
import DocumentsPage from "./pages/DocumentsPage";
import TrackerPage from "./pages/TrackerPage";
import PassbookPage from "./pages/PassbookPage";
import FieldWorkerPage from "./pages/FieldWorkerPage";
import AdminSchemesPage from "./pages/AdminSchemesPage";

export default function App() {
  return (
    <LanguageProvider>
      <CitizenProfileProvider>
        <AppStateProvider>
          <BrowserRouter>
            <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
              <OfflineBanner />
              <Navbar />
              <main className="flex-1">
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/schemes" element={<SchemesCatalogPage />} />
                  <Route path="/schemes/:id" element={<SchemeDetailPage />} />
                  <Route path="/documents" element={<DocumentsPage />} />
                  <Route path="/tracker" element={<TrackerPage />} />
                  <Route path="/passbook" element={<PassbookPage />} />
                  <Route path="/field-worker" element={<FieldWorkerPage />} />
                  <Route path="/admin/schemes" element={<AdminSchemesPage />} />
                </Routes>
              </main>
            </div>
          </BrowserRouter>
        </AppStateProvider>
      </CitizenProfileProvider>
    </LanguageProvider>
  );
}
