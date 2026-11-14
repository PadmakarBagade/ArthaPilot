"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Logo } from "@/components/Logo";
import {
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Lock,
  Layers,
  Database,
  Calculator,
  LineChart,
  Bot,
  Zap,
  ChevronRight,
  TrendingUp,
  Lightbulb,
  Check,
  UserCheck,
  Target,
  Brain,
  RefreshCw,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/* Animated counter hook                                               */
/* ------------------------------------------------------------------ */
function useCountUp(target: number, duration = 1200, startOnMount = true) {
  const [value, setValue] = useState(0);
  const started = useRef(false);
  useEffect(() => {
    if (!startOnMount || started.current) return;
    started.current = true;
    const startTime = performance.now();
    const tick = (now: number) => {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [target, duration, startOnMount]);
  return value;
}

/* ------------------------------------------------------------------ */
/* Block definitions                                                    */
/* ------------------------------------------------------------------ */
const blocks = [
  {
    num: 1,
    layer: "Input Layer",
    title: "Data Ingestion",
    desc: "Accepts bank statements in CSV, XLSX, and PDF format. Deduplicates records, parses Indian dates, and standardises all monetary figures into integer paise (₹1 = 100 paise) to eliminate floating-point math errors.",
    footer: "Tables: Transactions, Loans, Cards, Investments",
    icon: Database,
    accent: {
      tag: "text-blue-400",
      icon: "text-blue-400",
      iconBg: "bg-blue-600/20 border-blue-500/30",
      border: "hover:border-blue-500",
      glow: "hover:shadow-blue-500/20",
      bar: "bg-blue-500",
      grad: "from-blue-600/10 to-transparent",
      ring: "group-hover:ring-blue-500/30",
    },
    progress: 95,
  },
  {
    num: 2,
    layer: "Understanding Layer",
    title: "Categorisation & Recurring",
    desc: 'Cleans messy merchant names (e.g. "SWIGGY*ORDER 4482" → Swiggy). Runs rule cascade + ML classifier. Detects recurring subscriptions (Netflix, SIP, rent, EMIs) with interval cadences and flags salary vs. irregular income.',
    footer: "Outputs: Tagged Transactions & Known Recurring Bills",
    icon: Layers,
    accent: {
      tag: "text-purple-400",
      icon: "text-purple-400",
      iconBg: "bg-purple-600/20 border-purple-500/30",
      border: "hover:border-purple-500",
      glow: "hover:shadow-purple-500/20",
      bar: "bg-purple-500",
      grad: "from-purple-600/10 to-transparent",
      ring: "group-hover:ring-purple-500/30",
    },
    progress: 88,
  },
  {
    num: 3,
    layer: "Analytics Layer",
    title: "Financial Health Engine",
    desc: "Computes 6 weighted core metrics: Savings Rate, Debt-to-Income (DTI), Emergency Fund Runway, Fixed vs Variable Ratio, Credit Card Utilisation, and Spending Volatility into a single 0–100 score with full audit breakdown.",
    footer: "Outputs: 0–100 Health Score + Metric Provenance",
    icon: Calculator,
    accent: {
      tag: "text-emerald-400",
      icon: "text-emerald-400",
      iconBg: "bg-emerald-600/20 border-emerald-500/30",
      border: "hover:border-emerald-500",
      glow: "hover:shadow-emerald-500/20",
      bar: "bg-emerald-500",
      grad: "from-emerald-600/10 to-transparent",
      ring: "group-hover:ring-emerald-500/30",
    },
    progress: 100,
  },
  {
    num: 4,
    layer: "Future Layer",
    title: "Prediction Engine",
    desc: "1,000-run Monte Carlo simulation forecasts cash flow over 30, 60, or 90 days using recurring bills, expected paydays, and bootstrapped variable spending distributions. Automatically flags future danger days where balances dip below zero.",
    footer: "Outputs: 30/60/90-Day P10/P50/P90 Bands + Cash Gaps",
    icon: LineChart,
    accent: {
      tag: "text-amber-400",
      icon: "text-amber-400",
      iconBg: "bg-amber-600/20 border-amber-500/30",
      border: "hover:border-amber-500",
      glow: "hover:shadow-amber-500/20",
      bar: "bg-amber-500",
      grad: "from-amber-600/10 to-transparent",
      ring: "group-hover:ring-amber-500/30",
    },
    progress: 82,
  },
  {
    num: 5,
    layer: "Action Layer",
    title: "Recommendation & Simulator",
    desc: "Ranks high-impact actions (Avalanche debt payoff, subscription pruning, SIP reallocation, deferring large purchases). Re-runs the entire mathematical model to show side-by-side Before vs After score, savings, and runway changes.",
    footer: "Outputs: Side-by-side Before/After Simulation Diffs",
    icon: Zap,
    accent: {
      tag: "text-cyan-400",
      icon: "text-cyan-400",
      iconBg: "bg-cyan-600/20 border-cyan-500/30",
      border: "hover:border-cyan-500",
      glow: "hover:shadow-cyan-500/20",
      bar: "bg-cyan-500",
      grad: "from-cyan-600/10 to-transparent",
      ring: "group-hover:ring-cyan-500/30",
    },
    progress: 78,
  },
  {
    num: 6,
    layer: "Conversational Layer",
    title: "Conversational Copilot",
    desc: "Accepts natural language queries in English, Hindi, and Marathi. The LLM acts purely as a semantic router: it selects the Python tool, executes verified code on real data, and translates verified numbers into the mandatory 3-section format.",
    footer: "Rule: Zero Math Hallucinations Allowed",
    icon: Bot,
    accent: {
      tag: "text-indigo-400",
      icon: "text-indigo-400",
      iconBg: "bg-indigo-600/20 border-indigo-500/30",
      border: "hover:border-indigo-500",
      glow: "hover:shadow-indigo-500/20",
      bar: "bg-indigo-500",
      grad: "from-indigo-600/10 to-transparent",
      ring: "group-hover:ring-indigo-500/30",
    },
    progress: 91,
  },
];

/* ------------------------------------------------------------------ */
/* BuildingBlockCard with rich hover effects                            */
/* ------------------------------------------------------------------ */
function BuildingBlockCard({ block }: { block: (typeof blocks)[0] }) {
  const [hovered, setHovered] = useState(false);
  const [barWidth, setBarWidth] = useState(0);
  const Icon = block.icon;

  useEffect(() => {
    if (hovered) {
      const t = setTimeout(() => setBarWidth(block.progress), 60);
      return () => clearTimeout(t);
    } else {
      setBarWidth(0);
    }
  }, [hovered, block.progress]);

  return (
    <div
      className={`
        group relative rounded-2xl border border-slate-800 bg-slate-900/60 p-6 flex flex-col justify-between
        transition-all duration-300 cursor-default overflow-hidden
        hover:shadow-xl ${block.accent.glow}
        ${block.accent.border}
        ring-1 ring-transparent ${block.accent.ring}
      `}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Gradient glow overlay on hover */}
      <div
        className={`absolute inset-0 bg-gradient-to-br ${block.accent.grad} opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none rounded-2xl`}
      />

      {/* Animated border sweep line (top) */}
      <div
        className="absolute top-0 left-0 h-0.5 bg-gradient-to-r from-transparent via-current to-transparent transition-all duration-500 opacity-0 group-hover:opacity-100"
        style={{
          width: hovered ? "100%" : "0%",
          color: "inherit",
        }}
      />

      <div className="relative z-10">
        {/* Icon with pop + glow on hover */}
        <div
          className={`
            h-11 w-11 rounded-xl border flex items-center justify-center mb-4
            ${block.accent.iconBg} ${block.accent.icon}
            transition-all duration-300
            group-hover:scale-110 group-hover:rotate-3 group-hover:shadow-lg
          `}
        >
          <Icon className="h-5 w-5" />
        </div>

        <div className={`text-[11px] font-bold uppercase tracking-wider ${block.accent.tag}`}>
          Block {block.num}: {block.layer}
        </div>
        <h3 className="text-lg font-bold text-white mt-1 group-hover:text-white transition-colors">{block.title}</h3>
        <p className="text-xs text-slate-400 mt-2.5 leading-relaxed group-hover:text-slate-300 transition-colors">
          {block.desc}
        </p>
      </div>

      {/* Footer with animated progress bar */}
      <div className="relative z-10 mt-5 pt-3 border-t border-slate-800">
        <div className="text-[11px] font-semibold text-slate-500 group-hover:text-slate-400 transition-colors mb-2">
          {block.footer}
        </div>
        {/* Progress bar — fills on hover */}
        <div className="h-1 w-full rounded-full bg-slate-800 overflow-hidden">
          <div
            className={`h-full rounded-full ${block.accent.bar} transition-all duration-700 ease-out`}
            style={{ width: `${barWidth}%` }}
          />
        </div>
        <div
          className={`mt-1 text-[10px] font-bold ${block.accent.tag} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
        >
          {block.progress}% complete
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main Page                                                           */
/* ------------------------------------------------------------------ */
export default function LandingPage() {
  const router = useRouter();
  const { user, demoLogin } = useAuth();
  const [loadingPersona, setLoadingPersona] = useState<string | null>(null);
  const scoreCount = useCountUp(74, 1400);

  const handleQuickDemo = async (personaId: string) => {
    setLoadingPersona(personaId);
    try {
      await demoLogin(personaId);
      router.push("/dashboard");
    } catch {
      router.push(`/dashboard`);
    } finally {
      setLoadingPersona(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-blue-600 selection:text-white">

      {/* ============================================================== */}
      {/* 1. NAVBAR                                                       */}
      {/* ============================================================== */}
      <nav className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 group">
            <Logo size="sm" />
          </Link>

          <div className="hidden md:flex items-center gap-7 text-xs font-semibold text-slate-300">
            <a href="#blocks" className="hover:text-blue-400 transition-colors">
              6 Building Blocks
            </a>
            <a href="#three-sections" className="hover:text-blue-400 transition-colors">
              Fact / Prediction / Action
            </a>
            <a href="#dynamic-update" className="hover:text-blue-400 transition-colors">
              Dynamic Update
            </a>
            <a href="#personas" className="hover:text-blue-400 transition-colors">
              Personas
            </a>
            <a href="#trust" className="hover:text-blue-400 transition-colors">
              Trust &amp; Privacy
            </a>
          </div>

          <div className="flex items-center gap-3">
            {user ? (
              <Link
                href="/dashboard"
                className="flex items-center gap-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-blue-600/30 transition-all"
              >
                <span>Go to Dashboard</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            ) : (
              <>
                <Link
                  href="/login"
                  className="rounded-xl border border-slate-700 bg-slate-900/80 hover:bg-slate-800 px-3.5 py-2 text-xs font-semibold text-slate-200 transition-all"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="hidden sm:inline-flex rounded-xl bg-blue-600 hover:bg-blue-500 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-blue-600/30 transition-all"
                >
                  Get Started Free
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* ============================================================== */}
      {/* 2. HERO SECTION                                                 */}
      {/* ============================================================== */}
      <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-28">
        {/* Glow backdrop effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-blue-600/15 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute top-1/3 left-1/4 -translate-y-1/2 w-[400px] h-[300px] bg-indigo-600/10 blur-[100px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto">
            {/* Pill badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-950/40 px-3.5 py-1 text-xs font-semibold text-blue-300 mb-6 backdrop-blur-md">
              <Sparkles className="h-3.5 w-3.5 text-blue-400" />
              <span>India&apos;s 1st Deterministic Financial Health Copilot</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-tight">
              One Unified Health Picture.{" "}
              <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-400 bg-clip-text text-transparent">
                Zero Financial Hallucinations.
              </span>
            </h1>

            <p className="mt-5 text-base sm:text-lg text-slate-300 leading-relaxed">
              Upload bank statements, connect loans &amp; investments, see your 0–100 Health Score, forecast cash
              shortfalls with Monte Carlo bands, and simulate every money move — with strict separation of{" "}
              <strong className="text-blue-400">Fact</strong>, <strong className="text-amber-400">Prediction</strong>, and{" "}
              <strong className="text-emerald-400">Recommendation</strong>.
            </p>

            {/* CTAs */}
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3.5">
              <Link
                href="/dashboard"
                className="flex items-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-500 px-6 py-3.5 text-sm font-bold text-white shadow-xl shadow-blue-600/30 transition-all hover:scale-[1.02]"
              >
                <span>Launch Interactive Copilot</span>
                <ArrowRight className="h-4 w-4" />
              </Link>

              <button
                type="button"
                onClick={() => handleQuickDemo("rahul")}
                disabled={loadingPersona !== null}
                className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/90 hover:bg-slate-800 px-5 py-3.5 text-sm font-bold text-slate-200 transition-all hover:border-slate-600"
              >
                <UserCheck className="h-4 w-4 text-blue-400" />
                <span>{loadingPersona ? "Loading..." : "Try Rahul's Demo (1-Click)"}</span>
              </button>
            </div>

            {/* Core Guarantee Micro-badges */}
            <div className="mt-8 pt-6 border-t border-slate-800/80 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-blue-400" />
                <span>Deterministic Python Engine</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <span>Exact Integer Paise Arithmetic (₹)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-purple-400" />
                <span>Local-First Private Data</span>
              </div>
            </div>
          </div>

          {/* Interactive Hero Preview Widget */}
          <div className="mt-14 rounded-3xl border border-slate-800 bg-slate-900/70 p-4 sm:p-7 shadow-2xl backdrop-blur-xl">
            <div className="grid gap-6 md:grid-cols-12 items-center">
              {/* Left: Live Score Preview */}
              <div className="md:col-span-4 rounded-2xl bg-slate-950/80 border border-slate-800 p-5 flex flex-col items-center justify-center text-center">
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Live Composite Score
                </div>
                <div className="relative my-2 flex items-center justify-center">
                  <div className="h-32 w-32 rounded-full border-8 border-blue-500/20 border-t-blue-500 flex flex-col items-center justify-center animate-spin-slow" style={{ animation: 'none' }}>
                    <span className="text-3xl font-black text-white">{scoreCount}</span>
                    <span className="text-[10px] font-bold text-blue-400 uppercase">Good Band</span>
                  </div>
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  Calculated across Savings Rate (38%), DTI (16%), and 4.2 months Emergency Runway.
                </p>
                <Link
                  href="/dashboard"
                  className="mt-4 text-xs font-bold text-blue-400 hover:text-blue-300 inline-flex items-center gap-1"
                >
                  Explore Metric Provenance <ChevronRight className="h-3 w-3" />
                </Link>
              </div>

              {/* Right: Mandatory 3-Section Live Card */}
              <div className="md:col-span-8 space-y-3">
                <div className="flex items-center justify-between text-xs font-bold text-slate-400">
                  <span className="flex items-center gap-1.5">
                    <Bot className="h-4 w-4 text-blue-400" />
                    Copilot Query: &quot;Can I afford a ₹45,000 laptop this month?&quot;
                  </span>
                  <span className="rounded-md bg-amber-500/20 border border-amber-500/30 px-2 py-0.5 text-[10px] font-bold text-amber-300">
                    Verdict: Risky
                  </span>
                </div>

                <div className="grid gap-2.5 sm:grid-cols-3">
                  {/* Fact Card (Blue) */}
                  <div className="rounded-xl border border-blue-500/30 bg-blue-950/30 p-3.5 text-left hover:border-blue-500/60 hover:bg-blue-950/50 transition-all">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-blue-400 mb-1">
                      <Check className="h-3.5 w-3.5" />
                      <span>Observed Fact</span>
                    </div>
                    <p className="text-xs text-slate-200">
                      Liquid savings before purchase is ₹32,000. Required safe buffer is ₹15,000.
                    </p>
                    <span className="mt-2 text-[10px] text-blue-400/80 font-mono block">
                      Ref: accounts_table#primary
                    </span>
                  </div>

                  {/* Prediction Card (Orange) */}
                  <div className="rounded-xl border border-amber-500/30 bg-amber-950/30 p-3.5 text-left hover:border-amber-500/60 hover:bg-amber-950/50 transition-all">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-amber-400 mb-1">
                      <TrendingUp className="h-3.5 w-3.5" />
                      <span>Prediction (82% Conf)</span>
                    </div>
                    <p className="text-xs text-slate-200">
                      Balance will dip to -₹13,000 on the 24th due to recurring rent &amp; EMI obligations.
                    </p>
                    <span className="mt-2 text-[10px] text-amber-400/80 font-mono block">
                      Confidence: 12 mos data
                    </span>
                  </div>

                  {/* Recommendation Card (Green) */}
                  <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/30 p-3.5 text-left hover:border-emerald-500/60 hover:bg-emerald-950/50 transition-all">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400 mb-1">
                      <Lightbulb className="h-3.5 w-3.5" />
                      <span>Recommendation</span>
                    </div>
                    <p className="text-xs text-slate-200">
                      Defer purchase by 12 days to next salary cycle, or opt for a 0% no-cost 6-month EMI.
                    </p>
                    <span className="mt-2 text-[10px] text-emerald-400 font-bold block">
                      Impact: Gap avoided
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 3. THE BIG IDEA — REDESIGNED                                   */}
      {/* ============================================================== */}
      <section className="py-20 relative overflow-hidden border-y border-slate-800">
        {/* Layered glowing backgrounds */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-950/40 via-slate-950 to-indigo-950/30 pointer-events-none" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-700/10 blur-[100px] rounded-full pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 w-72 h-72 bg-indigo-700/10 blur-[80px] rounded-full pointer-events-none" />

        <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6">
          {/* Section label */}
          <div className="flex items-center justify-center gap-3 mb-10">
            <div className="h-px flex-1 bg-gradient-to-r from-transparent to-blue-500/40" />
            <span className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-widest text-blue-400 bg-blue-950/60 border border-blue-500/20 px-4 py-1.5 rounded-full">
              <Brain className="h-3.5 w-3.5" />
              The Big Idea
            </span>
            <div className="h-px flex-1 bg-gradient-to-l from-transparent to-blue-500/40" />
          </div>

          {/* Main 2-column layout */}
          <div className="grid gap-8 lg:grid-cols-2 items-center">
            {/* LEFT: Statement */}
            <div className="space-y-6">
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white leading-tight">
                One App.
                <br />
                <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-400 bg-clip-text text-transparent">
                  Three Truths.
                </span>
                <br />
                <span className="text-slate-300 text-2xl sm:text-3xl font-bold">Zero Hallucinated Math.</span>
              </h2>

              <p className="text-sm text-slate-300 leading-relaxed max-w-lg">
                A local-first web app where you upload financial data, see one unified health picture, ask questions
                in plain English, and get answers that cleanly separate{" "}
                <span className="font-bold text-blue-400 underline decoration-blue-500/40 underline-offset-4">what happened</span>,{" "}
                <span className="font-bold text-amber-400 underline decoration-amber-500/40 underline-offset-4">what is predicted</span>, and{" "}
                <span className="font-bold text-emerald-400 underline decoration-emerald-500/40 underline-offset-4">what you should do</span>{" "}
                — each with simulated impact and verified confidence.
              </p>

              {/* Key stats bar */}
              <div className="grid grid-cols-3 gap-3 pt-2">
                {[
                  { value: "105+", label: "Tests Passing", color: "text-blue-400", bg: "bg-blue-500/10 border-blue-500/20" },
                  { value: "0", label: "LLM Math Calls", color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/20" },
                  { value: "5", label: "Realistic Personas", color: "text-purple-400", bg: "bg-purple-500/10 border-purple-500/20" },
                ].map((s) => (
                  <div key={s.label} className={`rounded-xl border ${s.bg} px-3 py-3 text-center`}>
                    <div className={`text-2xl font-black ${s.color}`}>{s.value}</div>
                    <div className="text-[10px] text-slate-400 font-semibold mt-0.5">{s.label}</div>
                  </div>
                ))}
              </div>

              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-blue-600/30 transition-all hover:scale-[1.02]"
              >
                <Sparkles className="h-4 w-4" />
                Experience the Copilot
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>

            {/* RIGHT: Animated mini Fact/Prediction/Recommendation preview */}
            <div className="relative">
              {/* Animated gradient border card */}
              <div className="relative rounded-2xl p-[2px] bg-gradient-to-br from-blue-500/60 via-indigo-500/40 to-emerald-500/40">
                <div className="rounded-2xl bg-slate-950/95 p-6 space-y-4">
                  {/* Header */}
                  <div className="flex items-center gap-2.5 pb-3 border-b border-slate-800">
                    <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">ArthaPilot Copilot</div>
                      <div className="text-[10px] text-slate-400">Query: &quot;Will I run short before salary?&quot;</div>
                    </div>
                    <span className="ml-auto rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-bold px-2 py-0.5 border border-emerald-500/30">
                      ● Live
                    </span>
                  </div>

                  {/* Fact */}
                  <div className="rounded-xl bg-blue-950/40 border border-blue-500/30 p-3.5 group/fact hover:border-blue-400/60 hover:bg-blue-950/60 transition-all cursor-default">
                    <div className="flex items-center gap-1.5 text-blue-400 text-[11px] font-bold mb-1.5">
                      <Check className="h-3 w-3" />
                      <span>✅ Observed Fact</span>
                      <span className="ml-auto text-[10px] text-blue-400/60 font-mono">100% provenance</span>
                    </div>
                    <p className="text-xs text-slate-200">Current balance: ₹8,340. Next salary in 6 days. Fixed obligations due: ₹14,200.</p>
                  </div>

                  {/* Prediction */}
                  <div className="rounded-xl bg-amber-950/40 border border-amber-500/30 p-3.5 hover:border-amber-400/60 hover:bg-amber-950/60 transition-all cursor-default">
                    <div className="flex items-center gap-1.5 text-amber-400 text-[11px] font-bold mb-1.5">
                      <TrendingUp className="h-3 w-3" />
                      <span>🔮 Prediction</span>
                      <span className="ml-auto text-[10px] text-amber-400 font-bold">Confidence: 76%</span>
                    </div>
                    <p className="text-xs text-slate-200">Balance may dip to -₹5,860 on the 23rd. Overdraft risk: 61%.</p>
                  </div>

                  {/* Recommendation */}
                  <div className="rounded-xl bg-emerald-950/40 border border-emerald-500/30 p-3.5 hover:border-emerald-400/60 hover:bg-emerald-950/60 transition-all cursor-default">
                    <div className="flex items-center gap-1.5 text-emerald-400 text-[11px] font-bold mb-1.5">
                      <Lightbulb className="h-3 w-3" />
                      <span>💡 Recommendation</span>
                      <span className="ml-auto text-[10px] text-emerald-400 font-bold">Impact: Gap avoided</span>
                    </div>
                    <p className="text-xs text-slate-200">Defer ₹3,000 OTT subscription renewal by 7 days. Runway: 1.8 → 2.3 months.</p>
                  </div>
                </div>
              </div>

              {/* Floating decoration */}
              <div className="absolute -top-3 -right-3 h-6 w-6 rounded-full bg-blue-500 opacity-60 blur-sm animate-pulse" />
              <div className="absolute -bottom-3 -left-3 h-4 w-4 rounded-full bg-indigo-500 opacity-50 blur-sm animate-pulse" style={{ animationDelay: '1s' }} />
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 4. THE 6 BUILDING BLOCKS                                        */}
      {/* ============================================================== */}
      <section id="blocks" className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <span className="text-xs font-extrabold uppercase tracking-widest text-blue-400">
            System Architecture
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-white mt-2">
            The 6 Building Blocks of ArthaPilot
          </h2>
          <p className="text-sm text-slate-400 mt-3">
            Every layer is decoupled, deterministic, and rigorously verified with 105 automated unit and integration tests.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {blocks.map((block) => (
            <BuildingBlockCard key={block.num} block={block} />
          ))}
        </div>
      </section>

      {/* ============================================================== */}
      {/* 5. MANDATORY 3-SECTION SHOWCASE                                 */}
      {/* ============================================================== */}
      <section id="three-sections" className="py-20 border-t border-slate-800 bg-slate-900/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-extrabold uppercase tracking-widest text-blue-400">
              The Mandatory Requirement
            </span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2">
              Separating Fact, Prediction, and Recommendation
            </h2>
            <p className="text-sm text-slate-400 mt-3">
              Standard AI financial tools blend reality and guesses. ArthaPilot visually isolates past facts from
              statistical forecasts and suggested actions.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {/* Fact */}
            <div className="group rounded-2xl border-2 border-blue-500/50 bg-blue-950/20 p-6 space-y-3 hover:border-blue-400 hover:bg-blue-950/30 hover:shadow-xl hover:shadow-blue-500/10 transition-all duration-300 cursor-default">
              <div className="flex items-center justify-between">
                <span className="rounded-lg bg-blue-500/20 text-blue-300 font-extrabold text-xs px-2.5 py-1">
                  ✅ Blue: Observed Fact
                </span>
                <span className="text-[11px] text-slate-400 font-mono">100% Provenance</span>
              </div>
              <h4 className="text-base font-bold text-white">What already happened</h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                &ldquo;You spent ₹18,400 across 48 food delivery orders in the last 3 months. Your median order size was
                ₹385.&rdquo;
              </p>
              <div className="text-[11px] text-blue-400 font-medium group-hover:text-blue-300 transition-colors">
                Carries explicit evidence IDs linked directly to source bank rows.
              </div>
              {/* Animated progress bar on hover */}
              <div className="h-1 w-full rounded-full bg-blue-900/40 overflow-hidden">
                <div className="h-full rounded-full bg-blue-500 w-0 group-hover:w-full transition-all duration-700 ease-out" />
              </div>
            </div>

            {/* Prediction */}
            <div className="group rounded-2xl border-2 border-amber-500/50 bg-amber-950/20 p-6 space-y-3 hover:border-amber-400 hover:bg-amber-950/30 hover:shadow-xl hover:shadow-amber-500/10 transition-all duration-300 cursor-default">
              <div className="flex items-center justify-between">
                <span className="rounded-lg bg-amber-500/20 text-amber-300 font-extrabold text-xs px-2.5 py-1">
                  🔮 Orange: Prediction
                </span>
                <span className="text-[11px] text-amber-300 font-bold">Confidence: 78%</span>
              </div>
              <h4 className="text-base font-bold text-white">What will happen next</h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                &ldquo;Your balance will likely drop to ₹2,900 on the 27th before your salary credit. Risk of overdraft is
                42%.&rdquo;
              </p>
              <div className="text-[11px] text-amber-400 font-medium group-hover:text-amber-300 transition-colors">
                Explicit reasons why confidence is high or low (e.g. 12 months data vs irregular income).
              </div>
              <div className="h-1 w-full rounded-full bg-amber-900/40 overflow-hidden">
                <div className="h-full rounded-full bg-amber-500 w-0 group-hover:w-[78%] transition-all duration-700 ease-out" />
              </div>
            </div>

            {/* Recommendation */}
            <div className="group rounded-2xl border-2 border-emerald-500/50 bg-emerald-950/20 p-6 space-y-3 hover:border-emerald-400 hover:bg-emerald-950/30 hover:shadow-xl hover:shadow-emerald-500/10 transition-all duration-300 cursor-default">
              <div className="flex items-center justify-between">
                <span className="rounded-lg bg-emerald-500/20 text-emerald-300 font-extrabold text-xs px-2.5 py-1">
                  💡 Green: Recommendation
                </span>
                <span className="text-[11px] text-emerald-300 font-bold">Simulated Impact</span>
              </div>
              <h4 className="text-base font-bold text-white">What you should do</h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                &ldquo;Delay the discretionary purchase by 10 days. Cash gap avoided. Emergency runway improves 2.1 → 2.6
                months.&rdquo;
              </p>
              <div className="text-[11px] text-emerald-400 font-medium group-hover:text-emerald-300 transition-colors">
                Verified impact calculated via the deterministic simulation engine.
              </div>
              <div className="h-1 w-full rounded-full bg-emerald-900/40 overflow-hidden">
                <div className="h-full rounded-full bg-emerald-500 w-0 group-hover:w-full transition-all duration-700 ease-out" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 6. DYNAMIC UPDATE DEMO                                          */}
      {/* ============================================================== */}
      <section id="dynamic-update" className="py-20 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid gap-12 lg:grid-cols-12 items-center">
            <div className="lg:col-span-6 space-y-5">
              <span className="text-xs font-extrabold uppercase tracking-widest text-blue-400">
                The Dynamic Update Demo
              </span>
              <h2 className="text-3xl sm:text-4xl font-black text-white">
                Live Diff Recalculation on Every Transaction &amp; EMI
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">
                Add an expense, register a new loan, or simulate an income change. ArthaPilot instantly takes a snapshot,
                recalculates metrics, runs Monte Carlo forecasts, and surfaces a comprehensive &ldquo;What Changed&rdquo;
                summary card.
              </p>

              <div className="space-y-3 pt-2">
                {[
                  { step: 1, color: "bg-blue-500/20 text-blue-400", title: "Immediate Score Delta", desc: "See health score change before/after in real time (e.g. 72 → 61)." },
                  { step: 2, color: "bg-amber-500/20 text-amber-400", title: "New Cash Gaps Flagged", desc: "Identifies any newly created cash-flow shortfalls created by the added expense." },
                  { step: 3, color: "bg-emerald-500/20 text-emerald-400", title: "Advice Automatically Adapts", desc: "Recommendation dynamically flips from \"invest ₹5,000\" to \"build buffer first\"." },
                ].map(({ step, color, title, desc }) => (
                  <div key={step} className="flex items-start gap-3 group/step hover:translate-x-1 transition-transform duration-200">
                    <div className={`h-6 w-6 rounded-full ${color} flex items-center justify-center text-xs font-bold shrink-0 mt-0.5`}>
                      {step}
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-white">{title}</h4>
                      <p className="text-xs text-slate-400">{desc}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-2">
                <Link
                  href="/dashboard"
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-500 px-5 py-2.5 text-xs font-bold text-white transition-all shadow-md shadow-blue-600/30"
                >
                  <span>Test Dynamic Update in App</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>

            {/* Right: Mock What Changed Card */}
            <div className="lg:col-span-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <div className="h-7 w-7 rounded-lg bg-blue-600/20 flex items-center justify-center text-blue-400 font-bold text-xs">
                    <RefreshCw className="h-3.5 w-3.5" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white">Live What Changed Summary</div>
                    <div className="text-[10px] text-slate-400">Simulating: Added ₹15,000 Monthly Car Loan EMI</div>
                  </div>
                </div>
                <span className="rounded bg-red-950/60 border border-red-800/40 text-red-300 font-bold text-xs px-2 py-0.5">
                  Score -11 pts
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 py-4 border-b border-slate-800">
                <div className="rounded-xl bg-slate-950 p-3 group/metric hover:bg-slate-900 transition-colors">
                  <span className="text-[10px] text-slate-500 font-bold uppercase">Health Score</span>
                  <div className="mt-1 flex items-baseline gap-2">
                    <span className="text-sm line-through text-slate-500">72.0</span>
                    <span className="text-xl font-black text-white">61.0</span>
                  </div>
                  <div className="mt-1.5 h-1 rounded-full bg-slate-800 overflow-hidden">
                    <div className="h-full rounded-full bg-red-500 w-[61%]" />
                  </div>
                </div>

                <div className="rounded-xl bg-slate-950 p-3 hover:bg-slate-900 transition-colors">
                  <span className="text-[10px] text-slate-500 font-bold uppercase">Cash Danger Gaps</span>
                  <div className="mt-1 flex items-baseline gap-2">
                    <span className="text-sm line-through text-slate-500">0 Gaps</span>
                    <span className="text-xl font-black text-amber-400">1 New Gap</span>
                  </div>
                  <div className="mt-1.5 h-1 rounded-full bg-slate-800 overflow-hidden">
                    <div className="h-full rounded-full bg-amber-500 w-full" />
                  </div>
                </div>
              </div>

              <div className="pt-4 space-y-2">
                <div className="text-xs font-bold text-slate-300">Actionable Advice Shifted:</div>
                <p className="text-xs text-slate-400 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                  ⚠️ After adding this ₹15,000 EMI, your DTI jumped from 18% to 41%. Recommendation shifted from
                  &ldquo;Increase SIP by ₹3,000&rdquo; to &ldquo;Build 3-month liquid buffer to protect EMI obligations&rdquo;.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 7. PRE-LOADED PERSONAS                                          */}
      {/* ============================================================== */}
      <section id="personas" className="py-20 border-t border-slate-800 bg-slate-900/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-extrabold uppercase tracking-widest text-blue-400">
              Instant Hackathon / Demo Mode
            </span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2">
              Explore 5 Realistic Synthetic Personas
            </h2>
            <p className="text-sm text-slate-400 mt-3">
              Each persona includes 12 months of authentic Indian transactions, recurring bills, loans, cards, and
              investments.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {[
              { id: "rahul", name: "Rahul", role: "Young Professional", income: "₹65,000/mo", focus: "Food Delivery & Subscriptions", emoji: "👨‍💻", score: 68 },
              { id: "priya", name: "Priya", role: "Salaried + Home Loan", income: "₹1,20,000/mo", focus: "₹38,000 EMI + Credit Card", emoji: "👩‍💼", score: 74 },
              { id: "amit", name: "Amit", role: "Freelance Designer", income: "Variable Income", focus: "Irregular pay & cash gap spikes", emoji: "🎨", score: 55 },
              { id: "sneha", name: "Sneha", role: "Senior Tech Lead", income: "₹2,50,000/mo", focus: "High savings & SIP allocation", emoji: "👩‍🔬", score: 89 },
              { id: "vikram", name: "Vikram", role: "Retired Veteran", income: "Pension + Interest", focus: "Fixed expenses & capital safety", emoji: "🎖️", score: 82 },
            ].map((p) => (
              <div
                key={p.id}
                className="group rounded-2xl border border-slate-800 bg-slate-900/70 p-5 flex flex-col justify-between hover:border-blue-500/50 hover:bg-slate-900 hover:shadow-lg hover:shadow-blue-500/10 transition-all duration-300"
              >
                <div>
                  <div className="text-2xl mb-2">{p.emoji}</div>
                  <div className="text-xs font-bold text-slate-500 uppercase">{p.role}</div>
                  <h3 className="text-xl font-bold text-white mt-1">{p.name}</h3>
                  <div className="text-xs font-bold text-blue-400 mt-1">{p.income}</div>
                  <p className="text-[11px] text-slate-400 mt-2">{p.focus}</p>
                  {/* Score mini-bar */}
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-[10px] text-slate-500 font-semibold mb-1">
                      <span>Health</span>
                      <span className="text-blue-400 font-bold">{p.score}/100</span>
                    </div>
                    <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 w-0 group-hover:transition-all group-hover:duration-700"
                        style={{ width: `${p.score}%`, transition: 'width 0.7s ease-out' }}
                      />
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => handleQuickDemo(p.id)}
                  disabled={loadingPersona !== null}
                  className="mt-4 w-full rounded-xl bg-slate-800 group-hover:bg-blue-600 group-hover:text-white py-2 text-xs font-bold text-slate-300 transition-all text-center"
                >
                  {loadingPersona === p.id ? "Launching..." : "Launch Demo"}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 8. TRUST & PRIVACY SECTION                                      */}
      {/* ============================================================== */}
      <section id="trust" className="py-20 border-t border-slate-800">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-6">
          <div className="h-14 w-14 rounded-2xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 mx-auto hover:scale-110 transition-transform">
            <Lock className="h-7 w-7" />
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-white">Local-First, Strict Data Privacy</h2>
          <p className="text-sm text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Your real bank statements are never uploaded to remote LLM servers. All numbers are computed on your machine
            using verified Python code. PII (names, account numbers, UPI IDs) is masked before anything is displayed.
          </p>

          <div className="grid gap-4 sm:grid-cols-3 pt-6 text-left">
            {[
              { title: "Zero Hallucinated Math", desc: "The LLM never calculates balances or interest. Python code owns 100% of arithmetic.", icon: Target },
              { title: "Integer Paise Precision", desc: "₹1 = 100 paise. Stored strictly as integers to guarantee zero floating point drift.", icon: Calculator },
              { title: "30-Day Holdout Backtested", desc: "Validated against 5 synthetic personas with measured MAE of ₹12,267.", icon: CheckCircle2 },
            ].map(({ title, desc, icon: Icon }) => (
              <div key={title} className="group rounded-xl border border-slate-800 bg-slate-900/60 p-4 hover:border-blue-500/40 hover:bg-slate-900 transition-all">
                <div className="h-8 w-8 rounded-lg bg-blue-600/15 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-3 group-hover:scale-110 group-hover:bg-blue-600/25 transition-all">
                  <Icon className="h-4 w-4" />
                </div>
                <div className="text-xs font-bold text-white mb-1">{title}</div>
                <p className="text-[11px] text-slate-400">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 9. FOOTER                                                        */}
      {/* ============================================================== */}
      <footer className="border-t border-slate-800/80 py-12 bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <Logo size="xs" />
          </div>

          <div className="flex flex-wrap items-center gap-5">
            <Link href="/dashboard" className="hover:text-blue-400 transition-colors">
              App Dashboard
            </Link>
            <Link href="/login" className="hover:text-blue-400 transition-colors">
              Sign In
            </Link>
            <Link href="/register" className="hover:text-blue-400 transition-colors">
              Register
            </Link>
            <a href="#blocks" className="hover:text-blue-400 transition-colors">
              Building Blocks
            </a>
          </div>

          <div>Built with FastAPI, SQLAlchemy, Next.js 14 &amp; Tailwind CSS.</div>
        </div>
      </footer>
    </div>
  );
}
