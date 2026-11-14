"use client";

import React from "react";
import { X, ExternalLink, ShieldCheck } from "lucide-react";
import { formatPaise } from "@/lib/api";

export interface EvidenceDetail {
  title: string;
  category?: string;
  summary: string;
  formula?: string;
  transactionIds?: string[];
  rawNumbers?: Record<string, string | number>;
  source?: string;
}

interface EvidenceDrawerProps {
  evidence: EvidenceDetail | null;
  onClose: () => void;
}

export function EvidenceDrawer({ evidence, onClose }: EvidenceDrawerProps) {
  if (!evidence) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-sm transition-opacity"
      role="dialog"
      aria-modal="true"
      aria-labelledby="evidence-drawer-title"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md bg-white p-6 shadow-2xl flex flex-col h-full overflow-y-auto animate-in slide-in-from-right duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b pb-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-blue-600" />
            <h2 id="evidence-drawer-title" className="text-lg font-semibold text-slate-900">
              Verified Evidence
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            aria-label="Close evidence panel"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="py-5 space-y-5 flex-1">
          <div>
            <span className="inline-block rounded bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 uppercase tracking-wide">
              {evidence.category || "Calculation Audit"}
            </span>
            <h3 className="mt-2 text-xl font-bold text-slate-900">{evidence.title}</h3>
            <p className="mt-2 text-sm text-slate-600 leading-relaxed">{evidence.summary}</p>
          </div>

          {evidence.formula && (
            <div className="rounded-xl border border-blue-100 bg-blue-50/60 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-blue-800">Deterministic Formula</p>
              <code className="mt-1 block font-mono text-xs text-blue-900 bg-white/80 p-2.5 rounded border border-blue-200 overflow-x-auto">
                {evidence.formula}
              </code>
            </div>
          )}

          {evidence.rawNumbers && Object.keys(evidence.rawNumbers).length > 0 && (
            <div className="rounded-xl border border-slate-200 p-4 space-y-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Component Values</p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(evidence.rawNumbers).map(([key, val]) => (
                  <div key={key} className="bg-slate-50 p-2 rounded">
                    <span className="text-slate-500 block truncate">{key}</span>
                    <span className="font-semibold text-slate-900 font-mono">
                      {typeof val === "number" && Math.abs(val) > 1000 ? formatPaise(val) : String(val)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {evidence.transactionIds && evidence.transactionIds.length > 0 && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                Backing Transactions ({evidence.transactionIds.length})
              </p>
              <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1">
                {evidence.transactionIds.slice(0, 20).map((id) => (
                  <div key={id} className="flex items-center justify-between text-xs bg-slate-50 border p-2 rounded font-mono text-slate-700">
                    <span className="truncate max-w-[280px]">{id}</span>
                    <ExternalLink className="h-3 w-3 text-slate-400 shrink-0" />
                  </div>
                ))}
              </div>
              {evidence.transactionIds.length > 20 && (
                <p className="mt-2 text-xs text-slate-400 text-center">
                  +{evidence.transactionIds.length - 20} additional transactions verified in backend
                </p>
              )}
            </div>
          )}
        </div>

        <div className="border-t pt-4 text-[11px] text-slate-400 text-center">
          Golden Rule: The language model never computes money. All numbers originate from verified, tested Python functions.
        </div>
      </div>
    </div>
  );
}

