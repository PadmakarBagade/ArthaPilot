"use client";

import React from "react";
import { X, ShieldCheck, Lock, Database, FileText } from "lucide-react";

interface DataTrustModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function DataTrustModal({ isOpen, onClose }: DataTrustModalProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="data-trust-title"
      onClick={onClose}
    >
      <div
        className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl p-6 max-h-[90vh] overflow-y-auto space-y-6 animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b pb-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-6 w-6 text-blue-600" />
            <h2 id="data-trust-title" className="text-xl font-bold text-slate-900">
              Data, Privacy & Verified Mathematics
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-4">
            <div className="flex items-center gap-2 text-emerald-900 font-bold text-sm">
              <Lock className="h-4 w-4 text-emerald-700" />
              Zero Calculation by LLM Guarantee
            </div>
            <p className="mt-1 text-xs text-emerald-800 leading-relaxed">
              ArthaPilot enforces an immutable architectural boundary: The language model <strong>never calculates money</strong>.
              All interest math, cash-flow forecasts, health scores, and metrics are calculated in pure, tested Python functions.
              The AI only routes requests and translates verified JSON results into clear explanations.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 p-4 space-y-3">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
              <Database className="h-4 w-4 text-blue-600" />
              Three-Layer Data Provenance
            </div>
            <div className="grid gap-2 text-xs text-slate-600 sm:grid-cols-3">
              <div className="bg-slate-50 p-2.5 rounded-lg border">
                <span className="font-bold text-slate-900 block">1. Synthetic Personas</span>
                Rahul, Priya, Arjun, Meera, and Sam. Controlled demos with planted anomalies.
              </div>
              <div className="bg-slate-50 p-2.5 rounded-lg border">
                <span className="font-bold text-slate-900 block">2. Berka Public Dataset</span>
                PKDD 99 Czech banking data testing cash-flow regularity and forecast calibration.
              </div>
              <div className="bg-slate-50 p-2.5 rounded-lg border">
                <span className="font-bold text-slate-900 block">3. Anonymised Uploads</span>
                Local CSV/XLSX/PDF statements. Names, accounts, and UPI IDs are masked locally before processing.
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 p-4 space-y-3">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
              <FileText className="h-4 w-4 text-blue-600" />
              Verified Validation Benchmarks
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-2.5">
                <span className="text-xl font-bold text-blue-800 block">100%</span>
                <span className="text-[11px] text-blue-700">Paise Precision (Zero Floats)</span>
              </div>
              <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-2.5">
                <span className="text-xl font-bold text-emerald-800 block">97.5%</span>
                <span className="text-[11px] text-emerald-700">Recurring Detection Recall</span>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-2.5">
                <span className="text-xl font-bold text-purple-800 block">102</span>
                <span className="text-[11px] text-purple-700">Automated Unit Tests</span>
              </div>
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-2.5">
                <span className="text-xl font-bold text-amber-800 block">1,000</span>
                <span className="text-[11px] text-amber-700">Monte Carlo Paths</span>
              </div>
            </div>
          </div>

          <div className="rounded-xl bg-slate-100 p-3 text-[11px] text-slate-500 leading-relaxed">
            <strong>Disclaimer:</strong> ArthaPilot provides educational and analytical financial guidance based on transaction patterns.
            It does not constitute regulated financial, investment, or tax advice under SEBI or RBI regulations.
          </div>
        </div>

        <div className="flex justify-end pt-2 border-t">
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl bg-blue-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 transition-colors"
          >
            I Understand
          </button>
        </div>
      </div>
    </div>
  );
}
