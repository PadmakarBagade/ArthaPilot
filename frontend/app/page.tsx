"use client";

import { useEffect, useState } from "react";
import {
  askCopilot,
  BestMoves,
  ChatAnswer,
  checkAffordability,
  Confidence,
  Forecast,
  formatDate,
  formatPaise,
  Gap,
  getBestMoves,
  getConfidence,
  getDebtPayoff,
  getForecast,
  getGaps,
  getHealth,
  getInsights,
  getRecurring,
  getTransactions,
  getWhatChanged,
  Health,
  Insight,
  listUsers,
  planGoal,
  RecurringItem,
  runStressTest,
  Transaction,
  User,
  WhatChanged,
} from "@/lib/api";
import { ScoreRing } from "@/components/ScoreRing";
import { EvidenceDetail, EvidenceDrawer } from "@/components/EvidenceDrawer";
import { FactCard, PredictionCard, RecommendationCard, VerdictCard } from "@/components/Cards";
import { DangerCalendar } from "@/components/DangerCalendar";
import { ForecastChart } from "@/components/ForecastChart";
import { WhatChangedCard } from "@/components/WhatChangedCard";
import { InsightsList } from "@/components/InsightsList";
import { DataTrustModal } from "@/components/DataTrustModal";
import { AddDataModal } from "@/components/AddDataModal";
import { PlanTools } from "@/components/PlanTools";
import {
  Sparkles,
  ShieldCheck,
  Send,
  PlusCircle,
  ArrowRight,
  CheckCircle,
  ChevronRight,
  Globe,
} from "lucide-react";

