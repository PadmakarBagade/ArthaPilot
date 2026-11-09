"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Shield, ArrowRight, AlertCircle, CheckCircle2 } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [personaType, setPersonaType] = useState("Salaried Professional");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }
    setLoading(true);
    try {
      await register(name, email, password);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 text-slate-100">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link href="/" className="inline-flex items-center gap-2 mb-4">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Shield className="h-6 w-6 text-white" />
          </div>
          <span className="text-2xl font-black tracking-tight text-white">
            Artha<span className="text-blue-400">Pilot</span>
          </span>
        </Link>
        <h2 className="text-2xl font-bold tracking-tight text-white">
          Create your free account
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-blue-400 hover:text-blue-300">
            Sign in here
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-slate-800/90 border border-slate-700/80 py-8 px-6 shadow-xl rounded-2xl sm:px-10 backdrop-blur-xl">
          {error && (
            <div className="mb-5 flex items-center gap-2.5 rounded-xl border border-red-500/30 bg-red-950/40 p-3 text-xs text-red-300">
              <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-medium text-slate-300">Full Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Rohan Sharma"
                className="mt-1.5 block w-full rounded-xl border border-slate-700 bg-slate-900/80 px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="rohan@example.com"
                className="mt-1.5 block w-full rounded-xl border border-slate-700 bg-slate-900/80 px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300">Password (min 6 chars)</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1.5 block w-full rounded-xl border border-slate-700 bg-slate-900/80 px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300">Income / Career Profile</label>
              <select
                value={personaType}
                onChange={(e) => setPersonaType(e.target.value)}
                className="mt-1.5 block w-full rounded-xl border border-slate-700 bg-slate-900/80 px-3.5 py-2.5 text-sm text-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="Salaried Professional">Salaried Professional</option>
                <option value="Freelancer / Consultant">Freelancer / Variable Income</option>
                <option value="Small Business Owner">Small Business / MSME</option>
                <option value="Student / Early Career">Early Career / First Job</option>
                <option value="Retiree / Senior">Retiree / Pensioner</option>
              </select>
            </div>

            <div className="rounded-xl bg-blue-950/40 border border-blue-800/40 p-3 space-y-1.5 text-xs text-blue-200">
              <div className="flex items-center gap-1.5 font-medium text-blue-100">
                <CheckCircle2 className="h-3.5 w-3.5 text-blue-400 shrink-0" />
                Deterministic, Local-First Privacy
              </div>
              <p className="text-[11px] text-blue-300/80">
                All math is executed locally in integer paise. No bank credentials stored, no LLM math.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/30 transition-all disabled:opacity-50"
            >
              {loading ? "Creating account..." : "Create Account & Get Started"}
              <ArrowRight className="h-4 w-4" />
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-700/60 text-center">
            <Link href="/" className="text-xs text-slate-400 hover:text-white transition-colors">
              ← Return to Landing Page
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
