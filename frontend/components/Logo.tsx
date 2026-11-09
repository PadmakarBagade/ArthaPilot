"use client";

import React from "react";

type LogoVariant = "full" | "mark";
type LogoSize = "xs" | "sm" | "md" | "lg" | "xl";

interface LogoProps {
  variant?: LogoVariant;
  size?: LogoSize;
  className?: string;
  /** Force text to be a specific color (defaults to white) */
  textColor?: string;
}

const sizeMap: Record<LogoSize, { icon: number; text: string; sub: string }> = {
  xs: { icon: 24, text: "text-sm", sub: "text-[8px]" },
  sm: { icon: 32, text: "text-base", sub: "text-[9px]" },
  md: { icon: 40, text: "text-xl", sub: "text-[10px]" },
  lg: { icon: 52, text: "text-2xl", sub: "text-xs" },
  xl: { icon: 72, text: "text-4xl", sub: "text-sm" },
};

/** ArthaPilot SVG logomark — compass needle + ascending trend + shield */
export function LogoMark({ size = 40, className = "" }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="ArthaPilot logo"
    >
      <defs>
        <linearGradient id="ap-shield-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#3B82F6" />
          <stop offset="100%" stopColor="#6366F1" />
        </linearGradient>
        <linearGradient id="ap-arrow-grad" x1="0" y1="1" x2="1" y2="0">
          <stop offset="0%" stopColor="#38BDF8" />
          <stop offset="100%" stopColor="#A5F3FC" />
        </linearGradient>
      </defs>

      {/* Shield body */}
      <path
        d="M24 4L7 11v13c0 9.5 7.3 18.4 17 21 9.7-2.6 17-11.5 17-21V11L24 4z"
        fill="url(#ap-shield-grad)"
        opacity="0.95"
      />

      {/* Inner shield highlight */}
      <path
        d="M24 8.5L10 14.5v9.8c0 7.3 5.6 14.1 14 16.3 8.4-2.2 14-9 14-16.3v-9.8L24 8.5z"
        fill="white"
        fillOpacity="0.08"
      />

      {/* Trending up line chart (ascending bars inside shield) */}
      <rect x="13" y="30" width="4" height="6" rx="1" fill="white" fillOpacity="0.95" />
      <rect x="19" y="25" width="4" height="11" rx="1" fill="white" fillOpacity="0.95" />
      <rect x="25" y="19" width="4" height="17" rx="1" fill="white" fillOpacity="0.95" />

      {/* Upward arrow tip on the rightmost bar */}
      <path
        d="M31 15l3.5 5h-7L31 15z"
        fill="url(#ap-arrow-grad)"
      />
      {/* Connector line */}
      <line x1="31" y1="20" x2="31" y2="36" stroke="url(#ap-arrow-grad)" strokeWidth="4" strokeLinecap="round" />

      {/* Compass needle dot at top of shield */}
      <circle cx="24" cy="12" r="2" fill="white" fillOpacity="0.7" />
    </svg>
  );
}

/** Full brand logo with text */
export function Logo({ variant = "full", size = "md", className = "" }: LogoProps) {
  const { icon, text, sub } = sizeMap[size];

  if (variant === "mark") {
    return <LogoMark size={icon} className={className} />;
  }

  return (
    <div className={`flex items-center gap-2.5 select-none ${className}`}>
      <LogoMark size={icon} />
      <div className="flex flex-col leading-none">
        <span className={`${text} font-black tracking-tight text-white`}>
          Artha<span className="text-blue-400">Pilot</span>
        </span>
        <span className={`${sub} text-slate-400 font-semibold tracking-wide mt-0.5`}>
          अर्थपायलट · Financial Health Copilot
        </span>
      </div>
    </div>
  );
}

export default Logo;

