const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type User = {
  id: string;
  name: string;
  persona_type: string | null;
  source: string;
};

export type Health = {
  total_score: number | null;
  indicative_score: number | null;
  band: string;
  score_coverage: number;
  months_used: number;
  summary: string;
  metrics: Record<string, {
    plain_label: string;
    raw_value: number | null;
    unit: string;
    status: string;
    reason: string;
    evidence: Record<string, unknown>;
    sub_score: number | null;
  }>;
};

export type Confidence = {
  score: number;
  level: string;
  reasons: string[];
  how_to_improve: string[];
  months_of_data: number;
  uncategorised_share: number;
};

export type ChatAnswer = {
  summary: string;
  facts: { text: string; evidence_ids: string[] }[];
  predictions: { text: string; confidence: number; confidence_reasons: string[] }[];
  recommendations: { text: string; impact: Record<string, unknown> }[];
  verdict?: string | null;
  follow_ups: string[];
};

export type Forecast = {
  dates: string[];
  p10_paise: number[];
  p50_paise: number[];
  p90_paise: number[];
  probability_below_zero: number[];
  runs: number;
  seed: number;
  start_balance_paise: number;
};

export type Gap = {
  date: string;
  expected_balance_paise: number;
  probability_below_zero: number;
  evidence: string;
};

export type BestMove = {
  action: { type: string; category?: string; percent?: number; merchant?: string; amount_paise?: number };
  impact_paise: number;
  effort_score: number;
  reason: string;
};

export type BestMoves = {
  best_move: BestMove | null;
  alternatives: BestMove[];
  evidence_formula: string;
};

export type Transaction = {
  txn_id: string;
  date: string;
  amount_paise: number;
  merchant: string;
  category: string;
  category_confidence: number;
  is_recurring: boolean;
};

export type RecurringItem = {
  id: string;
  merchant: string;
  amount_paise: number;
  interval_days: number;
  next_due_date: string;
  confidence: number;
  txn_ids: string[];
};

export type WhatChanged = {
  snapshot_id: string | null;
  score_before: number | null;
  score_after: number | null;
  score_delta: number | null;
  confidence_before: number | null;
  confidence_after: number | null;
  new_gaps: string[];
  removed_gaps: string[];
  recommendation_changed: boolean;
  summary: string;
  evidence: string[];
};

export type Insight = {
  type: string;
  title: string;
  message: string;
  severity: "low" | "medium" | "high";
  evidence_ids: string[];
  data: Record<string, unknown>;
};

export type DebtPayoff = {
  strategy: string;
  baseline_months: number;
  accelerated_months: number;
  months_saved: number;
  baseline_interest_paise: number;
  accelerated_interest_paise: number;
  interest_saved_paise: number;
  payoff_order: string[];
  formula: string;
  evidence_debt_ids: string[];
};

export type StressResult = {
  scenario: string;
  survival_days: number;
  first_breach_date: string | null;
  forecast: Forecast;
};

export type AffordabilityResult = {
  verdict: "Yes" | "Risky" | "No";
  amount_paise: number;
  balance_before_paise: number;
  balance_after_paise: number;
  safe_threshold_paise: number;
  safer_alternative: string | null;
  formula: string;
};

export type GoalResult = {
  target_paise: number;
  deadline: string;
  months: number;
  required_monthly_paise: number;
  current_monthly_surplus_paise: number;
  feasible: boolean;
  formula: string;
};

export function formatPaise(paise: number): string {
  const rupees = Math.round(paise / 100);
  const isNegative = rupees < 0;
  const absRupees = Math.abs(rupees);
  return `${isNegative ? "-" : ""}₹${absRupees.toLocaleString("en-IN")}`;
}

