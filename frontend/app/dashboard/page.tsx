"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  askCopilot,
  BestMoves,
  Card,
  ChatAnswer,
  checkAffordability,
  Confidence,
  Forecast,
  formatDate,
  formatPaise,
  Gap,
  getBestMoves,
  getCards,
  getConfidence,
  getDebtPayoff,
  getForecast,
  getGaps,
  getHealth,
  getInsights,
  getInvestments,
  getRecurring,
  getTransactions,
  getWhatChanged,
  Health,
  Insight,
  Investment,
  listUsers,
  planGoal,
  RecurringItem,
  runStressTest,
  Transaction,
  User,
  WhatChanged,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
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
import { Logo } from "@/components/Logo";
import {
  Sparkles,
  ShieldCheck,
  PlusCircle,
  ChevronRight,
  Home as HomeIcon,
  MessageSquare,
  TrendingUp,
  CreditCard as CardIcon,
  LogOut,
} from "lucide-react";

export default function DashboardPage() {
  const { user: authUser, logout } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [language, setLanguage] = useState<"en" | "hi" | "mr">("en");
  const [activeTab, setActiveTab] = useState<"Home" | "Ask" | "Plan" | "Money">("Home");
  const [forecastDays, setForecastDays] = useState<number>(90);

  // Domain data states
  const [health, setHealth] = useState<Health | null>(null);
  const [confidence, setConfidence] = useState<Confidence | null>(null);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [gaps, setGaps] = useState<Gap[]>([]);
  const [bestMoves, setBestMoves] = useState<BestMoves | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [recurring, setRecurring] = useState<RecurringItem[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [cards, setCards] = useState<Card[]>([]);
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [whatChanged, setWhatChanged] = useState<WhatChanged | null>(null);

  // UI modal states
  const [evidence, setEvidence] = useState<EvidenceDetail | null>(null);
  const [showDataTrust, setShowDataTrust] = useState(false);
  const [showAddData, setShowAddData] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Copilot chat state
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState<
    { role: "user" | "assistant"; content?: string; answer?: ChatAnswer }[]
  >([]);
  const [asking, setAsking] = useState(false);

  // Initial user list load
  useEffect(() => {
    listUsers()
      .then((items) => {
        setUsers(items);
        if (items.length > 0) {
          if (authUser && items.some((u) => u.id === authUser.id)) {
            setSelectedUser(authUser.id);
          } else {
            const rahul = items.find((u) => u.id === "rahul");
            setSelectedUser(rahul ? rahul.id : items[0].id);
          }
        }
      })
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Unable to connect to backend"));
  }, [authUser]);

  // Load all user data when selected user or forecast horizon changes
  async function refreshUserData(userId: string, days: number = forecastDays) {
    if (!userId) return;
    try {
      const [h, c, f, g, b, t, r, ins, wc, crds, invs] = await Promise.all([
        getHealth(userId),
        getConfidence(userId),
        getForecast(userId, days),
        getGaps(userId),
        getBestMoves(userId),
        getTransactions(userId),
        getRecurring(userId),
        getInsights(userId),
        getWhatChanged(userId),
        getCards(userId).catch(() => []),
        getInvestments(userId).catch(() => []),
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
      setCards(crds);
      setInvestments(invs);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load persona analytics");
    }
  }

  useEffect(() => {
    if (selectedUser) {
      refreshUserData(selectedUser, forecastDays);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedUser, forecastDays]);

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
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top Header */}
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur-sm px-4 sm:px-8 py-3 shadow-2xs">
        <div className="flex flex-wrap items-center justify-between gap-3 max-w-7xl mx-auto">
          {/* Logo & Navigation */}
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2 group">
              <Logo size="sm" />
            </Link>

            <Link
              href="/"
              className="hidden md:inline-flex text-xs font-semibold text-slate-500 hover:text-blue-600 transition-colors border-l border-slate-200 pl-4"
            >
              ← Landing Page
            </Link>
          </div>

          {/* User selector & Actions */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Persona Switcher */}
            <div className="flex items-center gap-1.5 bg-slate-100 rounded-xl px-2.5 py-1 border border-slate-200/80">
              <span className="text-xs font-medium text-slate-500">Persona:</span>
              <select
                aria-label="Select Financial Persona"
                value={selectedUser}
                onChange={(e) => handlePersonaChange(e.target.value)}
                className="bg-transparent text-xs font-bold text-slate-800 outline-none cursor-pointer"
              >
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name} {u.persona_type ? `(${u.persona_type})` : ""}
                  </option>
                ))}
              </select>
            </div>

            {/* Language Toggle */}
            <div className="flex items-center rounded-xl border border-slate-200 bg-slate-100 p-0.5 text-xs font-semibold">
              <button
                type="button"
                onClick={() => setLanguage("en")}
                className={`rounded-lg px-2 py-0.5 transition-all ${
                  language === "en" ? "bg-white text-blue-600 shadow-2xs" : "text-slate-600 hover:text-slate-900"
                }`}
              >
                EN
              </button>
              <button
                type="button"
                onClick={() => setLanguage("hi")}
                className={`rounded-lg px-2 py-0.5 transition-all ${
                  language === "hi" ? "bg-white text-blue-600 shadow-2xs" : "text-slate-600 hover:text-slate-900"
                }`}
              >
                हिन्दी
              </button>
              <button
                type="button"
                onClick={() => setLanguage("mr")}
                className={`rounded-lg px-2 py-0.5 transition-all ${
                  language === "mr" ? "bg-white text-blue-600 shadow-2xs" : "text-slate-600 hover:text-slate-900"
                }`}
              >
                मराठी
              </button>
            </div>

            {/* Data Trust Modal */}
            <button
              type="button"
              onClick={() => setShowDataTrust(true)}
              className="flex items-center gap-1.5 rounded-xl border border-blue-200 bg-blue-50/70 hover:bg-blue-100/70 px-2.5 py-1 text-xs font-semibold text-blue-700 transition-colors"
            >
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Data Trust</span>
            </button>

            {/* Add Data */}
            <button
              type="button"
              onClick={() => setShowAddData(true)}
              className="flex items-center gap-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 px-3 py-1 text-xs font-semibold text-white shadow-xs transition-colors"
            >
              <PlusCircle className="h-3.5 w-3.5" />
              <span>Add Data</span>
            </button>

            {/* Auth / Account Profile */}
            {authUser ? (
              <div className="flex items-center gap-2 border-l border-slate-200 pl-2">
                <div className="h-7 w-7 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center text-xs font-bold">
                  {authUser.name.charAt(0).toUpperCase()}
                </div>
                <button
                  type="button"
                  onClick={logout}
                  title="Sign Out"
                  className="p-1 rounded-lg text-slate-500 hover:text-red-600 hover:bg-slate-100 transition-colors"
                >
                  <LogOut className="h-3.5 w-3.5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 border-l border-slate-200 pl-2">
                <Link
                  href="/login"
                  className="rounded-xl border border-slate-200 bg-white hover:bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-700 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="rounded-xl bg-slate-900 hover:bg-slate-800 px-2.5 py-1 text-xs font-semibold text-white transition-colors"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* 4 Navigation Tabs */}
        <div className="max-w-7xl mx-auto mt-2.5 flex items-center gap-1 border-t border-slate-100 pt-2">
          {[
            { id: "Home", label: "Health Overview", icon: HomeIcon },
            { id: "Ask", label: "Ask Copilot", icon: MessageSquare },
            { id: "Plan", label: "Plan & Forecast", icon: TrendingUp },
            { id: "Money", label: "Money & Spending", icon: CardIcon },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                type="button"
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
                  isActive
                    ? "bg-slate-900 text-white shadow-2xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${isActive ? "text-blue-400" : "text-slate-400"}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl mx-auto w-full p-4 sm:p-6 space-y-6">
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-3.5 text-xs text-red-700 flex items-center justify-between">
            <span>{error}</span>
            <button type="button" onClick={() => setError(null)} className="font-bold underline">
              Dismiss
            </button>
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 1: HOME DASHBOARD */}
        {/* ============================================================== */}
        {activeTab === "Home" && (
          <div className="space-y-6">
            {/* Top Grid: Health Score Ring + Danger Calendar */}
            <div className="grid gap-6 lg:grid-cols-12">
              <div className="lg:col-span-5 rounded-3xl border border-slate-200 bg-white p-6 shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-base font-extrabold text-slate-900">Financial Health Score</h2>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Deterministic composite of 6 weighted financial metrics
                      </p>
                    </div>
                    {confidence && (
                      <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-bold text-slate-700">
                        {confidence.score}% Confidence
                      </span>
                    )}
                  </div>

                  <div className="my-6 flex justify-center">
                    <ScoreRing score={health?.total_score ?? null} band={health?.band ?? "Calculating"} size={175} />
                  </div>
                </div>

                <div className="rounded-2xl bg-slate-50 p-4 border border-slate-100">
                  <div className="text-xs font-semibold text-slate-700">Audit Status</div>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {health?.summary || "Computed strictly via deterministic Python formulas."}
                  </p>
                  <button
                    type="button"
                    onClick={() => setActiveTab("Money")}
                    className="mt-3 inline-flex items-center gap-1 text-xs font-bold text-blue-600 hover:text-blue-700"
                  >
                    View All Supporting Transactions <ChevronRight className="h-3 w-3" />
                  </button>
                </div>
              </div>

              {/* 30-Day Danger Calendar */}
              <div className="lg:col-span-7 rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-base font-extrabold text-slate-900">30-Day Cash Danger Calendar</h2>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Predicted daily balance dips below safe reserves
                    </p>
                  </div>
                  <span className="text-xs font-semibold text-slate-500">
                    {gaps.length === 0 ? "🟢 No gaps detected" : `⚠️ ${gaps.length} Danger Days`}
                  </span>
                </div>
                <DangerCalendar
                  dates={forecast?.dates || []}
                  p10Balances={forecast?.p10_paise || []}
                  p50Balances={forecast?.p50_paise || []}
                  gaps={gaps}
                />
              </div>
            </div>

            {/* What Changed Diff Card */}
            {whatChanged && <WhatChangedCard whatChanged={whatChanged} />}

            {/* 6 Sub-Score Breakdown Cards */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-extrabold text-slate-900">6 Core Financial Health Drivers</h3>
                <span className="text-xs text-slate-500">Click any card to inspect provenance &amp; math</span>
              </div>
              <div className="grid gap-3.5 sm:grid-cols-2 lg:grid-cols-3">
                {health?.metrics &&
                  Object.entries(health.metrics).map(([key, m]) => (
                    <button
                      type="button"
                      key={key}
                      onClick={() => openMetricEvidence(key, m.plain_label)}
                      className="group rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-2xs hover:border-blue-400 hover:shadow-xs transition-all flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-slate-600">{m.plain_label}</span>
                          <span
                            className={`rounded-md px-1.5 py-0.5 text-[10px] font-bold ${
                              m.status === "ok"
                                ? "bg-emerald-50 text-emerald-700"
                                : m.status === "warning"
                                ? "bg-amber-50 text-amber-700"
                                : "bg-red-50 text-red-700"
                            }`}
                          >
                            {m.status.toUpperCase()}
                          </span>
                        </div>
                        <div className="mt-2 text-xl font-black text-slate-900">
                          {m.raw_value !== null ? `${Math.round(m.raw_value * 100)}%` : "N/A"}
                        </div>
                        <p className="mt-1 text-xs text-slate-500 line-clamp-2">{m.reason}</p>
                      </div>
                      <div className="mt-3 flex items-center justify-between text-[11px] font-bold text-blue-600 group-hover:translate-x-0.5 transition-transform">
                        <span>Inspect Evidence</span>
                        <ChevronRight className="h-3.5 w-3.5" />
                      </div>
                    </button>
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 2: ASK COPILOT (Fact / Prediction / Recommendation) */}
        {/* ============================================================== */}
        {activeTab === "Ask" && (
          <div className="grid gap-6 lg:grid-cols-12 max-w-5xl mx-auto">
            <div className="lg:col-span-12 space-y-4">
              {/* Copilot Header & Guidelines Badge */}
              <div className="rounded-2xl border border-blue-200 bg-gradient-to-r from-blue-50/80 to-indigo-50/50 p-4.5">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-blue-600 shrink-0" />
                  <h2 className="text-sm font-extrabold text-slate-900">
                    Deterministic Copilot: Mandatory 3-Section Format
                  </h2>
                </div>
                <p className="mt-1 text-xs text-slate-600">
                  ArthaPilot never hallucinates math. Every answer is structured with Blue Fact (verified past numbers),
                  Orange Prediction (with confidence %), and Green Recommendation (with simulated impact).
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {[
                    "Can I afford a ₹45,000 laptop?",
                    "When is my next cash gap?",
                    "What is my best next move?",
                    "Show my recurring subscriptions",
                  ].map((preset) => (
                    <button
                      type="button"
                      key={preset}
                      onClick={() => submitQuestion(preset)}
                      className="rounded-lg border border-blue-200/80 bg-white/90 px-2.5 py-1 text-xs font-semibold text-blue-800 hover:bg-blue-600 hover:text-white transition-all shadow-2xs"
                    >
                      {preset}
                    </button>
                  ))}
                </div>
              </div>

              {/* Chat Thread */}
              <div className="space-y-4 min-h-[350px]">
                {chatHistory.length === 0 ? (
                  <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 p-10 text-center bg-white/50">
                    <MessageSquare className="h-8 w-8 text-slate-300 mb-2" />
                    <p className="text-sm font-bold text-slate-700">Ask any question in plain English</p>
                    <p className="text-xs text-slate-400 mt-1 max-w-sm">
                      Try asking about affordability, upcoming balance dips, or debt payoff strategies.
                    </p>
                  </div>
                ) : (
                  chatHistory.map((msg, idx) => (
                    <div key={idx} className="space-y-3">
                      {msg.role === "user" ? (
                        <div className="flex justify-end">
                          <div className="rounded-2xl rounded-tr-xs bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-2xs max-w-xl">
                            {msg.content}
                          </div>
                        </div>
                      ) : (
                        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs space-y-4">
                          {msg.answer?.verdict && <VerdictCard verdict={msg.answer.verdict} />}
                          <p className="text-sm font-semibold text-slate-800">{msg.answer?.summary}</p>

                          {/* 3 Visible Sections: Fact, Prediction, Recommendation */}
                          <div className="grid gap-3 sm:grid-cols-3">
                            <div className="space-y-2">
                              {msg.answer?.facts.map((f, fIdx) => (
                                <FactCard key={fIdx} text={f.text} evidenceIds={f.evidence_ids} />
                              ))}
                            </div>
                            <div className="space-y-2">
                              {msg.answer?.predictions.map((p, pIdx) => (
                                <PredictionCard key={pIdx} text={p.text} confidence={p.confidence} reasons={p.confidence_reasons} />
                              ))}
                            </div>
                            <div className="space-y-2">
                              {msg.answer?.recommendations.map((r, rIdx) => (
                                <RecommendationCard key={rIdx} text={r.text} impact={r.impact} />
                              ))}
                            </div>
                          </div>

                          {/* Follow-up suggestions */}
                          {msg.answer?.follow_ups && msg.answer.follow_ups.length > 0 && (
                            <div className="border-t border-slate-100 pt-3">
                              <span className="text-[11px] font-bold text-slate-400 block mb-1.5">Suggested Next:</span>
                              <div className="flex flex-wrap gap-1.5">
                                {msg.answer.follow_ups.map((fu, fIdx) => (
                                  <button
                                    type="button"
                                    key={fIdx}
                                    onClick={() => submitQuestion(fu)}
                                    className="rounded-lg bg-slate-100 hover:bg-slate-200 px-2 py-1 text-xs text-slate-700 transition-colors"
                                  >
                                    {fu}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))
                )}
                {asking && (
                  <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white p-4 text-xs font-semibold text-slate-500 animate-pulse">
                    <Sparkles className="h-4 w-4 text-blue-600 animate-spin" />
                    Running Python analysis engine on real transaction rows...
                  </div>
                )}
              </div>

              {/* Chat Input Bar */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  submitQuestion();
                }}
                className="relative flex items-center"
              >
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask in English or switch to हिन्दी / मराठी above..."
                  className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3.5 pr-24 text-sm text-slate-900 shadow-xs focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  disabled={asking || !question.trim()}
                  className="absolute right-2 rounded-xl bg-blue-600 hover:bg-blue-700 px-4 py-2 text-xs font-bold text-white shadow-xs transition-all disabled:opacity-40"
                >
                  Ask
                </button>
              </form>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 3: PLAN & FORECAST (Monte Carlo, Affordability, Debt Payoff) */}
        {/* ============================================================== */}
        {activeTab === "Plan" && (
          <div className="space-y-6">
            {/* Monte Carlo Cash-Flow Chart */}
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-base font-extrabold text-slate-900">
                    Monte Carlo Cash-Flow Forecast ({forecastDays} Days)
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    1,000 statistical runs simulating variable spend distributions &amp; scheduled bills
                  </p>
                </div>
                {/* 30 / 60 / 90 Horizon Selector */}
                <div className="flex items-center rounded-xl border border-slate-200 bg-slate-100 p-0.5 text-xs font-semibold">
                  {[30, 60, 90].map((days) => (
                    <button
                      type="button"
                      key={days}
                      onClick={() => setForecastDays(days)}
                      className={`rounded-lg px-2.5 py-1 transition-all ${
                        forecastDays === days
                          ? "bg-white text-blue-600 shadow-2xs font-bold"
                          : "text-slate-600 hover:text-slate-900"
                      }`}
                    >
                      {days} Days
                    </button>
                  ))}
                </div>
              </div>

              <ForecastChart forecast={forecast} height={320} />
            </div>

            {/* Best Move Recommendation Card */}
            {bestMoves?.best_move && (
              <div className="rounded-3xl border-2 border-emerald-500/40 bg-gradient-to-r from-emerald-50/80 to-teal-50/60 p-6 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="rounded-md bg-emerald-600 text-white text-[10px] font-black uppercase px-2 py-0.5">
                      Top Recommended Move
                    </span>
                    <span className="text-xs font-bold text-emerald-800">
                      Impact: +{formatPaise(bestMoves.best_move.impact_paise)}/mo
                    </span>
                  </div>
                  <h3 className="text-base font-black text-slate-900 mt-1">{bestMoves.best_move.reason}</h3>
                  <p className="text-xs text-slate-600">Verified math: {bestMoves.evidence_formula}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-500 bg-white/80 border border-slate-200 rounded-lg px-2.5 py-1">
                    Effort: {bestMoves.best_move.effort_score}/5
                  </span>
                </div>
              </div>
            )}

            {/* Plan Tools Component (Affordability, Debt Payoff, Stress Test, Goals) */}
            <PlanTools
              userId={selectedUser}
              onRunAffordability={(amt) => checkAffordability(selectedUser, amt)}
              onRunGoal={(target, deadline) => planGoal(selectedUser, target, deadline)}
              onRunDebtPayoff={(extra, strat) => getDebtPayoff(selectedUser, extra, strat)}
              onRunStressTest={(scen, emi) => runStressTest(selectedUser, scen, emi)}
            />
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 4: MONEY & SPENDING (Tables for Transactions, Cards, Investments, Insights) */}
        {/* ============================================================== */}
        {activeTab === "Money" && (
          <div className="space-y-6">
            {/* Behavioural Insights */}
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-extrabold text-slate-900">7 Behavioural Spend Insights</h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Automated anomaly detection across weekend spikes, subscription hikes &amp; duplicate charges
                  </p>
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700">
                  {insights.length} Signals
                </span>
              </div>
              <InsightsList
                insights={insights}
                onEvidenceClick={(ins) =>
                  setEvidence({
                    title: ins.title,
                    summary: ins.message,
                    category: "Behavioural Insight",
                    transactionIds: ins.evidence_ids,
                  })
                }
              />
            </div>

            {/* Credit Cards & Limits Table */}
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-extrabold text-slate-900">Credit Cards &amp; Limits</h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Credit limits, outstanding balances, and calculated utilisation
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setShowAddData(true)}
                  className="text-xs font-bold text-blue-600 hover:underline"
                >
                  + Add Card
                </button>
              </div>

              {cards.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-100 text-slate-400 font-bold">
                        <th className="pb-2">Card Account</th>
                        <th className="pb-2">Balance</th>
                        <th className="pb-2">Credit Limit</th>
                        <th className="pb-2">Utilisation</th>
                        <th className="pb-2">APR</th>
                        <th className="pb-2">Min Due</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {cards.map((c) => {
                        const util = c.limit_paise > 0 ? Math.round((c.balance_paise / c.limit_paise) * 100) : 0;
                        return (
                          <tr key={c.id} className="hover:bg-slate-50">
                            <td className="py-2.5 font-bold text-slate-800">{c.id}</td>
                            <td className="py-2.5 font-bold text-slate-900">{formatPaise(c.balance_paise)}</td>
                            <td className="py-2.5 text-slate-600">{formatPaise(c.limit_paise)}</td>
                            <td className="py-2.5">
                              <span
                                className={`rounded px-1.5 py-0.5 font-bold text-[10px] ${
                                  util > 30 ? "bg-amber-100 text-amber-800" : "bg-emerald-100 text-emerald-800"
                                }`}
                              >
                                {util}%
                              </span>
                            </td>
                            <td className="py-2.5 text-slate-600">{c.apr}%</td>
                            <td className="py-2.5 text-slate-600">{formatPaise(c.min_due_paise)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-xs text-slate-400 py-3 text-center">No credit cards added for this persona.</p>
              )}
            </div>

            {/* Investments & Holdings Table */}
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-extrabold text-slate-900">Investments &amp; Wealth Holdings</h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Liquid portfolios, mutual fund SIPs, and asset allocations
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setShowAddData(true)}
                  className="text-xs font-bold text-blue-600 hover:underline"
                >
                  + Add Investment
                </button>
              </div>

              {investments.length > 0 ? (
                <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
                  {investments.map((inv) => (
                    <div key={inv.id} className="rounded-2xl border border-slate-200 bg-slate-50/60 p-4">
                      <span className="text-[11px] font-bold text-slate-500 uppercase">{inv.type}</span>
                      <div className="mt-1 text-lg font-extrabold text-slate-900">{formatPaise(inv.value_paise)}</div>
                      <div className="mt-2 text-xs text-slate-600 flex items-center justify-between border-t border-slate-200/60 pt-2">
                        <span>Monthly SIP:</span>
                        <span className="font-bold text-emerald-700">{formatPaise(inv.monthly_sip_paise)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 py-3 text-center">No investment holdings recorded.</p>
              )}
            </div>

            {/* Recurring Obligations Table */}
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-extrabold text-slate-900">Known Recurring Obligations</h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Automatically detected repeat bills with interval cadence and next due dates
                  </p>
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700">
                  {recurring.length} Items
                </span>
              </div>
              <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
                {recurring.map((item) => (
                  <div key={item.id} className="rounded-2xl border border-slate-200 p-4 bg-white">
                    <div className="flex justify-between items-baseline">
                      <span className="font-bold text-slate-900 text-sm truncate">{item.merchant}</span>
                      <span className="font-extrabold text-slate-900 text-sm">{formatPaise(item.amount_paise)}</span>
                    </div>
                    <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500">
                      <span>Due {formatDate(item.next_due_date)}</span>
                      <span className="rounded bg-blue-50 text-blue-700 font-bold px-1.5 py-0.5">
                        {Math.round(item.confidence * 100)}% Conf
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Categorised Transaction Table */}
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-extrabold text-slate-900">Verified Transactions Log</h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Deduplicated and standardised into integer paise (₹1 = 100 paise)
                  </p>
                </div>
                <span className="text-xs font-semibold text-slate-500">{transactions.length} rows</span>
              </div>
              <div className="overflow-x-auto max-h-[400px]">
                <table className="w-full text-left text-xs">
                  <thead className="sticky top-0 bg-white border-b border-slate-200">
                    <tr className="text-slate-400 font-bold">
                      <th className="pb-2">Date</th>
                      <th className="pb-2">Merchant</th>
                      <th className="pb-2">Category</th>
                      <th className="pb-2 text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {transactions.slice(0, 50).map((t) => (
                      <tr key={t.txn_id} className="hover:bg-slate-50">
                        <td className="py-2 font-mono text-slate-500">{formatDate(t.date)}</td>
                        <td className="py-2 font-semibold text-slate-800">{t.merchant}</td>
                        <td className="py-2">
                          <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-700">
                            {t.category || "Uncategorised"}
                          </span>
                        </td>
                        <td
                          className={`py-2 text-right font-bold ${
                            t.amount_paise > 0 ? "text-emerald-700" : "text-slate-900"
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

      {/* Slide-out Evidence Drawer */}
      <EvidenceDrawer evidence={evidence} onClose={() => setEvidence(null)} />

      {/* Modals */}
      <DataTrustModal isOpen={showDataTrust} onClose={() => setShowDataTrust(false)} />
      <AddDataModal
        isOpen={showAddData}
        onClose={() => setShowAddData(false)}
        userId={selectedUser}
        onSuccess={() => refreshUserData(selectedUser)}
      />
    </div>
  );
}
