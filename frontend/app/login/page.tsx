"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Shield, ArrowRight, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login, demoLogin } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to sign in");
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = async (personaId: string) => {
    setError(null);
    setLoading(true);
    try {
      await demoLogin(personaId);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed demo login");
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
          Sign in to your financial copilot
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          Or{" "}
          <Link href="/register" className="font-medium text-blue-400 hover:text-blue-300">
            create a new account for free
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
              <label className="block text-xs font-medium text-slate-300">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="mt-1.5 block w-full rounded-xl border border-slate-700 bg-slate-900/80 px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1.5 block w-full rounded-xl border border-slate-700 bg-slate-900/80 px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/30 transition-all disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Sign In"}
              <ArrowRight className="h-4 w-4" />
            </button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-700" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-slate-800 px-3 text-slate-400">Or instant 1-click demo</span>
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-xs text-slate-400 mb-2">Explore fully loaded synthetic personas:</p>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleDemo("rahul")}
                className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/60 p-2 text-left hover:border-blue-500/50 hover:bg-slate-900 transition-all"
              >
                <div className="h-7 w-7 rounded-full bg-blue-900/60 flex items-center justify-center text-blue-300 text-xs font-bold">
                  R
                </div>
                <div>
                  <div className="text-xs font-medium text-white">Rahul</div>
                  <div className="text-[10px] text-slate-400">Young Pro</div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => handleDemo("priya")}
                className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/60 p-2 text-left hover:border-blue-500/50 hover:bg-slate-900 transition-all"
              >
                <div className="h-7 w-7 rounded-full bg-purple-900/60 flex items-center justify-center text-purple-300 text-xs font-bold">
                  P
                </div>
                <div>
                  <div className="text-xs font-medium text-white">Priya</div>
                  <div className="text-[10px] text-slate-400">Salaried + EMI</div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => handleDemo("amit")}
                className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/60 p-2 text-left hover:border-blue-500/50 hover:bg-slate-900 transition-all"
              >
                <div className="h-7 w-7 rounded-full bg-emerald-900/60 flex items-center justify-center text-emerald-300 text-xs font-bold">
                  A
                </div>
                <div>
                  <div className="text-xs font-medium text-white">Amit</div>
                  <div className="text-[10px] text-slate-400">Freelancer</div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => handleDemo("sneha")}
                className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/60 p-2 text-left hover:border-blue-500/50 hover:bg-slate-900 transition-all"
              >
                <div className="h-7 w-7 rounded-full bg-amber-900/60 flex items-center justify-center text-amber-300 text-xs font-bold">
                  S
                </div>
                <div>
                  <div className="text-xs font-medium text-white">Sneha</div>
                  <div className="text-[10px] text-slate-400">High Earner</div>
                </div>
              </button>
            </div>
          </div>

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
