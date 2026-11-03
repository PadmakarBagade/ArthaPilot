"use client";

import { type FormEvent, useEffect, useState } from "react";

import { askCopilot, BestMoves, ChatAnswer, Confidence, Forecast, Gap, getBestMoves, getConfidence, getForecast, getGaps, getHealth, Health, listUsers, User } from "@/lib/api";

export default function Home() {
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [health, setHealth] = useState<Health | null>(null);
  const [confidence, setConfidence] = useState<Confidence | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("Home");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<ChatAnswer | null>(null);
  const [asking, setAsking] = useState(false);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [gaps, setGaps] = useState<Gap[]>([]);
  const [bestMoves, setBestMoves] = useState<BestMoves | null>(null);

  useEffect(() => {
    listUsers()
      .then((items) => {
        setUsers(items);
        if (items[0]) setSelectedUser(items[0].id);
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Unable to load users"));
  }, []);

  useEffect(() => {
    if (!selectedUser) return;
    Promise.all([getHealth(selectedUser), getConfidence(selectedUser), getForecast(selectedUser), getGaps(selectedUser), getBestMoves(selectedUser)])
      .then(([nextHealth, nextConfidence, nextForecast, nextGaps, nextBestMoves]) => {
        setHealth(nextHealth);
        setConfidence(nextConfidence);
        setForecast(nextForecast);
        setGaps(nextGaps);
        setBestMoves(nextBestMoves);
        setError(null);
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Unable to load dashboard"));
  }, [selectedUser]);

  const score = health?.total_score;

  async function submitQuestion(event: FormEvent) {
    event.preventDefault();
    if (!selectedUser || !question.trim()) return;
    setAsking(true);
    try {
      setAnswer(await askCopilot(selectedUser, question.trim()));
      setError(null);
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Unable to ask copilot");
    } finally {
      setAsking(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-950 sm:px-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="flex flex-col gap-4 border-b pb-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-blue-700">ArthaPilot</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight">Your financial health, clearly explained.</h1>
            <p className="mt-2 text-slate-600">Facts from your data. Predictions with confidence. Actions with simulated impact.</p>
          </div>
          <label className="text-sm font-medium">
            Demo profile
            <select className="mt-1 block min-w-48 rounded-md border bg-white px-3 py-2" value={selectedUser} onChange={(event) => setSelectedUser(event.target.value)}>
              {users.map((user) => <option key={user.id} value={user.id}>{user.name}</option>)}
            </select>
          </label>
        </header>

        <nav className="flex gap-2 overflow-x-auto" aria-label="Primary navigation">
          {["Home", "Spending", "Forecast", "Ask", "Plan"].map((tab) => (
            <button key={tab} type="button" onClick={() => setActiveTab(tab)} className={`rounded-full px-4 py-2 text-sm font-medium ${activeTab === tab ? "bg-blue-700 text-white" : "bg-white text-slate-600 ring-1 ring-slate-200"}`}>{tab}</button>
          ))}
        </nav>

        {error && <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">{error}</div>}
        {activeTab === "Ask" && <section className="space-y-4 rounded-xl border bg-white p-6">
          <div><h2 className="text-xl font-semibold">Ask ArthaPilot</h2><p className="mt-1 text-sm text-slate-600">The copilot explains backend results; it does not calculate money.</p></div>
          <div className="flex flex-wrap gap-2">{["How healthy are my finances?", "What recurring bills do I have?", "How confident is this analysis?"].map((item) => <button key={item} type="button" className="rounded-full bg-slate-100 px-3 py-2 text-sm text-slate-700" onClick={() => setQuestion(item)}>{item}</button>)}</div>
          <form onSubmit={submitQuestion} className="flex flex-col gap-2 sm:flex-row">
            <input aria-label="Ask a financial question" className="min-h-11 flex-1 rounded-md border px-3" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask a question about this profile" />
            <button type="submit" disabled={asking || !question.trim()} className="min-h-11 rounded-md bg-blue-700 px-5 font-medium text-white disabled:opacity-50">{asking ? "Checking..." : "Ask"}</button>
          </form>
          {answer && <div className="space-y-3">
            <p className="font-medium">{answer.summary}</p>
            <div className="grid gap-3 md:grid-cols-3">
              <article className="rounded-lg border-l-4 border-blue-500 bg-blue-50 p-4"><p className="text-xs font-semibold uppercase text-blue-700">Observed Fact</p>{answer.facts.map((item) => <p key={item.text} className="mt-2 text-sm">{item.text}<span className="mt-1 block text-xs text-blue-700">Evidence: {item.evidence_ids.join(", ") || "formula/tool result"}</span></p>)}</article>
              <article className="rounded-lg border-l-4 border-amber-500 bg-amber-50 p-4"><p className="text-xs font-semibold uppercase text-amber-700">Prediction</p>{answer.predictions.map((item) => <p key={item.text} className="mt-2 text-sm">{item.text}<span className="mt-1 block text-xs text-amber-700">Confidence: {item.confidence}%</span></p>)}</article>
              <article className="rounded-lg border-l-4 border-emerald-500 bg-emerald-50 p-4"><p className="text-xs font-semibold uppercase text-emerald-700">Recommendation</p>{answer.recommendations.map((item) => <p key={item.text} className="mt-2 text-sm">{item.text}</p>)}</article>
            </div>
          </div>}
        </section>}
        {activeTab !== "Home" && activeTab !== "Ask" && activeTab !== "Forecast" && activeTab !== "Plan" && <section className="rounded-xl border bg-white p-6"><h2 className="text-xl font-semibold">{activeTab}</h2><p className="mt-2 text-slate-600">This workspace is connected to the typed API and will display verified {activeTab.toLowerCase()} results as those services are enabled.</p></section>}
        {activeTab === "Forecast" && <section className="space-y-5 rounded-xl border bg-white p-6">
          <div><h2 className="text-xl font-semibold">30-day cash-flow outlook</h2><p className="mt-1 text-sm text-slate-600">The chart shows the likely path and the tested 10th–90th percentile range. Values are integer paise from the forecast service.</p></div>
          {forecast && <div className="overflow-x-auto">
            <div className="grid min-w-[720px] grid-cols-6 gap-2 text-xs">
              {forecast.dates.filter((_, index) => index % 5 === 0).map((date, index) => {
                const sourceIndex = index * 5;
                const p10 = forecast.p10_paise[sourceIndex];
                const p50 = forecast.p50_paise[sourceIndex];
                const p90 = forecast.p90_paise[sourceIndex];
                const max = Math.max(...forecast.p90_paise.map(Math.abs), 1);
                return <div key={date} className="rounded-lg bg-slate-50 p-3"><p className="font-medium">{date.slice(5)}</p><div className="mt-3 h-32 flex items-end gap-1"><span className="w-1/3 rounded-t bg-blue-200" style={{ height: `${Math.max(4, Math.abs(p10) / max * 100)}%` }} /><span className="w-1/3 rounded-t bg-blue-600" style={{ height: `${Math.max(4, Math.abs(p50) / max * 100)}%` }} /><span className="w-1/3 rounded-t bg-blue-100" style={{ height: `${Math.max(4, Math.abs(p90) / max * 100)}%` }} /></div><p className="mt-2 text-slate-600">Likely ₹{Math.round(p50 / 100).toLocaleString("en-IN")}</p></div>;
              })}
            </div>
          </div>}
          <div className="grid gap-3 md:grid-cols-2"><div className="rounded-lg bg-slate-50 p-4"><p className="font-medium">Legend</p><p className="mt-2 text-sm text-slate-600">Dark blue: likely · light blue: forecast range · seed {forecast?.seed ?? "—"} · {forecast?.runs ?? 0} simulations</p></div><div className="rounded-lg bg-red-50 p-4"><p className="font-medium text-red-800">Danger days</p><p className="mt-2 text-sm text-red-700">{gaps.length ? `${gaps.length} days fall below the configured safe threshold.` : "No safe-threshold breaches detected."}</p>{gaps.slice(0, 3).map((gap) => <p key={gap.date} className="mt-1 text-xs">{gap.date}: ₹{Math.round(gap.expected_balance_paise / 100).toLocaleString("en-IN")}</p>)}</div></div>
        </section>}
        {activeTab === "Plan" && <section className="space-y-5 rounded-xl border bg-white p-6">
          <div><h2 className="text-xl font-semibold">Best Next Move</h2><p className="mt-1 text-sm text-slate-600">Recommendations are ranked from deterministic simulated surplus impact divided by effort.</p></div>
          {bestMoves?.best_move ? <div className="rounded-lg border-l-4 border-emerald-500 bg-emerald-50 p-4"><p className="text-xs font-semibold uppercase text-emerald-700">Recommendation</p><p className="mt-2 font-semibold">{bestMoves.best_move.reason}</p><p className="mt-1 text-sm text-emerald-800">Simulated surplus impact: ₹{Math.round(bestMoves.best_move.impact_paise / 100).toLocaleString("en-IN")} · effort {bestMoves.best_move.effort_score}/10</p></div> : <p className="rounded-lg bg-slate-50 p-4 text-slate-600">No simulated action is available for this profile yet.</p>}
          {!!bestMoves?.alternatives.length && <div><h3 className="font-medium">Alternatives</h3><ul className="mt-2 space-y-2">{bestMoves.alternatives.map((move) => <li key={move.reason} className="rounded-lg border p-3 text-sm">{move.reason} <span className="text-slate-500">· ₹{Math.round(move.impact_paise / 100).toLocaleString("en-IN")} impact</span></li>)}</ul></div>}
          <p className="text-xs text-slate-500">Formula evidence: {bestMoves?.evidence_formula ?? "Not available"}</p>
        </section>}
        {activeTab === "Home" && <section className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <article className="rounded-xl border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">Observed Fact · Health score</p>
              <p className="mt-2 text-4xl font-semibold text-blue-700">{score === null || score === undefined ? "—" : score.toFixed(1)}<span className="text-lg text-slate-400"> / 100</span></p>
              <p className="mt-2 text-sm text-slate-600">{health?.band ?? "Waiting for a profile"}. Evidence and metric formulas are returned by the health API.</p>
            </article>
            <article className="rounded-xl border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">Prediction · Confidence</p>
              <p className="mt-2 text-4xl font-semibold text-amber-700">{confidence ? `${confidence.score}%` : "—"}</p>
              <p className="mt-2 text-sm text-slate-600">{confidence?.level ?? "Waiting for data"} confidence based on {confidence?.months_of_data ?? 0} months of transactions.</p>
            </article>
            <article className="rounded-xl border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">Recommendation</p>
              <p className="mt-2 text-lg font-semibold text-emerald-700">Build from verified data</p>
              <p className="mt-2 text-sm text-slate-600">Future actions will show before/after impact and their calculation evidence.</p>
            </article>
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <article className="rounded-xl border bg-white p-5">
              <h2 className="text-lg font-semibold">What the score means</h2>
              <p className="mt-2 text-slate-600">{health?.summary ?? "Load a demo profile to calculate the score."}</p>
              <div className="mt-4 space-y-3">
                {health && Object.entries(health.metrics).slice(0, 4).map(([key, metric]) => <div key={key} className="rounded-lg bg-slate-50 p-3"><div className="flex justify-between gap-4 text-sm font-medium"><span>{metric.plain_label || key}</span><span>{metric.status}</span></div><p className="mt-1 text-sm text-slate-600">{metric.reason}</p></div>)}
              </div>
            </article>
            <article className="rounded-xl border bg-white p-5">
              <h2 className="text-lg font-semibold">How to improve confidence</h2>
              <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-600">
                {(confidence?.how_to_improve.length ? confidence.how_to_improve : ["Add a demo profile or upload supported statement data."]).map((item) => <li key={item}>{item}</li>)}
              </ul>
              <p className="mt-5 text-xs text-slate-500">Guidance, not regulated financial advice. Numbers are shown only with backend evidence or formulas.</p>
            </article>
          </div>
        </section>}
        <footer className="text-xs text-slate-500">Your data stays private. Raw statements are not sent to the language model.</footer>
      </div>
    </main>
  );
}
