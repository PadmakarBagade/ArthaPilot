"use client";

import React, { useState } from "react";
import { formatPaise, formatDate, Gap } from "@/lib/api";
import { AlertCircle, Calendar as CalendarIcon, CheckCircle2 } from "lucide-react";

interface DangerCalendarProps {
  dates: string[];
  p10Balances: number[];
  p50Balances: number[];
  gaps: Gap[];
  onSelectDate?: (date: string, balance: number) => void;
}

export function DangerCalendar({ dates, p10Balances, p50Balances, gaps, onSelectDate }: DangerCalendarProps) {
  const [selectedDayIndex, setSelectedDayIndex] = useState<number | null>(null);

  const gapDateSet = new Set(gaps.map((g) => g.date));

  // Show up to 35 days for a clean 5-week calendar view
  const displayDays = dates.slice(0, 35);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b pb-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <CalendarIcon className="h-5 w-5 text-blue-600" />
            <h3 className="font-bold text-slate-900">Danger Calendar (30-Day Cash-Flow Risk)</h3>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Red days indicate cash dips below your safety buffer in the 10th-percentile forecast.
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs font-medium">
          <span className="flex items-center gap-1.5 text-slate-600">
            <span className="h-3 w-3 rounded-sm bg-emerald-100 border border-emerald-300" /> Safe Path
          </span>
          <span className="flex items-center gap-1.5 text-red-700">
            <span className="h-3 w-3 rounded-sm bg-red-500 border border-red-600" /> Danger / Gap
          </span>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-1.5 sm:gap-2">
        {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => (
          <div key={day} className="text-center text-[11px] font-semibold uppercase tracking-wider text-slate-400 py-1">
            {day}
          </div>
        ))}

        {displayDays.map((isoDate, idx) => {
          const isGap = gapDateSet.has(isoDate);
          const p50 = p50Balances[idx] ?? 0;
          const dateObj = new Date(isoDate);
          const dayNum = dateObj.getDate();
          const isSelected = selectedDayIndex === idx;

          return (
            <button
              type="button"
              key={isoDate}
              onClick={() => {
                setSelectedDayIndex(idx);
                if (onSelectDate) onSelectDate(isoDate, p50);
              }}
              className={`group relative flex flex-col items-center justify-center p-2 rounded-lg border transition-all text-center min-h-[58px] ${
                isGap
                  ? "bg-red-50 border-red-300 hover:bg-red-100 text-red-950 font-semibold"
                  : "bg-slate-50 border-slate-200 hover:bg-blue-50 text-slate-800"
              } ${isSelected ? "ring-2 ring-blue-600 border-blue-600" : ""}`}
            >
              <span className="text-xs font-bold">{dayNum}</span>
              <span className={`text-[10px] mt-0.5 truncate max-w-full ${isGap ? "text-red-700 font-bold" : "text-slate-500"}`}>
                {formatPaise(p50).slice(0, 7)}
              </span>
              {isGap && (
                <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-600 animate-pulse" />
              )}
            </button>
          );
        })}
      </div>

      {selectedDayIndex !== null && (
        <div className="mt-4 rounded-lg bg-slate-50 border p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
          <div>
            <span className="font-bold text-slate-900">{formatDate(dates[selectedDayIndex])}</span>
            <span className="text-slate-500 ml-2">
              Likely: <strong className="text-slate-900">{formatPaise(p50Balances[selectedDayIndex])}</strong> · Worst case:{" "}
              <strong className="text-slate-900">{formatPaise(p10Balances[selectedDayIndex])}</strong>
            </span>
          </div>
          {gapDateSet.has(dates[selectedDayIndex]) ? (
            <span className="flex items-center gap-1 font-semibold text-red-700">
              <AlertCircle className="h-4 w-4" /> Buffer breached!
            </span>
          ) : (
            <span className="flex items-center gap-1 font-semibold text-emerald-700">
              <CheckCircle2 className="h-4 w-4" /> Healthy balance
            </span>
          )}
        </div>
      )}
    </div>
  );
}
