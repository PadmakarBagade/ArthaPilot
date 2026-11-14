"use client";

import React, { useState, useEffect, useRef } from "react";

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

  // Animated stroke offset: starts at circumference (empty), animates to target
  const [animatedScore, setAnimatedScore] = useState(0);
  const [hovered, setHovered] = useState(false);
  const animRef = useRef<number | null>(null);

  useEffect(() => {
    if (validScore === null) return;
    // Animate from 0 → validScore on mount / change
    const duration = 1000;
    const startTime = performance.now();
    const startScore = 0;
    const tick = (now: number) => {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setAnimatedScore(Math.round(eased * (validScore - startScore) + startScore));
      if (progress < 1) {
        animRef.current = requestAnimationFrame(tick);
      }
    };
    animRef.current = requestAnimationFrame(tick);
    return () => {
      if (animRef.current !== null) cancelAnimationFrame(animRef.current);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [validScore]);

  const displayScore = hovered ? validScore : animatedScore;
  const strokeDashoffset =
    displayScore !== null ? circumference - (displayScore / 100) * circumference : circumference;

  // Colors by score band
  let ringColor = "#94a3b8"; // slate-400
  let bgColor = "#f1f5f9";   // slate-100
  let textColor = "text-slate-700";
  let bandColor = "text-slate-500";
  if (validScore !== null) {
    if (validScore >= 75) {
      ringColor = "#059669";   // emerald-600
      bgColor = "#ecfdf5";
      textColor = "text-emerald-700";
      bandColor = "text-emerald-600";
    } else if (validScore >= 55) {
      ringColor = "#2563eb";   // blue-600
      bgColor = "#eff6ff";
      textColor = "text-blue-700";
      bandColor = "text-blue-600";
    } else {
      ringColor = "#d97706";   // amber-600
      bgColor = "#fffbeb";
      textColor = "text-amber-700";
      bandColor = "text-amber-600";
    }
  }

  return (
    <div
      className={`flex flex-col items-center justify-center group ${onClick ? "cursor-pointer" : ""}`}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div
        className={`relative flex items-center justify-center transition-transform duration-300 ${hovered ? "scale-105" : "scale-100"}`}
        style={{ width: size, height: size }}
      >
        {/* Hover glow ring */}
        {hovered && (
          <div
            className="absolute rounded-full opacity-20 blur-md transition-opacity duration-300"
            style={{
              width: size + 16,
              height: size + 16,
              top: -8,
              left: -8,
              background: ringColor,
            }}
          />
        )}

        <svg width={size} height={size} className="-rotate-90">
          {/* Background track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={bgColor}
            strokeWidth={strokeWidth}
            fill="none"
          />
          {/* Animated score arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={ringColor}
            strokeWidth={hovered ? strokeWidth + 2 : strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="none"
            style={{ transition: "stroke-dashoffset 0.6s ease-out, stroke-width 0.3s ease" }}
          />
        </svg>

        {/* Center text */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className={`text-3xl font-bold tracking-tight ${textColor} transition-all duration-300`}>
            {validScore !== null ? Math.round(displayScore ?? 0) : "—"}
          </span>
          <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500">out of 100</span>
          {/* Show "hover" tooltip hint on hover */}
          {hovered && validScore !== null && (
            <span className={`text-[9px] font-bold uppercase ${bandColor} mt-0.5 opacity-80`}>
              {band.split(" ")[0]}
            </span>
          )}
        </div>
      </div>

      <div className="mt-2 text-center">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</p>
        <p className={`text-sm font-medium ${bandColor}`}>{band}</p>
        {/* Score breakdown bar on hover */}
        {hovered && validScore !== null && (
          <div className="mt-2 w-full">
            <div className="h-1 w-32 mx-auto rounded-full bg-slate-200 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{ width: `${validScore}%`, backgroundColor: ringColor }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