export default function Home() {
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [language, setLanguage] = useState<"en" | "hi" | "mr">("en");
  const [activeTab, setActiveTab] = useState<"Home" | "Ask" | "Plan" | "Money">("Home");

  // Domain data states
  const [health, setHealth] = useState<Health | null>(null);
  const [confidence, setConfidence] = useState<Confidence | null>(null);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [gaps, setGaps] = useState<Gap[]>([]);
  const [bestMoves, setBestMoves] = useState<BestMoves | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [recurring, setRecurring] = useState<RecurringItem[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [whatChanged, setWhatChanged] = useState<WhatChanged | null>(null);

  // UI modal states
  const [evidence, setEvidence] = useState<EvidenceDetail | null>(null);
  const [showDataTrust, setShowDataTrust] = useState(false);
  const [showAddData, setShowAddData] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [onboardingStep, setOnboardingStep] = useState(1);
  const [error, setError] = useState<string | null>(null);

  // Copilot chat state
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState<
    { role: "user" | "assistant"; content?: string; answer?: ChatAnswer }[]
  >([]);
  const [asking, setAsking] = useState(false);

  // Initial user list load
  useEffect(() => {
    if (typeof window !== "undefined") {
      const onboarded = window.localStorage.getItem("arthapilot-onboarded");
      if (!onboarded) {
        setShowOnboarding(true);
      }
    }

    listUsers()
      .then((items) => {
        setUsers(items);
        if (items.length > 0) {
          // Default to rahul if available, else first user
          const rahul = items.find((u) => u.id === "rahul");
          setSelectedUser(rahul ? rahul.id : items[0].id);
        }
      })
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Unable to connect to backend"));
  }, []);

  function finishOnboarding() {
    if (typeof window !== "undefined") {
      window.localStorage.setItem("arthapilot-onboarded", "true");
    }
    setShowOnboarding(false);
  }

  // Load all user data when selected user changes
  async function refreshUserData(userId: string) {
    if (!userId) return;
    try {
      const [h, c, f, g, b, t, r, ins, wc] = await Promise.all([
        getHealth(userId),
        getConfidence(userId),
        getForecast(userId, 90),
        getGaps(userId),
        getBestMoves(userId),
        getTransactions(userId),
        getRecurring(userId),
        getInsights(userId),
        getWhatChanged(userId),
      ]);
      setHealth(h);
      setConfidence(c);
      setForecast(f);
      setGaps(g);
      setBestMoves(b);
      setTransactions(t);
      setRecurring(r);
      setInsights(ins);
      setWhatChanged(wc);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load persona analytics");
    }
  }

  useEffect(() => {
    if (selectedUser) {
      refreshUserData(selectedUser);
    }
  }, [selectedUser]);

  // Persona switcher handler
  async function handlePersonaChange(newUserId: string) {
    setSelectedUser(newUserId);
    setChatHistory([]);
  }

  // Copilot question submit
  async function submitQuestion(qText?: string) {
    const textToAsk = (qText || question).trim();
    if (!selectedUser || !textToAsk) return;

    setAsking(true);
    setQuestion("");
    const userMsg = { role: "user" as const, content: textToAsk };
    setChatHistory((prev) => [...prev, userMsg]);

    try {
      const answer = await askCopilot(selectedUser, textToAsk, language);
      setChatHistory((prev) => [...prev, { role: "assistant" as const, answer }]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Copilot request failed");
    } finally {
      setAsking(false);
    }
  }

  // Open evidence helper
  function openMetricEvidence(key: string, label: string) {
    const metric = health?.metrics[key];
    if (!metric) return;
    setEvidence({
      title: label,
      category: "Metric Evidence",
      summary: metric.reason,
      formula: metric.evidence?.formula ? String(metric.evidence.formula) : undefined,
      transactionIds: Array.isArray(metric.evidence?.transaction_ids)
        ? (metric.evidence.transaction_ids as string[])
        : undefined,
      rawNumbers: {
        raw_value: metric.raw_value ?? 0,
        sub_score: metric.sub_score ?? 0,
        status: metric.status,
      },
    });
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      {/* Top Header */}
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur-sm px-4 sm:px-8 py-3.5 shadow-2xs">
        <div className="mx-auto max-w-6xl flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white font-bold shadow-md shadow-blue-500/20">
              अ
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight text-slate-900">ArthaPilot</span>
                <span className="rounded-md bg-blue-100 text-blue-800 text-[10px] font-bold px-1.5 py-0.5 uppercase tracking-wide">
                  Copilot
                </span>
              </div>
              <p className="text-[11px] text-slate-500 hidden sm:block">
                Verified Indian Financial Health Engine · Zero LLM Calculation
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
            {/* Language toggle */}
            <div className="flex items-center bg-slate-100 p-0.5 rounded-lg text-xs font-semibold">
              <Globe className="h-3.5 w-3.5 text-slate-400 ml-1.5 mr-1" />
              {(["en", "hi", "mr"] as const).map((lang) => (
                <button
                  key={lang}
                  type="button"
                  onClick={() => setLanguage(lang)}
                  className={`px-2 py-1 rounded-md transition-all ${
                    language === lang ? "bg-white text-blue-700 shadow-2xs font-bold" : "text-slate-500 hover:text-slate-900"
                  }`}
                >
                  {lang === "en" ? "EN" : lang === "hi" ? "हिन्दी" : "मराठी"}
                </button>
              ))}
            </div>

            {/* Persona switcher */}
            <div className="flex items-center gap-1.5">
              <label htmlFor="persona-select" className="sr-only">Demo profile</label>
              <select
                id="persona-select"
                value={selectedUser}
                onChange={(e) => handlePersonaChange(e.target.value)}
                className="rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-bold text-slate-800 shadow-2xs focus:border-blue-600 focus:outline-hidden"
              >
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name} ({u.id})
                  </option>
                ))}
              </select>
            </div>

            {/* Action buttons */}
            <button
              type="button"
              onClick={() => setShowAddData(true)}
              className="flex items-center gap-1 rounded-xl bg-blue-50 border border-blue-200 px-3 py-1.5 text-xs font-bold text-blue-700 hover:bg-blue-100 transition-colors"
            >
              <PlusCircle className="h-3.5 w-3.5" />
              Scenario
            </button>

            <button
              type="button"
              onClick={() => setShowDataTrust(true)}
              className="flex items-center gap-1 rounded-xl bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-700 hover:bg-slate-200 transition-colors"
            >
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
              Trust &amp; AI
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="mx-auto max-w-6xl w-full px-4 sm:px-8 py-6 space-y-6 flex-1">
        {/* Navigation Tabs (4 Tabs as per Phase 8A) */}
        <nav className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto" aria-label="Main Navigation">
          {[
            { id: "Home", label: "Home Dashboard" },
            { id: "Ask", label: "Ask Copilot" },
            { id: "Plan", label: "Plan & Forecast" },
            { id: "Money", label: "Money & Spending" },
          ].map((tab) => {
            const isSelected = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`rounded-xl px-4 py-2 text-sm font-bold transition-all whitespace-nowrap ${
                  isSelected
                    ? "bg-blue-700 text-white shadow-sm"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </nav>

        {error && (
          <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-xs font-semibold text-red-800">
            {error}
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 1: HOME DASHBOARD */}
        {/* ============================================================== */}
        {activeTab === "Home" && (
          <div className="space-y-6">
            {/* Live What Changed Diff Card */}
            <WhatChangedCard
              whatChanged={whatChanged}
              onViewEvidence={() =>
                setEvidence({
                  title: "Snapshot State Diff",
                  category: "What Changed Audit",
                  summary: whatChanged?.summary || "",
                  transactionIds: whatChanged?.evidence,
                })
              }
            />

            {/* 3 Top Cards Above The Fold */}
            <div className="grid gap-4 md:grid-cols-3">
              {/* Card 1: Health Score */}
              <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-blue-700">Observed Fact</span>
                    <button
                      type="button"
                      onClick={() =>
                        setEvidence({
                          title: "Health Score Audit",
                          category: "Scoring Engine",
                          summary: health?.summary || "Score calculated from verified metric weighted components.",
                          formula: "Score = Sum(Component SubScore * Weight)",
                          rawNumbers: {
                            Coverage: `${Math.round((health?.score_coverage ?? 0) * 100)}%`,
                            Months: health?.months_used ?? 0,
                          },
                        })
                      }
                      className="text-xs text-blue-600 underline font-semibold"
                    >
                      Audit
                    </button>
                  </div>
                  <div className="mt-4 flex items-center justify-center">
                    <ScoreRing score={health?.total_score} band={health?.band} />
                  </div>
                </div>
                <p className="mt-4 text-xs text-slate-600 text-center leading-relaxed font-medium">
                  {health?.summary ?? "Load a demo persona to view health score."}
                </p>
              </article>

              {/* Card 2: Confidence Engine */}
              <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-amber-700">Prediction</span>
                    <span className="rounded-full bg-amber-100 text-amber-800 text-[10px] font-bold px-2 py-0.5 uppercase tracking-wide">
                      {confidence?.level ?? "Medium"}
                    </span>
                  </div>
                  <div className="mt-3">
                    <span className="text-3xl font-extrabold text-amber-900 tracking-tight">
                      {confidence?.score ?? 0}%
                    </span>
                    <p className="text-xs text-slate-500 mt-0.5">Statistical confidence rating</p>
                  </div>
                  <div className="mt-3 space-y-1.5">
                    <p className="text-xs font-semibold text-slate-700">Audit Basis:</p>
                    <ul className="text-xs text-slate-600 space-y-1 list-disc pl-4">
                      {(confidence?.reasons?.length ? confidence.reasons.slice(0, 3) : ["Consistent transaction history"]).map(
                        (r) => (
                          <li key={r}>{r}</li>
                        )
                      )}
                    </ul>
                  </div>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-500">
                  {confidence?.how_to_improve?.[0] ?? "Upload full 6+ months statements for High rating."}
                </div>
              </article>

              {/* Card 3: Best Next Move */}
              <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">Recommendation</span>
                    <span className="rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 uppercase tracking-wide">
                      Simulated
                    </span>
                  </div>
                  <h4 className="mt-3 text-base font-bold text-slate-900 leading-snug">
                    {bestMoves?.best_move?.reason ?? "Build an emergency buffer"}
                  </h4>
                  {bestMoves?.best_move && (
                    <div className="mt-3 rounded-xl bg-emerald-50 border border-emerald-200 p-3">
                      <div className="flex justify-between text-xs">
                        <span className="text-emerald-800 font-semibold">Monthly Surplus Gain:</span>
                        <span className="font-extrabold text-emerald-900">
                          +{formatPaise(bestMoves.best_move.impact_paise)}
                        </span>
                      </div>
                      <div className="flex justify-between text-xs mt-1">
                        <span className="text-emerald-700">Implementation Effort:</span>
                        <span className="font-semibold text-emerald-900">
                          {bestMoves.best_move.effort_score} / 10
                        </span>
                      </div>
                    </div>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => setActiveTab("Plan")}
                  className="mt-4 flex items-center justify-between text-xs font-bold text-blue-700 hover:text-blue-900 pt-3 border-t border-slate-100"
                >
                  <span>Explore in What-If Simulator</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              </article>
            </div>

            {/* Financial Vitals Grid */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-slate-900">Core Financial Health Indicators</h3>
                <span className="text-xs text-slate-400">Click any card to inspect evidence</span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { key: "savings_rate", label: "Savings Rate", suffix: "%" },
                  { key: "debt_to_income", label: "Debt-to-Income (DTI)", suffix: "%" },
                  { key: "emergency_runway", label: "Emergency Runway", suffix: " Months" },
                  { key: "credit_utilisation", label: "Credit Card Utilisation", suffix: "%" },
                ].map((item) => {
                  const m = health?.metrics[item.key];
                  const raw = m?.raw_value;
                  const isGood = m?.status === "healthy" || m?.status === "good";
                  return (
                    <button
                      type="button"
                      key={item.key}
                      onClick={() => openMetricEvidence(item.key, item.label)}
                      className="rounded-xl bg-slate-50 border border-slate-200 p-3.5 text-left hover:border-blue-400 hover:bg-blue-50/50 transition-all"
                    >
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block truncate">
                        {item.label}
                      </span>
                      <div className="mt-1.5 flex items-baseline justify-between">
                        <span className="text-xl font-extrabold text-slate-900">
                          {raw !== null && raw !== undefined
                            ? item.suffix === "%"
                              ? `${Math.round(raw * 100)}%`
                              : `${Number(raw).toFixed(1)} mos`
                            : "—"}
                        </span>
                        <span
                          className={`text-[10px] font-bold px-1.5 py-0.5 rounded capitalize ${
                            isGood ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"
                          }`}
                        >
                          {m?.status ?? "fair"}
                        </span>
                      </div>
                      <p className="mt-1 text-[11px] text-slate-500 line-clamp-2">{m?.reason ?? "—"}</p>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Cash-Flow Risk Preview */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-slate-900">30-Day Cash-Flow Forecast Preview</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {gaps.length > 0
                      ? `⚠️ ${gaps.length} danger day(s) detected where balance dips below safety reserve.`
                      : "✅ No deficits detected. Projected balances remain safe."}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setActiveTab("Plan")}
                  className="text-xs font-bold text-blue-700 hover:underline flex items-center gap-1"
                >
                  View Full 90-Day Outlook <ChevronRight className="h-4 w-4" />
                </button>
              </div>

              {forecast && (
                <ForecastChart forecast={forecast} height={220} />
              )}
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 2: ASK COPILOT (CONVERSATIONAL Q&A) */}
        {/* ============================================================== */}
        {activeTab === "Ask" && (
          <div className="space-y-6">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-2xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-blue-700" />
                    <h2 className="text-lg font-bold text-slate-900">ArthaPilot Conversational Copilot</h2>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Answers are strictly derived from tested Python functions and structured in three separate parts:
                    Fact, Prediction, and Recommendation.
                  </p>
                </div>
                <div className="text-[11px] font-bold text-blue-800 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-200 shrink-0">
                  {language === "hi" ? "हिन्दी मोड" : language === "mr" ? "मराठी मोड" : "English Mode"}
                </div>
              </div>

              {/* Suggested Questions */}
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Suggested Questions:
                </p>
                <div className="flex flex-wrap gap-2">
                  {[
                    "Can I afford a ₹45,000 laptop?",
                    "Will I run short before salary?",
                    "What is my best next move?",
                    "What recurring bills do I have?",
                    "How healthy are my finances?",
                    "How sure are you about this analysis?",
                  ].map((chip) => (
                    <button
                      key={chip}
                      type="button"
                      onClick={() => submitQuestion(chip)}
                      className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-blue-50 hover:border-blue-300 transition-colors"
                    >
                      {chip}
                    </button>
                  ))}
                </div>
              </div>

              {/* Chat Input Form */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  submitQuestion();
                }}
                className="flex gap-2"
              >
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask a question about your cash flow, bills, loans, or goals..."
                  className="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium focus:border-blue-600 focus:outline-hidden"
                />
                <button
                  type="submit"
                  disabled={asking || !question.trim()}
                  className="flex items-center gap-1.5 rounded-xl bg-blue-700 px-5 font-bold text-white text-sm hover:bg-blue-800 disabled:opacity-50 transition-colors shadow-xs"
                >
                  <Send className="h-4 w-4" />
                  {asking ? "Checking..." : "Ask"}
                </button>
              </form>
            </div>

            {/* Chat Messages */}
            <div className="space-y-4">
              {chatHistory.map((item, index) => {
                if (item.role === "user") {
                  return (
                    <div key={index} className="flex justify-end">
                      <div className="rounded-2xl bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white max-w-lg shadow-2xs">
                        {item.content}
                      </div>
                    </div>
                  );
                }

                const ans = item.answer;
                if (!ans) return null;

                return (
                  <div key={index} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
                    {/* Direct Summary */}
                    <div className="text-sm font-bold text-slate-900 border-b pb-3">
                      {ans.summary}
                    </div>

                    {/* Verdict if present */}
                    {ans.verdict && (
                      <VerdictCard
                        verdict={ans.verdict as "Yes" | "Risky" | "No"}
                        reason={ans.recommendations?.[0]?.text}
                      />
                    )}

                    {/* Three-Part Architecture Cards */}
                    <div className="grid gap-3 md:grid-cols-3">
                      {ans.facts.map((f, i) => (
                        <FactCard
                          key={i}
                          text={f.text}
                          evidenceIds={f.evidence_ids}
                          onEvidenceClick={() =>
                            setEvidence({
                              title: "Observed Fact Provenance",
                              category: "Copilot Fact",
                              summary: f.text,
                              transactionIds: f.evidence_ids,
                            })
                          }
                        />
                      ))}

                      {ans.predictions.map((p, i) => (
                        <PredictionCard
                          key={i}
                          text={p.text}
                          confidence={p.confidence}
                          reasons={p.confidence_reasons}
                        />
                      ))}

                      {ans.recommendations.map((r, i) => (
                        <RecommendationCard
                          key={i}
                          text={r.text}
                          impact={r.impact}
                          onSimulate={() => setActiveTab("Plan")}
                        />
                      ))}
                    </div>

                    {/* Follow ups */}
                    {ans.follow_ups.length > 0 && (
                      <div className="flex flex-wrap items-center gap-2 pt-2 border-t text-xs">
                        <span className="text-slate-400 font-medium">Follow-up:</span>
                        {ans.follow_ups.map((fu) => (
                          <button
                            key={fu}
                            type="button"
                            onClick={() => submitQuestion(fu)}
                            className="rounded-lg bg-slate-100 hover:bg-slate-200 px-2.5 py-1 text-slate-700 font-semibold transition-colors"
                          >
                            {fu}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 3: PLAN & FORECAST */}
        {/* ============================================================== */}
        {activeTab === "Plan" && (
          <div className="space-y-6">
            {/* Danger Calendar */}
            {forecast && (
              <DangerCalendar
                dates={forecast.dates}
                p10Balances={forecast.p10_paise}
                p50Balances={forecast.p50_paise}
                gaps={gaps}
                onSelectDate={(d, b) =>
                  setEvidence({
                    title: `Forecast Balance on ${formatDate(d)}`,
                    category: "Monte Carlo Forecast Point",
                    summary: `Expected cash balance: ${formatPaise(b)}. Seed: ${forecast.seed}, 500 simulations.`,
                    formula: "balance_expected = initial + sum(scheduled) - E(variable_spend)",
                  })
                }
              />
            )}

            {/* Interactive 90-Day Full Forecast Band Chart */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
              <div>
                <h3 className="font-bold text-slate-900">90-Day Cash-Flow Trajectory (Monte Carlo Simulation)</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Visualizes P10 (worst 10% scenario), P50 (likely trajectory), and P90 (best 10% scenario).
                </p>
              </div>
              {forecast && <ForecastChart forecast={forecast} height={320} />}
            </div>

            {/* Integrated Plan Tools: Affordability, Debt Payoff, Stress Shocks, Goals */}
            <PlanTools
              userId={selectedUser}
              onRunAffordability={(amt) => checkAffordability(selectedUser, amt)}
              onRunGoal={(target, deadline) => planGoal(selectedUser, target, deadline)}
              onRunDebtPayoff={(extra, strat) => getDebtPayoff(selectedUser, extra, strat)}
              onRunStressTest={(scenario, emi) => runStressTest(selectedUser, scenario, emi)}
              onOpenEvidence={(title, summary, formula) =>
                setEvidence({
                  title,
                  category: "Plan Audit",
                  summary,
                  formula,
                })
              }
            />
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 4: MONEY & SPENDING */}
        {/* ============================================================== */}
        {activeTab === "Money" && (
          <div className="space-y-6">
            {/* Spending by Category Cards */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-slate-900">Spending Breakdown by Category</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Cleaned and categorized debit transactions. Click any category to inspect evidence IDs.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                {Object.entries(
                  transactions.reduce<Record<string, number>>((acc, tx) => {
                    if (tx.amount_paise < 0) {
                      const cat = tx.category || "Uncategorised";
                      acc[cat] = (acc[cat] || 0) + Math.abs(tx.amount_paise);
                    }
                    return acc;
                  }, {})
                )
                  .sort(([, a], [, b]) => b - a)
                  .map(([category, amtPaise]) => {
                    const count = transactions.filter((t) => t.category === category).length;
                    return (
                      <button
                        type="button"
                        key={category}
                        onClick={() =>
                          setEvidence({
                            title: `${category} Spending Audit`,
                            category: "Category Spend",
                            summary: `Total of ${formatPaise(amtPaise)} spent across ${count} verified transactions.`,
                            transactionIds: transactions
                              .filter((t) => t.category === category)
                              .map((t) => t.txn_id),
                          })
                        }
                        className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 text-left hover:border-blue-400 hover:bg-blue-50/50 transition-all"
                      >
                        <span className="text-[11px] font-semibold text-slate-500 block truncate">{category}</span>
                        <span className="mt-1 text-lg font-extrabold text-slate-900 block">{formatPaise(amtPaise)}</span>
                        <span className="mt-1 text-[10px] text-blue-700 font-semibold block">{count} Transactions</span>
                      </button>
                    );
                  })}
              </div>
            </div>

            {/* Recurring Obligations */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-slate-900">Detected Recurring Bills &amp; Subscriptions</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Identified by regex pattern clustering and interval gap analysis.
                  </p>
                </div>
                <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg">
                  {recurring.length} Detected
                </span>
              </div>

              {recurring.length > 0 ? (
                <div className="grid gap-2.5 sm:grid-cols-2 md:grid-cols-3">
                  {recurring.map((item) => (
                    <button
                      type="button"
                      key={item.id}
                      onClick={() =>
                        setEvidence({
                          title: item.merchant,
                          category: "Recurring Obligation",
                          summary: `Charges ${formatPaise(item.amount_paise)} every ${item.interval_days} days. Next due on ${formatDate(
                            item.next_due_date
                          )}. Detection confidence: ${Math.round(item.confidence * 100)}%.`,
                          transactionIds: item.txn_ids,
                        })
                      }
                      className="rounded-xl border border-slate-200 p-3.5 text-left hover:border-blue-400 hover:bg-slate-50 transition-all"
                    >
                      <div className="flex justify-between items-baseline gap-2">
                        <span className="font-bold text-slate-900 text-sm truncate">{item.merchant}</span>
                        <span className="font-extrabold text-slate-900 text-sm">{formatPaise(item.amount_paise)}</span>
                      </div>
                      <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500">
                        <span>Due {formatDate(item.next_due_date)}</span>
                        <span className="rounded bg-blue-50 text-blue-700 font-bold px-1.5 py-0.5">
                          {Math.round(item.confidence * 100)}% Conf
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 text-center py-4">No recurring bills found.</p>
              )}
            </div>

            {/* Spending Behaviour & Anomaly Insights */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-slate-900">Behavioural Insights &amp; Anomaly Alerts</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Checks duplicate charges, subscription creep, weekend spending spikes, and month-end squeezes.
                  </p>
                </div>
              </div>
              <InsightsList
                insights={insights}
                onEvidenceClick={(ins) =>
                  setEvidence({
                    title: ins.title,
                    category: "Anomaly Evidence",
                    summary: ins.message,
                    transactionIds: ins.evidence_ids,
                  })
                }
              />
            </div>

            {/* Recent Transactions Table */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-2xs space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-slate-900">Recent Bank Transactions</h3>
                <span className="text-xs text-slate-400">{transactions.length} Records</span>
              </div>

              <div className="overflow-x-auto max-h-80 rounded-xl border border-slate-100">
                <table className="min-w-full text-left text-xs">
                  <thead className="sticky top-0 bg-slate-50 text-slate-400 uppercase tracking-wider border-b">
                    <tr>
                      <th className="p-3">Date</th>
                      <th className="p-3">Merchant</th>
                      <th className="p-3">Category</th>
                      <th className="p-3 text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {transactions.slice(0, 30).map((t) => (
                      <tr
                        key={t.txn_id}
                        onClick={() =>
                          setEvidence({
                            title: t.merchant || "Transaction Details",
                            category: "Transaction Audit",
                            summary: `Amount: ${formatPaise(t.amount_paise)} on ${formatDate(t.date)}. Category confidence: ${Math.round(
                              t.category_confidence * 100
                            )}%.`,
                            transactionIds: [t.txn_id],
                          })
                        }
                        className="hover:bg-slate-50/80 cursor-pointer"
                      >
                        <td className="p-3 font-medium text-slate-700">{formatDate(t.date)}</td>
                        <td className="p-3 font-bold text-slate-900">{t.merchant || "Unknown"}</td>
                        <td className="p-3">
                          <span className="rounded-md bg-slate-100 text-slate-700 px-2 py-0.5 font-medium">
                            {t.category}
                          </span>
                        </td>
                        <td
                          className={`p-3 text-right font-extrabold font-mono ${
                            t.amount_paise < 0 ? "text-slate-900" : "text-emerald-700"
                          }`}
                        >
                          {formatPaise(t.amount_paise)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-5 px-4 sm:px-8 text-center text-xs text-slate-400 space-y-1">
        <p>ArthaPilot · Your Financial Health Copilot · Built with Python 3.11, Next.js &amp; Recharts</p>
        <p className="text-[11px] text-slate-400">
          All numbers verified via integer paise. Personal data masked locally. Educational guidance, not regulated financial advice.
        </p>
      </footer>

      {/* Global Modals & Drawers */}
      <EvidenceDrawer evidence={evidence} onClose={() => setEvidence(null)} />
      <DataTrustModal isOpen={showDataTrust} onClose={() => setShowDataTrust(false)} />
      <AddDataModal
        isOpen={showAddData}
        onClose={() => setShowAddData(false)}
        userId={selectedUser}
        onSuccess={() => {
          setShowAddData(false);
          refreshUserData(selectedUser);
        }}
      />

      {/* 3-Step Guided Onboarding Tour */}
      {showOnboarding && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="w-full max-w-md bg-white rounded-2xl p-6 shadow-2xl space-y-5 animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between text-xs text-blue-700 font-bold uppercase tracking-wider">
              <span>Step {onboardingStep} of 3</span>
              <button type="button" onClick={finishOnboarding} className="text-slate-400 hover:text-slate-600">
                Skip Tour
              </button>
            </div>

            {onboardingStep === 1 && (
              <div>
                <h3 className="text-xl font-extrabold text-slate-900">Welcome to ArthaPilot</h3>
                <p className="mt-2 text-xs text-slate-600 leading-relaxed">
                  Your local-first financial health copilot. We keep facts, predictions, and recommendations strictly
                  separate so you can make informed decisions.
                </p>
                <button
                  type="button"
                  onClick={() => setOnboardingStep(2)}
                  className="mt-6 w-full rounded-xl bg-blue-700 py-3 text-xs font-bold text-white hover:bg-blue-800"
                >
                  Next: Choose Persona
                </button>
              </div>
            )}

            {onboardingStep === 2 && (
              <div>
                <h3 className="text-xl font-extrabold text-slate-900">Select a Demo Persona</h3>
                <p className="mt-2 text-xs text-slate-600 leading-relaxed">
                  Explore pre-built financial stories: <strong>Rahul</strong> (salaried with month-end gap),{" "}
                  <strong>Priya</strong> (wealthy with SIPs), <strong>Arjun</strong> (volatile freelancer), or upload
                  your own statement.
                </p>
                <div className="mt-4 space-y-2">
                  {users.slice(0, 3).map((u) => (
                    <button
                      key={u.id}
                      type="button"
                      onClick={() => setSelectedUser(u.id)}
                      className={`w-full p-2.5 rounded-xl border text-left text-xs font-semibold flex items-center justify-between ${
                        selectedUser === u.id ? "border-blue-600 bg-blue-50 text-blue-800" : "hover:bg-slate-50"
                      }`}
                    >
                      <span>{u.name}</span>
                      {selectedUser === u.id && <CheckCircle className="h-4 w-4 text-blue-700" />}
                    </button>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={() => setOnboardingStep(3)}
                  className="mt-6 w-full rounded-xl bg-blue-700 py-3 text-xs font-bold text-white hover:bg-blue-800"
                >
                  Next: See 3 Golden Rules
                </button>
              </div>
            )}

            {onboardingStep === 3 && (
              <div>
                <h3 className="text-xl font-extrabold text-slate-900">Zero Guesswork, 100% Verified</h3>
                <ul className="mt-3 text-xs text-slate-600 space-y-2 list-disc pl-4 leading-relaxed">
                  <li>
                    <strong>The LLM never calculates money:</strong> All numbers come from tested Python functions.
                  </li>
                  <li>
                    <strong>Traceable evidence:</strong> Click any number to see its formulas and backing transactions.
                  </li>
                  <li>
                    <strong>Privacy first:</strong> Real statement data stays local; personal information is masked.
                  </li>
                </ul>
                <button
                  type="button"
                  onClick={finishOnboarding}
                  className="mt-6 w-full rounded-xl bg-emerald-700 py-3 text-xs font-bold text-white hover:bg-emerald-800"
                >
                  Start Exploring ArthaPilot
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
