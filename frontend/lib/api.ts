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
  action: { type: string; category?: string; percent?: number };
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

export async function getHealth(userId: string): Promise<Health> {
  return getJson<Health>(`/users/${encodeURIComponent(userId)}/health`);
}

export async function getConfidence(userId: string): Promise<Confidence> {
  return getJson<Confidence>(`/users/${encodeURIComponent(userId)}/confidence`);
}

export async function askCopilot(userId: string, question: string): Promise<ChatAnswer> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, language: "en" }),
  });
  if (!response.ok) throw new Error(`Chat request failed (${response.status})`);
  return response.json() as Promise<ChatAnswer>;
}

export async function getForecast(userId: string): Promise<Forecast> {
  return getJson<Forecast>(`/users/${encodeURIComponent(userId)}/forecast?days=30&runs=250&seed=42`);
}

export async function getGaps(userId: string): Promise<Gap[]> {
  return getJson<Gap[]>(`/users/${encodeURIComponent(userId)}/gaps`);
}

export async function getBestMoves(userId: string): Promise<BestMoves> {
  return getJson<BestMoves>(`/users/${encodeURIComponent(userId)}/best-moves`);
}

export async function getTransactions(userId: string): Promise<Transaction[]> {
  return getJson<Transaction[]>(`/users/${encodeURIComponent(userId)}/transactions?limit=250`);
}

export async function getRecurring(userId: string): Promise<RecurringItem[]> {
  return getJson<RecurringItem[]>(`/users/${encodeURIComponent(userId)}/recurring`);
}

export async function getWhatChanged(userId: string): Promise<WhatChanged> {
  return getJson<WhatChanged>(`/users/${encodeURIComponent(userId)}/what-changed`);
}

export async function addManualLoan(userId: string, outstanding_paise: number, emi_paise: number): Promise<void> {
  const response = await fetch(`${API_URL}/users/${encodeURIComponent(userId)}/loans`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ outstanding_paise, emi_paise, type: "Manual EMI" }),
  });
  if (!response.ok) throw new Error(`Loan update failed (${response.status})`);
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return false;
    }

    const data: unknown = await response.json();
    return (
      typeof data === "object" &&
      data !== null &&
      "status" in data &&
      data.status === "ok"
    );
  } catch {
    return false;
  }
}
