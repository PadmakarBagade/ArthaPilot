"use client";

import React from "react";

interface ScoreRingProps {
  score: number | null | undefined;
  band?: string;
  size?: number;
  strokeWidth?: number;
  label?: string;
  onClick?: () => void;
}

export function ScoreRing({
  score,
  band = "Waiting for data",
  size = 140,
  strokeWidth = 12,
  label = "Health Score",
  onClick,
}: ScoreRingProps) {
  const validScore = score !== null && score !== undefined && !isNaN(score) ? Math.min(100, Math.max(0, score)) : null;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = validScore !== null ? circumference - (validScore / 100) * circumference : circumference;

  let colorClass = "stroke-slate-300 text-slate-400";
  let ringBg = "text-slate-100";
  if (validScore !== null) {
    if (validScore >= 75) {
      colorClass = "stroke-emerald-600 text-emerald-600";
      ringBg = "text-emerald-50";
    } else if (validScore >= 55) {
      colorClass = "stroke-blue-600 text-blue-600";
      ringBg = "text-blue-50";
    } else {
      colorClass = "stroke-amber-600 text-amber-600";
      ringBg = "text-amber-50";
    }
  }

  return (
    <div
      className={`flex flex-col items-center justify-center ${onClick ? "cursor-pointer hover:opacity-95" : ""}`}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className={`${ringBg} fill-none`}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={`${colorClass} fill-none transition-all duration-700 ease-out`}
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-3xl font-bold tracking-tight text-slate-900">
            {validScore !== null ? Math.round(validScore) : "—"}
          </span>
          <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500">out of 100</span>
        </div>
      </div>
      <div className="mt-2 text-center">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</p>
        <p className="text-sm font-medium text-slate-800">{band}</p>
      </div>
    </div>
  );
}