export function formatDate(isoDate: string): string {
  try {
    const d = new Date(isoDate);
    return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
  } catch {
    return isoDate;
  }
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export async function listUsers(): Promise<User[]> {
  return getJson<User[]>("/users");
}

export async function loadPersona(userId: string): Promise<{ user_id: string; transactions_loaded: number }> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/load-persona`, {
    method: "POST",
  });
  if (!response.ok) throw new Error(`Loading persona failed (${response.status})`);
  return response.json();
}

export async function getHealth(userId: string): Promise<Health> {
  return getJson<Health>(`/users/${encodeURIComponent(userId)}/health`);
}

export async function getConfidence(userId: string): Promise<Confidence> {
  return getJson<Confidence>(`/users/${encodeURIComponent(userId)}/confidence`);
}

export async function askCopilot(userId: string, question: string, language: string = "en"): Promise<ChatAnswer> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, language }),
  });
  if (!response.ok) throw new Error(`Chat request failed (${response.status})`);
  return response.json() as Promise<ChatAnswer>;
}

export async function getForecast(userId: string, days: number = 90): Promise<Forecast> {
  return getJson<Forecast>(`/users/${encodeURIComponent(userId)}/forecast?days=${days}&runs=500&seed=42`);
}

export async function getGaps(userId: string): Promise<Gap[]> {
  return getJson<Gap[]>(`/users/${encodeURIComponent(userId)}/gaps`);
}

export async function getBestMoves(userId: string): Promise<BestMoves> {
  return getJson<BestMoves>(`/users/${encodeURIComponent(userId)}/best-moves`);
}

export async function getTransactions(userId: string, category?: string): Promise<Transaction[]> {
  const query = category ? `&category=${encodeURIComponent(category)}` : "";
  return getJson<Transaction[]>(`/users/${encodeURIComponent(userId)}/transactions?limit=250${query}`);
}

export async function getRecurring(userId: string): Promise<RecurringItem[]> {
  return getJson<RecurringItem[]>(`/users/${encodeURIComponent(userId)}/recurring`);
}

export async function getInsights(userId: string): Promise<Insight[]> {
  return getJson<Insight[]>(`/users/${encodeURIComponent(userId)}/insights`);
}

export async function getWhatChanged(userId: string): Promise<WhatChanged> {
  return getJson<WhatChanged>(`/users/${encodeURIComponent(userId)}/what-changed`);
}

export async function addManualLoan(userId: string, outstanding_paise: number, emi_paise: number, type: string = "Manual EMI"): Promise<void> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/loans`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ outstanding_paise, emi_paise, type }),
  });
  if (!response.ok) throw new Error(`Loan update failed (${response.status})`);
}

export async function addManualTransaction(userId: string, date: string, amount_paise: number, category: string, merchant: string): Promise<void> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/transactions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date, amount_paise, category, merchant, description: merchant }),
  });
  if (!response.ok) throw new Error(`Transaction update failed (${response.status})`);
}

export async function addIncomeChange(userId: string, amount_paise: number, date: string, description: string): Promise<void> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/income-change`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount_paise, date, description }),
  });
  if (!response.ok) throw new Error(`Income change failed (${response.status})`);
}

export async function runStressTest(userId: string, scenario: string, new_emi_paise: number = 0): Promise<StressResult> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/stress-test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario, new_emi_paise }),
  });
  if (!response.ok) throw new Error(`Stress test failed (${response.status})`);
  return response.json();
}

export async function checkAffordability(userId: string, amount_paise: number): Promise<AffordabilityResult> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/affordability`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount_paise }),
  });
  if (!response.ok) throw new Error(`Affordability check failed (${response.status})`);
  return response.json();
}

export async function planGoal(userId: string, target_paise: number, deadline: string): Promise<GoalResult> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/goal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_paise, deadline }),
  });
  if (!response.ok) throw new Error(`Goal plan failed (${response.status})`);
  return response.json();
}

export async function getDebtPayoff(userId: string, extra_monthly_paise: number, strategy: string): Promise<DebtPayoff> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/debt-payoff`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ extra_monthly_paise, strategy }),
  });
  if (!response.ok) throw new Error(`Debt payoff calculation failed (${response.status})`);
  return response.json();
}

export async function simulateAction(userId: string, action: { type: string; category?: string; percent?: number; merchant?: string; amount_paise?: number }): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(action),
  });
  if (!response.ok) throw new Error(`Simulation failed (${response.status})`);
  return response.json();
}

export async function uploadStatement(file: File): Promise<{ user_id?: string; transactions_loaded?: number; status?: string; mapping?: unknown }> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_URL}/upload`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed (${response.status})`);
  }
  return response.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`, { cache: "no-store" });
    if (!response.ok) return false;
    const data: unknown = await response.json();
    return typeof data === "object" && data !== null && "status" in data && data.status === "ok";
  } catch {
    return false;
  }
}
