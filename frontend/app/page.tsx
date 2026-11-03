"use client";

import { type FormEvent, useEffect, useState } from "react";

import { askCopilot, ChatAnswer, Confidence, getConfidence, getHealth, Health, listUsers, User } from "@/lib/api";

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
    Promise.all([getHealth(selectedUser), getConfidence(selectedUser)])
      .then(([nextHealth, nextConfidence]) => {
        setHealth(nextHealth);
        setConfidence(nextConfidence);
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
        {activeTab !== "Home" && activeTab !== "Ask" && <section className="rounded-xl border bg-white p-6"><h2 className="text-xl font-semibold">{activeTab}</h2><p className="mt-2 text-slate-600">This workspace is connected to the typed API and will display verified {activeTab.toLowerCase()} results as those services are enabled.</p></section>}
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
