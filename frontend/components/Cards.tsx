"use client";

import React from "react";
import { CheckCircle2, AlertTriangle, XCircle, Info, Sparkles, TrendingUp } from "lucide-react";

interface FactCardProps {
  text: string;
  evidenceIds?: string[];
  onEvidenceClick?: () => void;
}

export function FactCard({ text, evidenceIds = [], onEvidenceClick }: FactCardProps) {
  return (
    <article className="rounded-xl border-l-4 border-blue-600 bg-blue-50/70 p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-blue-700">
          <Info className="h-3.5 w-3.5" />
          Observed Fact
        </span>
        {evidenceIds.length > 0 && onEvidenceClick && (
          <button
            type="button"
            onClick={onEvidenceClick}
            className="text-[11px] font-medium text-blue-700 underline hover:text-blue-900"
          >
            {evidenceIds.length} Evidence IDs
          </button>
        )}
      </div>
      <p className="mt-2 text-sm text-slate-800 leading-relaxed font-medium">{text}</p>
    </article>
  );
}

interface PredictionCardProps {
  text: string;
  confidence: number;
  reasons?: string[];
}

export function PredictionCard({ text, confidence, reasons = [] }: PredictionCardProps) {
  return (
    <article className="rounded-xl border-l-4 border-amber-500 bg-amber-50/70 p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-amber-800">
          <TrendingUp className="h-3.5 w-3.5" />
          Prediction
        </span>
        <span className="inline-flex items-center rounded-full bg-amber-200/80 px-2 py-0.5 text-xs font-semibold text-amber-900">
          {confidence}% Confidence
        </span>
      </div>
      <p className="mt-2 text-sm text-slate-800 leading-relaxed font-medium">{text}</p>
      {reasons.length > 0 && (
        <p className="mt-1 text-xs text-amber-700 truncate">Basis: {reasons.join(", ")}</p>
      )}
    </article>
  );
}

interface RecommendationCardProps {
  text: string;
  impact?: Record<string, unknown>;
  onSimulate?: () => void;
}

export function RecommendationCard({ text, impact, onSimulate }: RecommendationCardProps) {
  return (
    <article className="rounded-xl border-l-4 border-emerald-600 bg-emerald-50/70 p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-emerald-800">
          <Sparkles className="h-3.5 w-3.5" />
          Recommendation
        </span>
        {onSimulate && (
          <button
            type="button"
            onClick={onSimulate}
            className="text-[11px] font-semibold text-emerald-800 underline hover:text-emerald-950"
          >
            Simulate Path
          </button>
        )}
      </div>
      <p className="mt-2 text-sm text-slate-800 leading-relaxed font-medium">{text}</p>
      {impact && Object.keys(impact).length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1 text-[11px] text-emerald-900 font-medium">
          {Object.entries(impact)
            .filter(([k]) => !["formula", "evidence"].includes(k))
            .slice(0, 2)
            .map(([k, v]) => (
              <span key={k} className="rounded bg-emerald-200/60 px-1.5 py-0.5">
                {k}: {String(v)}
              </span>
            ))}
        </div>
      )}
    </article>
  );
}

interface VerdictCardProps {
  verdict: "Yes" | "Risky" | "No";
  title?: string;
  reason?: string;
  saferAlternative?: string | null;
}

export function VerdictCard({ verdict, title, reason, saferAlternative }: VerdictCardProps) {
  const configs = {
    Yes: {
      border: "border-emerald-500",
      bg: "bg-emerald-50",
      text: "text-emerald-800",
      badge: "bg-emerald-600 text-white",
      icon: CheckCircle2,
      label: "Affordable & Safe",
    },
    Risky: {
      border: "border-amber-500",
      bg: "bg-amber-50",
      text: "text-amber-800",
      badge: "bg-amber-600 text-white",
      icon: AlertTriangle,
      label: "Risky / Tight Buffer",
    },
    No: {
      border: "border-red-500",
      bg: "bg-red-50",
      text: "text-red-800",
      badge: "bg-red-600 text-white",
      icon: XCircle,
      label: "Not Recommended",
    },
  };

  const config = configs[verdict] || configs.Risky;
  const Icon = config.icon;

  return (
    <div className={`rounded-xl border ${config.border} ${config.bg} p-5 shadow-sm`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className={`h-6 w-6 ${config.text}`} />
          <h3 className="text-lg font-bold text-slate-900">{title || `Verdict: ${verdict}`}</h3>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wider ${config.badge}`}>
          {config.label}
        </span>
      </div>
      {reason && <p className="mt-3 text-sm text-slate-700 leading-relaxed font-medium">{reason}</p>}
      {saferAlternative && (
        <div className="mt-3 rounded-lg bg-white/80 border p-3">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Safer Alternative</p>
          <p className="mt-1 text-xs text-slate-800 font-medium">{saferAlternative}</p>
        </div>
      )}
    </div>
  );
}

