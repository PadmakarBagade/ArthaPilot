"use client";

import React from "react";
import { Insight } from "@/lib/api";
import { AlertTriangle, Info, Sparkles, Copy, Layers, TrendingUp } from "lucide-react";

interface InsightsListProps {
  insights: Insight[];
  onEvidenceClick?: (insight: Insight) => void;
}

export function InsightsList({ insights, onEvidenceClick }: InsightsListProps) {
  if (!insights.length) {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-6 text-center text-sm text-slate-500">
        No spending anomalies or subscription leaks detected. Your accounts show regular transaction patterns.
      </div>
    );
  }

  const getIcon = (type: string) => {
    switch (type) {
      case "duplicate_charge":
        return <Copy className="h-5 w-5 text-red-600" />;
      case "overlapping_subscription":
        return <Layers className="h-5 w-5 text-amber-600" />;
      case "subscription_price_hike":
        return <TrendingUp className="h-5 w-5 text-amber-600" />;
      case "month_end_squeeze":
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case "weekend_spending_spike":
      case "post_salary_spike":
        return <Sparkles className="h-5 w-5 text-blue-600" />;
      default:
        return <Info className="h-5 w-5 text-slate-600" />;
    }
  };

  const getSeverityBadge = (severity: string) => {
    if (severity === "high") {
      return <span className="rounded-full bg-red-100 text-red-800 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5">High Risk</span>;
    }
    if (severity === "medium") {
      return <span className="rounded-full bg-amber-100 text-amber-800 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5">Attention</span>;
    }
    return <span className="rounded-full bg-slate-100 text-slate-700 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5">Notice</span>;
  };

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {insights.map((item, idx) => (
        <article
          key={`${item.type}-${idx}`}
          className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs hover:border-slate-300 transition-all flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                {getIcon(item.type)}
                <h4 className="font-bold text-slate-900 text-sm">{item.title}</h4>
              </div>
              {getSeverityBadge(item.severity)}
            </div>
            <p className="mt-2 text-xs text-slate-600 leading-relaxed font-medium">{item.message}</p>
          </div>

          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-400 font-mono">
              {item.evidence_ids.length > 0 ? `${item.evidence_ids.length} backing txns` : "Engine pattern"}
            </span>
            {onEvidenceClick && item.evidence_ids.length > 0 && (
              <button
                type="button"
                onClick={() => onEvidenceClick(item)}
                className="font-semibold text-blue-700 hover:text-blue-900 underline"
              >
                Inspect Evidence
              </button>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}
