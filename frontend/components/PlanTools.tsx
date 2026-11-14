"use client";

import React, { useState } from "react";
import { formatPaise, formatDate, AffordabilityResult, GoalResult, DebtPayoff, StressResult } from "@/lib/api";
import { VerdictCard } from "./Cards";
import { Calculator, ShieldAlert, Target, ArrowRight, CheckCircle, Flame } from "lucide-react";

interface PlanToolsProps {
  userId?: string;
  onRunAffordability: (amountPaise: number) => Promise<AffordabilityResult>;
  onRunGoal: (targetPaise: number, deadline: string) => Promise<GoalResult>;
  onRunDebtPayoff: (extraMonthlyPaise: number, strategy: string) => Promise<DebtPayoff>;
  onRunStressTest: (scenario: string, emiPaise: number) => Promise<StressResult>;
  onOpenEvidence?: (title: string, summary: string, formula?: string) => void;
}

export function PlanTools({
  onRunAffordability,
  onRunGoal,
  onRunDebtPayoff,
  onRunStressTest,
}: PlanToolsProps) {
  const [activeSubTab, setActiveSubTab] = useState<"affordability" | "debt" | "stress" | "goal">("affordability");

  // Affordability state
  const [affordAmount, setAffordAmount] = useState("45000");
  const [affordResult, setAffordResult] = useState<AffordabilityResult | null>(null);
  const [affordLoading, setAffordLoading] = useState(false);

  // Goal state
  const [goalAmount, setGoalAmount] = useState("100000");
  const [goalMonths, setGoalMonths] = useState("8");
  const [goalResult, setGoalResult] = useState<GoalResult | null>(null);
  const [goalLoading, setGoalLoading] = useState(false);

  // Debt payoff state
  const [debtExtra, setDebtExtra] = useState("5000");
  const [debtStrategy, setDebtStrategy] = useState("avalanche");
  const [debtResult, setDebtResult] = useState<DebtPayoff | null>(null);
  const [debtLoading, setDebtLoading] = useState(false);

  // Stress test state
  const [stressScenario, setStressScenario] = useState("income_stops_2_months");
  const [stressNewEmi] = useState("12000");
  const [stressResult, setStressResult] = useState<StressResult | null>(null);
  const [stressLoading, setStressLoading] = useState(false);

  async function handleAffordability(e: React.FormEvent) {
    e.preventDefault();
    const rs = Number(affordAmount);
    if (!rs || rs <= 0) return;
    setAffordLoading(true);
    try {
      const res = await onRunAffordability(rs * 100);
      setAffordResult(res);
    } finally {
      setAffordLoading(false);
    }
  }

  async function handleGoal(e: React.FormEvent) {
    e.preventDefault();
    const rs = Number(goalAmount);
    const m = Number(goalMonths);
    if (!rs || rs <= 0 || !m || m <= 0) return;
    setGoalLoading(true);
    try {
      const targetDate = new Date();
      targetDate.setMonth(targetDate.getMonth() + m);
      const iso = targetDate.toISOString().split("T")[0];
      const res = await onRunGoal(rs * 100, iso);
      setGoalResult(res);
    } finally {
      setGoalLoading(false);
    }
  }

  async function handleDebt(e: React.FormEvent) {
    e.preventDefault();
    const extraRs = Number(debtExtra) || 0;
    setDebtLoading(true);
    try {
      const res = await onRunDebtPayoff(extraRs * 100, debtStrategy);
      setDebtResult(res);
    } finally {
      setDebtLoading(false);
    }
  }

  async function handleStress(scenario: string) {
    setStressScenario(scenario);
    setStressLoading(true);
    try {
      const emiRs = scenario === "new_emi" ? Number(stressNewEmi) || 12000 : 0;
      const res = await onRunStressTest(scenario, emiRs * 100);
      setStressResult(res);
    } finally {
      setStressLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Sub tabs */}
      <div className="flex gap-2 border-b pb-3 overflow-x-auto">
        {[
          { id: "affordability", label: "Can I Afford It?", icon: Calculator },
          { id: "debt", label: "Debt Elimination (Avalanche/Snowball)", icon: Flame },
          { id: "stress", label: "Stress Testing & Shocks", icon: ShieldAlert },
          { id: "goal", label: "Goal Savings Planner", icon: Target },
        ].map((tab) => {
          const Icon = tab.icon;
          const isSelected = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveSubTab(tab.id as typeof activeSubTab)}
              className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-semibold whitespace-nowrap transition-all ${
                isSelected
                  ? "bg-blue-700 text-white shadow-sm"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200/80"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* 1. Affordability Tool */}
      {activeSubTab === "affordability" && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Affordability Verdict Calculator</h3>
            <p className="mt-1 text-xs text-slate-500">
              Simulates purchasing power against your liquid balance and safe buffer (1 week average expenses).
            </p>
          </div>

          <form onSubmit={handleAffordability} className="flex flex-col sm:flex-row gap-3 items-end">
            <div className="flex-1">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                Purchase Amount (₹)
              </label>
              <input
                type="number"
                min="100"
                step="100"
                value={affordAmount}
                onChange={(e) => setAffordAmount(e.target.value)}
                className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
                placeholder="e.g. 45000"
              />
            </div>
            <button
              type="submit"
              disabled={affordLoading}
              className="rounded-xl bg-blue-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-50 transition-colors h-11"
            >
              {affordLoading ? "Evaluating..." : "Check Affordability"}
            </button>
          </form>

          {affordResult && (
            <div className="space-y-4 pt-2">
              <VerdictCard
                verdict={affordResult.verdict}
                title={`Verdict: ${affordResult.verdict}`}
                reason={`Purchasing for ₹${Number(affordAmount).toLocaleString("en-IN")} leaves you with ${formatPaise(
                  affordResult.balance_after_paise
                )} liquid balance (your safe operating reserve is ${formatPaise(affordResult.safe_threshold_paise)}).`}
                saferAlternative={affordResult.safer_alternative}
              />

              <div className="grid grid-cols-3 gap-3 text-center text-xs">
                <div className="rounded-xl bg-slate-50 border p-3">
                  <span className="text-slate-400 block truncate">Liquid Before</span>
                  <span className="font-bold text-slate-900 mt-1 block">
                    {formatPaise(affordResult.balance_before_paise)}
                  </span>
                </div>
                <div className="rounded-xl bg-slate-50 border p-3">
                  <span className="text-slate-400 block truncate">Liquid After</span>
                  <span className="font-bold text-slate-900 mt-1 block">
                    {formatPaise(affordResult.balance_after_paise)}
                  </span>
                </div>
                <div className="rounded-xl bg-slate-50 border p-3">
                  <span className="text-slate-400 block truncate">Safe Reserve Threshold</span>
                  <span className="font-bold text-slate-900 mt-1 block">
                    {formatPaise(affordResult.safe_threshold_paise)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 2. Debt Payoff Tool */}
      {activeSubTab === "debt" && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Accelerated Debt Payoff Engine</h3>
            <p className="mt-1 text-xs text-slate-500">
              Compare Avalanche (highest APR first) and Snowball (lowest balance first) to eliminate debt and minimize total interest.
            </p>
          </div>

          <form onSubmit={handleDebt} className="grid sm:grid-cols-3 gap-3 items-end">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                Extra Monthly Payment (₹)
              </label>
              <input
                type="number"
                min="0"
                step="500"
                value={debtExtra}
                onChange={(e) => setDebtExtra(e.target.value)}
                className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                Strategy
              </label>
              <select
                value={debtStrategy}
                onChange={(e) => setDebtStrategy(e.target.value)}
                className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
              >
                <option value="avalanche">Avalanche (Highest APR first)</option>
                <option value="snowball">Snowball (Smallest Balance first)</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={debtLoading}
              className="rounded-xl bg-blue-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-50 transition-colors h-11"
            >
              {debtLoading ? "Calculating..." : "Compute Payoff Plan"}
            </button>
          </form>

          {debtResult && (
            <div className="space-y-4 pt-2">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-3.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-800 block">
                    Interest Saved
                  </span>
                  <span className="text-xl font-bold text-emerald-900 mt-1 block">
                    {formatPaise(debtResult.interest_saved_paise)}
                  </span>
                </div>
                <div className="rounded-xl bg-blue-50 border border-blue-200 p-3.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-blue-800 block">
                    Time Saved
                  </span>
                  <span className="text-xl font-bold text-blue-900 mt-1 block">
                    {debtResult.months_saved} Months
                  </span>
                </div>
                <div className="rounded-xl bg-slate-50 border p-3.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">
                    Debt-Free In
                  </span>
                  <span className="text-xl font-bold text-slate-900 mt-1 block">
                    {debtResult.accelerated_months} Months
                  </span>
                  <span className="text-[10px] text-slate-400">(was {debtResult.baseline_months} mos)</span>
                </div>
                <div className="rounded-xl bg-slate-50 border p-3.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">
                    Strategy Applied
                  </span>
                  <span className="text-base font-bold text-slate-900 mt-1 capitalize block">
                    {debtResult.strategy}
                  </span>
                </div>
              </div>

              {debtResult.payoff_order.length > 0 && (
                <div className="rounded-xl border p-4 bg-slate-50/50">
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                    Optimal Debt Clearance Sequence:
                  </p>
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    {debtResult.payoff_order.map((id, index) => (
                      <React.Fragment key={id}>
                        <span className="rounded-lg bg-white border border-slate-300 px-3 py-1 font-semibold text-slate-800 shadow-2xs">
                          {index + 1}. {id}
                        </span>
                        {index < debtResult.payoff_order.length - 1 && (
                          <ArrowRight className="h-3.5 w-3.5 text-slate-400" />
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* 3. Stress Tester Tool */}
      {activeSubTab === "stress" && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Financial Stress Tests & Shocks</h3>
            <p className="mt-1 text-xs text-slate-500">
              Subject your cash flow to pre-built economic shocks. Evaluates survival time and earliest breach date.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {[
              { id: "income_stops_1_month", label: "Income Stops 1 Month", desc: "Salary paused for 30 days" },
              { id: "income_stops_2_months", label: "Income Stops 2 Months", desc: "Salary paused for 60 days" },
              { id: "income_stops_3_months", label: "Income Stops 3 Months", desc: "Severe income hiatus (90 days)" },
              { id: "expenses_rise_15", label: "Expenses Rise 15%", desc: "Inflationary spike across all items" },
              { id: "emergency_expense_50000", label: "₹50,000 Emergency", desc: "One-off medical or repair shock" },
              { id: "new_emi", label: "New ₹12,000 EMI", desc: "Added debt payment shock" },
            ].map((sc) => (
              <button
                key={sc.id}
                type="button"
                onClick={() => handleStress(sc.id)}
                disabled={stressLoading}
                className={`p-3.5 rounded-xl border text-left transition-all ${
                  stressScenario === sc.id
                    ? "border-blue-600 bg-blue-50/70 ring-1 ring-blue-600"
                    : "border-slate-200 bg-white hover:bg-slate-50"
                }`}
              >
                <span className="font-bold text-xs text-slate-900 block">{sc.label}</span>
                <span className="text-[11px] text-slate-500 mt-1 block">{sc.desc}</span>
              </button>
            ))}
          </div>

          {stressResult && (
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-5 space-y-3 pt-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Shock Outcome</span>
                <span className="rounded-full bg-slate-200 px-2.5 py-0.5 text-xs font-semibold text-slate-800">
                  {stressResult.scenario}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-center">
                <div className="bg-white rounded-xl border p-4">
                  <span className="text-xs text-slate-400 uppercase tracking-wider block">Survival Buffer</span>
                  <span className="text-2xl font-bold text-blue-700 mt-1 block">
                    {stressResult.survival_days} Days
                  </span>
                </div>
                <div className="bg-white rounded-xl border p-4">
                  <span className="text-xs text-slate-400 uppercase tracking-wider block">Earliest Breach Date</span>
                  <span className="text-2xl font-bold text-slate-900 mt-1 block">
                    {stressResult.first_breach_date ? formatDate(stressResult.first_breach_date) : "No Breach (Safe)"}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 4. Goal Planner */}
      {activeSubTab === "goal" && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Systematic Goal Planner</h3>
            <p className="mt-1 text-xs text-slate-500">
              Calculate exact monthly contributions needed to achieve your target amount by your deadline date.
            </p>
          </div>

          <form onSubmit={handleGoal} className="grid sm:grid-cols-3 gap-3 items-end">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                Target Amount (₹)
              </label>
              <input
                type="number"
                min="1000"
                step="1000"
                value={goalAmount}
                onChange={(e) => setGoalAmount(e.target.value)}
                className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                Timeline (Months)
              </label>
              <input
                type="number"
                min="1"
                max="120"
                value={goalMonths}
                onChange={(e) => setGoalMonths(e.target.value)}
                className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
              />
            </div>
            <button
              type="submit"
              disabled={goalLoading}
              className="rounded-xl bg-blue-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-50 transition-colors h-11"
            >
              {goalLoading ? "Planning..." : "Compute Goal Plan"}
            </button>
          </form>

          {goalResult && (
            <div className="space-y-4 pt-2">
              <div
                className={`rounded-xl border p-4 flex items-center justify-between ${
                  goalResult.feasible
                    ? "bg-emerald-50 border-emerald-300 text-emerald-900"
                    : "bg-amber-50 border-amber-300 text-amber-900"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <CheckCircle className="h-5 w-5" />
                  <span className="text-sm font-bold">
                    {goalResult.feasible
                      ? "Goal is Feasible with your current monthly surplus!"
                      : "Deficit: Required monthly savings exceed your current average surplus."}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 text-center text-xs">
                <div className="rounded-xl bg-slate-50 border p-3">
                  <span className="text-slate-400 block truncate">Required Monthly</span>
                  <span className="font-bold text-slate-900 text-base mt-1 block">
                    {formatPaise(goalResult.required_monthly_paise)}
                  </span>
                </div>
                <div className="rounded-xl bg-slate-50 border p-3">
                  <span className="text-slate-400 block truncate">Current Monthly Surplus</span>
                  <span className="font-bold text-slate-900 text-base mt-1 block">
                    {formatPaise(goalResult.current_monthly_surplus_paise)}
                  </span>
                </div>
                <div className="rounded-xl bg-slate-50 border p-3">
                  <span className="text-slate-400 block truncate">Target Deadline</span>
                  <span className="font-bold text-slate-900 text-base mt-1 block">
                    {formatDate(goalResult.deadline)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
