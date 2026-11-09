"use client";

import React from "react";
import { WhatChanged } from "@/lib/api";
import { ArrowRight, Sparkles, TrendingUp, TrendingDown, AlertCircle, CheckCircle } from "lucide-react";

interface WhatChangedCardProps {
  whatChanged: WhatChanged | null;
  onViewEvidence?: () => void;
}

export function WhatChangedCard({ whatChanged, onViewEvidence }: WhatChangedCardProps) {
  if (!whatChanged || whatChanged.snapshot_id === null) {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 text-xs text-slate-500">
        No modifications applied yet. Apply a scenario (e.g. Add EMI, Cut Dining, Prepay Debt) to see immediate live diffs.
      </div>
    );
  }

  const scoreBefore = whatChanged.score_before;
  const scoreAfter = whatChanged.score_after;
  const delta = whatChanged.score_delta;
  const isPositive = delta !== null && delta !== undefined && delta > 0;
  const isNegative = delta !== null && delta !== undefined && delta < 0;

  return (
    <article className="rounded-2xl border-2 border-blue-600 bg-gradient-to-r from-blue-50/90 to-indigo-50/60 p-5 shadow-sm animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-blue-200/60 pb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-blue-700 animate-spin-slow" />
          <h3 className="font-bold text-slate-900">What Changed (Live Analysis Diff)</h3>
        </div>
        {onViewEvidence && (
          <button
            type="button"
            onClick={onViewEvidence}
            className="text-xs font-semibold text-blue-800 underline hover:text-blue-950"
          >
            Inspect Snapshot Diff
          </button>
        )}
      </div>

      <p className="mt-3 text-sm text-slate-800 font-medium leading-relaxed">{whatChanged.summary}</p>

      <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-xl bg-white p-3 border shadow-2xs">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">Health Score</span>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-sm text-slate-400">{scoreBefore !== null ? Math.round(scoreBefore) : "—"}</span>
            <ArrowRight className="h-3 w-3 text-slate-400" />
            <span className="text-lg font-bold text-slate-900">{scoreAfter !== null ? Math.round(scoreAfter) : "—"}</span>
            {delta !== null && delta !== undefined && (
              <span
                className={`ml-auto flex items-center text-xs font-bold ${
                  isPositive ? "text-emerald-700" : isNegative ? "text-red-700" : "text-slate-500"
                }`}
              >
                {isPositive ? <TrendingUp className="h-3.5 w-3.5 mr-0.5" /> : isNegative ? <TrendingDown className="h-3.5 w-3.5 mr-0.5" /> : null}
                {delta > 0 ? `+${delta}` : delta}
              </span>
            )}
          </div>
        </div>

        <div className="rounded-xl bg-white p-3 border shadow-2xs">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">Confidence</span>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-sm text-slate-400">{whatChanged.confidence_before ?? "—"}%</span>
            <ArrowRight className="h-3 w-3 text-slate-400" />
            <span className="text-lg font-bold text-slate-900">{whatChanged.confidence_after ?? "—"}%</span>
          </div>
        </div>

        <div className="rounded-xl bg-white p-3 border shadow-2xs">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">New Cash Gaps</span>
          <div className="mt-1 flex items-center gap-1.5">
            {whatChanged.new_gaps.length > 0 ? (
              <span className="flex items-center gap-1 text-sm font-bold text-red-600">
                <AlertCircle className="h-4 w-4" /> +{whatChanged.new_gaps.length} Danger Day(s)
              </span>
            ) : (
              <span className="text-sm font-semibold text-slate-500">None detected</span>
            )}
          </div>
        </div>

        <div className="rounded-xl bg-white p-3 border shadow-2xs">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">Advice Updated</span>
          <div className="mt-1 flex items-center gap-1.5">
            {whatChanged.recommendation_changed ? (
              <span className="flex items-center gap-1 text-sm font-bold text-blue-700">
                <CheckCircle className="h-4 w-4" /> Yes, adapted
              </span>
            ) : (
              <span className="text-sm font-semibold text-slate-500">Unchanged</span>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}

