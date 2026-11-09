"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import {
  Shield,
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
} from "lucide-react";

export default function LandingPage() {
  const router = useRouter();
  const { user, demoLogin } = useAuth();
  const [loadingPersona, setLoadingPersona] = useState<string | null>(null);

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
      {/* 1. NAVBAR */}
      {/* ============================================================== */}
      <nav className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white font-black text-lg shadow-lg shadow-blue-500/25 group-hover:scale-105 transition-transform">
              <Shield className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-black tracking-tight text-white leading-none">
                Artha<span className="text-blue-400">Pilot</span>
              </span>
              <span className="text-[10px] text-slate-400 font-medium tracking-wide">
                अर्थपायलट • Financial Health Copilot
              </span>
            </div>
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
      {/* 2. HERO SECTION */}
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
                  <div className="h-32 w-32 rounded-full border-8 border-blue-500/20 border-t-blue-500 flex flex-col items-center justify-center">
                    <span className="text-3xl font-black text-white">74</span>
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
                  <div className="rounded-xl border border-blue-500/30 bg-blue-950/30 p-3.5 text-left">
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
                  <div className="rounded-xl border border-amber-500/30 bg-amber-950/30 p-3.5 text-left">
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
                  <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/30 p-3.5 text-left">
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
      {/* 3. THE BIG IDEA IN ONE LINE */}
      {/* ============================================================== */}
      <section className="py-14 border-y border-slate-800/80 bg-slate-900/40">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center">
          <span className="text-xs font-extrabold uppercase tracking-widest text-blue-400">
            The Big Idea in One Line
          </span>
          <blockquote className="mt-4 text-xl sm:text-2xl font-bold text-slate-100 leading-relaxed">
            &ldquo;A local-first web app where you upload financial data, see one unified health picture, ask questions
            in plain English, and get answers that cleanly separate{" "}
            <span className="text-blue-400 underline decoration-blue-500/40 underline-offset-4">what happened</span>,{" "}
            <span className="text-amber-400 underline decoration-amber-500/40 underline-offset-4">what is predicted</span>,
            and{" "}
            <span className="text-emerald-400 underline decoration-emerald-500/40 underline-offset-4">
              what you should do
            </span>{" "}
            — each with simulated impact and verified confidence.&rdquo;
          </blockquote>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 4. THE 6 BUILDING BLOCKS */}
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
          {/* Block 1 */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 hover:border-blue-500/50 transition-all flex flex-col justify-between group">
            <div>
              <div className="h-10 w-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-4 group-hover:scale-105 transition-transform">
                <Database className="h-5 w-5" />
              </div>
              <div className="text-[11px] font-bold text-blue-400 uppercase tracking-wider">Block 1: Input Layer</div>
              <h3 className="text-lg font-bold text-white mt-1">Data Ingestion</h3>
              <p className="text-xs text-slate-400 mt-2.5 leading-relaxed">
                Accepts bank statements in CSV, XLSX, and PDF format. Deduplicates records, parses Indian dates, and
                standardises all monetary figures into integer paise (₹1 = 100 paise) to eliminate floating-point math
                errors.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-semibold text-slate-500">
              Tables: Transactions, Loans, Cards, Investments
            </div>
          </div>

          {/* Block 2 */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 hover:border-blue-500/50 transition-all flex flex-col justify-between group">
            <div>
              <div className="h-10 w-10 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-4 group-hover:scale-105 transition-transform">
                <Layers className="h-5 w-5" />
              </div>
              <div className="text-[11px] font-bold text-purple-400 uppercase tracking-wider">
                Block 2: Understanding Layer
              </div>
              <h3 className="text-lg font-bold text-white mt-1">Categorisation &amp; Recurring</h3>
              <p className="text-xs text-slate-400 mt-2.5 leading-relaxed">
                Cleans messy merchant names (e.g. &quot;SWIGGY*ORDER 4482&quot; → Swiggy). Runs rule cascade + ML classifier.
                Detects recurring subscriptions (Netflix, SIP, rent, EMIs) with interval cadences and flags salary vs.
                irregular income.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-semibold text-slate-500">
              Outputs: Tagged Transactions &amp; Known Recurring Bills
            </div>
          </div>

          {/* Block 3 */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 hover:border-blue-500/50 transition-all flex flex-col justify-between group">
            <div>
              <div className="h-10 w-10 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4 group-hover:scale-105 transition-transform">
                <Calculator className="h-5 w-5" />
              </div>
              <div className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider">
                Block 3: Analytics Layer
              </div>
              <h3 className="text-lg font-bold text-white mt-1">Financial Health Engine</h3>
              <p className="text-xs text-slate-400 mt-2.5 leading-relaxed">
                Computes 6 weighted core metrics: Savings Rate, Debt-to-Income (DTI), Emergency Fund Runway, Fixed vs
                Variable Ratio, Credit Card Utilisation, and Spending Volatility into a single 0–100 score with full audit
                breakdown.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-semibold text-slate-500">
              Outputs: 0–100 Health Score + Metric Provenance
            </div>
          </div>

          {/* Block 4 */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 hover:border-blue-500/50 transition-all flex flex-col justify-between group">
            <div>
              <div className="h-10 w-10 rounded-xl bg-amber-600/20 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-4 group-hover:scale-105 transition-transform">
                <LineChart className="h-5 w-5" />
              </div>
              <div className="text-[11px] font-bold text-amber-400 uppercase tracking-wider">
                Block 4: Future Layer
              </div>
              <h3 className="text-lg font-bold text-white mt-1">Prediction Engine</h3>
              <p className="text-xs text-slate-400 mt-2.5 leading-relaxed">
                1,000-run Monte Carlo simulation forecasts cash flow over 30, 60, or 90 days using recurring bills, expected
                paydays, and bootstrapped variable spending distributions. Automatically flags future danger days where
                balances dip below zero.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-semibold text-slate-500">
              Outputs: 30/60/90-Day P10/P50/P90 Bands + Cash Gaps
            </div>
          </div>

          {/* Block 5 */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 hover:border-blue-500/50 transition-all flex flex-col justify-between group">
            <div>
              <div className="h-10 w-10 rounded-xl bg-cyan-600/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-4 group-hover:scale-105 transition-transform">
                <Zap className="h-5 w-5" />
              </div>
              <div className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider">
                Block 5: Action Layer
              </div>
              <h3 className="text-lg font-bold text-white mt-1">Recommendation &amp; Simulator</h3>
              <p className="text-xs text-slate-400 mt-2.5 leading-relaxed">
                Ranks high-impact actions (Avalanche debt payoff, subscription pruning, SIP reallocation, deferring large
                purchases). Re-runs the entire mathematical model to show side-by-side Before vs After score, savings, and
                runway changes.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-semibold text-slate-500">
              Outputs: Side-by-side Before/After Simulation Diffs
            </div>
          </div>

          {/* Block 6 */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 hover:border-blue-500/50 transition-all flex flex-col justify-between group">
            <div>
              <div className="h-10 w-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-4 group-hover:scale-105 transition-transform">
                <Bot className="h-5 w-5" />
              </div>
              <div className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider">
                Block 6: Conversational Layer
              </div>
              <h3 className="text-lg font-bold text-white mt-1">Conversational Copilot</h3>
              <p className="text-xs text-slate-400 mt-2.5 leading-relaxed">
                Accepts natural language queries in English, Hindi, and Marathi. The LLM acts purely as a semantic router:
                it selects the Python tool, executes verified code on real data, and translates verified numbers into the
                mandatory 3-section format.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-semibold text-slate-500">
              Rule: Zero Math Hallucinations Allowed
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 5. MANDATORY 3-SECTION SHOWCASE */}
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
            <div className="rounded-2xl border-2 border-blue-500/50 bg-blue-950/20 p-6 space-y-3">
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
              <div className="text-[11px] text-blue-400 font-medium">
                Carries explicit evidence IDs linked directly to source bank rows.
              </div>
            </div>

            {/* Prediction */}
            <div className="rounded-2xl border-2 border-amber-500/50 bg-amber-950/20 p-6 space-y-3">
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
              <div className="text-[11px] text-amber-400 font-medium">
                Explicit reasons why confidence is high or low (e.g. 12 months data vs irregular income).
              </div>
            </div>

            {/* Recommendation */}
            <div className="rounded-2xl border-2 border-emerald-500/50 bg-emerald-950/20 p-6 space-y-3">
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
              <div className="text-[11px] text-emerald-400 font-medium">
                Verified impact calculated via the deterministic simulation engine.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 6. DYNAMIC UPDATE DEMO */}
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
                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                    1
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">Immediate Score Delta</h4>
                    <p className="text-xs text-slate-400">See health score change before/after in real time (e.g. 72 → 61).</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                    2
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">New Cash Gaps Flagged</h4>
                    <p className="text-xs text-slate-400">
                      Identifies any newly created cash-flow shortfalls created by the added expense.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                    3
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">Advice Automatically Adapts</h4>
                    <p className="text-xs text-slate-400">
                      Recommendation dynamically flips from &ldquo;invest ₹5,000&rdquo; to &ldquo;build buffer first&rdquo;.
                    </p>
                  </div>
                </div>
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
            <div className="lg:col-span-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <div className="h-7 w-7 rounded-lg bg-blue-600/20 flex items-center justify-center text-blue-400 font-bold text-xs">
                    Δ
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
                <div className="rounded-xl bg-slate-950 p-3">
                  <span className="text-[10px] text-slate-500 font-bold uppercase">Health Score</span>
                  <div className="mt-1 flex items-baseline gap-2">
                    <span className="text-sm line-through text-slate-500">72.0</span>
                    <span className="text-xl font-black text-white">61.0</span>
                  </div>
                </div>

                <div className="rounded-xl bg-slate-950 p-3">
                  <span className="text-[10px] text-slate-500 font-bold uppercase">Cash Danger Gaps</span>
                  <div className="mt-1 flex items-baseline gap-2">
                    <span className="text-sm line-through text-slate-500">0 Gaps</span>
                    <span className="text-xl font-black text-amber-400">1 New Gap</span>
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
      {/* 7. PRE-LOADED PERSONAS */}
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
              {
                id: "rahul",
                name: "Rahul",
                role: "Young Professional",
                income: "₹65,000/mo",
                focus: "Food Delivery & Subscriptions",
              },
              {
                id: "priya",
                name: "Priya",
                role: "Salaried + Home Loan",
                income: "₹1,20,000/mo",
                focus: "₹38,000 EMI + Credit Card",
              },
              {
                id: "amit",
                name: "Amit",
                role: "Freelance Designer",
                income: "Variable Income",
                focus: "Irregular pay & cash gap spikes",
              },
              {
                id: "sneha",
                name: "Sneha",
                role: "Senior Tech Lead",
                income: "₹2,50,000/mo",
                focus: "High savings & SIP allocation",
              },
              {
                id: "vikram",
                name: "Vikram",
                role: "Retired Veteran",
                income: "Pension + Interest",
                focus: "Fixed expenses & capital safety",
              },
            ].map((p) => (
              <div
                key={p.id}
                className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 flex flex-col justify-between hover:border-slate-700 transition-all"
              >
                <div>
                  <div className="text-xs font-bold text-slate-500 uppercase">{p.role}</div>
                  <h3 className="text-xl font-bold text-white mt-1">{p.name}</h3>
                  <div className="text-xs font-bold text-blue-400 mt-1">{p.income}</div>
                  <p className="text-[11px] text-slate-400 mt-2">{p.focus}</p>
                </div>
                <button
                  type="button"
                  onClick={() => handleQuickDemo(p.id)}
                  disabled={loadingPersona !== null}
                  className="mt-4 w-full rounded-xl bg-slate-800 hover:bg-blue-600 hover:text-white py-2 text-xs font-bold text-slate-300 transition-all text-center"
                >
                  {loadingPersona === p.id ? "Launching..." : "Launch Demo"}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 8. TRUST & PRIVACY SECTION */}
      {/* ============================================================== */}
      <section id="trust" className="py-20 border-t border-slate-800">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-6">
          <div className="h-12 w-12 rounded-2xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 mx-auto">
            <Lock className="h-6 w-6" />
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-white">Local-First, Strict Data Privacy</h2>
          <p className="text-sm text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Your real bank statements are never uploaded to remote LLM servers. All numbers are computed on your machine
            using verified Python code. PII (names, account numbers, UPI IDs) is masked before anything is displayed.
          </p>

          <div className="grid gap-4 sm:grid-cols-3 pt-6 text-left">
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="text-xs font-bold text-white mb-1">Zero Hallucinated Math</div>
              <p className="text-[11px] text-slate-400">
                The LLM never calculates balances or interest. Python code owns 100% of arithmetic.
              </p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="text-xs font-bold text-white mb-1">Integer Paise Precision</div>
              <p className="text-[11px] text-slate-400">
                ₹1 = 100 paise. Stored strictly as integers to guarantee zero floating point drift.
              </p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="text-xs font-bold text-white mb-1">30-Day Holdout Backtested</div>
              <p className="text-[11px] text-slate-400">
                Validated against 5 synthetic personas with measured MAE of ₹12,267.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 9. FOOTER */}
      {/* ============================================================== */}
      <footer className="border-t border-slate-800/80 py-12 bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-xs">
              A
            </div>
            <span className="font-bold text-slate-300">ArthaPilot (अर्थपायलट)</span>
            <span>• Deterministic Financial Health Copilot</span>
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
