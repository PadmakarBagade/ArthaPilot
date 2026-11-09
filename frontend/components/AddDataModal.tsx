"use client";

import React, { useState } from "react";
import { X, PlusCircle, Upload } from "lucide-react";
import { addManualLoan, addManualTransaction, addIncomeChange, uploadStatement } from "@/lib/api";

interface AddDataModalProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
  onSuccess: () => void;
}

export function AddDataModal({ isOpen, onClose, userId, onSuccess }: AddDataModalProps) {
  const [tab, setTab] = useState<"emi" | "transaction" | "income" | "upload">("emi");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  // EMI form
  const [emiOutstanding, setEmiOutstanding] = useState("120000");
  const [emiAmount, setEmiAmount] = useState("12000");
  const [emiType, setEmiType] = useState("Personal Loan");

  // Transaction form
  const [txDate, setTxDate] = useState(new Date().toISOString().split("T")[0]);
  const [txAmount, setTxAmount] = useState("2500");
  const [txCategory, setTxCategory] = useState("Dining");
  const [txMerchant, setTxMerchant] = useState("Dinner Outing");

  // Income form
  const [incomeAmount, setIncomeAmount] = useState("15000");
  const [incomeDate, setIncomeDate] = useState(new Date().toISOString().split("T")[0]);
  const [incomeDesc, setIncomeDesc] = useState("Freelance Gig");

  // File upload form
  const [file, setFile] = useState<File | null>(null);

  if (!isOpen) return null;

  async function handleEmiSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const outPaise = (Number(emiOutstanding) || 0) * 100;
      const emiPaise = (Number(emiAmount) || 0) * 100;
      await addManualLoan(userId, outPaise, emiPaise, emiType);
      setMessage("Loan scenario successfully recorded and snapshot saved!");
      onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to record loan scenario");
    } finally {
      setLoading(false);
    }
  }

  async function handleTxSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const amtPaise = -(Math.abs(Number(txAmount) || 0) * 100);
      await addManualTransaction(userId, txDate, amtPaise, txCategory, txMerchant);
      setMessage("Transaction added and analysis recalculated!");
      onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to add transaction");
    } finally {
      setLoading(false);
    }
  }

  async function handleIncomeSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const amtPaise = Math.abs(Number(incomeAmount) || 0) * 100;
      await addIncomeChange(userId, amtPaise, incomeDate, incomeDesc);
      setMessage("Income change added and snapshot saved!");
      onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to add income change");
    } finally {
      setLoading(false);
    }
  }

  async function handleUploadSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await uploadStatement(file);
      setMessage(`Successfully loaded ${res.transactions_loaded ?? 0} transactions!`);
      onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to upload file");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg bg-white rounded-2xl shadow-2xl p-6 space-y-5 animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b pb-4">
          <div className="flex items-center gap-2">
            <PlusCircle className="h-6 w-6 text-blue-600" />
            <h2 className="text-xl font-bold text-slate-900">Add Data or Test Scenario</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab selector */}
        <div className="grid grid-cols-4 gap-1 rounded-xl bg-slate-100 p-1 text-xs font-semibold">
          <button
            type="button"
            onClick={() => setTab("emi")}
            className={`py-2 rounded-lg transition-all ${
              tab === "emi" ? "bg-white text-blue-700 shadow-2xs font-bold" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Add EMI
          </button>
          <button
            type="button"
            onClick={() => setTab("transaction")}
            className={`py-2 rounded-lg transition-all ${
              tab === "transaction" ? "bg-white text-blue-700 shadow-2xs font-bold" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Add Expense
          </button>
          <button
            type="button"
            onClick={() => setTab("income")}
            className={`py-2 rounded-lg transition-all ${
              tab === "income" ? "bg-white text-blue-700 shadow-2xs font-bold" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Add Income
          </button>
          <button
            type="button"
            onClick={() => setTab("upload")}
            className={`py-2 rounded-lg transition-all ${
              tab === "upload" ? "bg-white text-blue-700 shadow-2xs font-bold" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Upload File
          </button>
        </div>

        {error && <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-800 font-medium">{error}</div>}
        {message && <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800 font-medium">{message}</div>}

        {/* EMI form */}
        {tab === "emi" && (
          <form onSubmit={handleEmiSubmit} className="space-y-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                Loan Type
              </label>
              <input
                type="text"
                value={emiType}
                onChange={(e) => setEmiType(e.target.value)}
                className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                  Principal (₹)
                </label>
                <input
                  type="number"
                  min="1000"
                  value={emiOutstanding}
                  onChange={(e) => setEmiOutstanding(e.target.value)}
                  className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                  Monthly EMI (₹)
                </label>
                <input
                  type="number"
                  min="100"
                  value={emiAmount}
                  onChange={(e) => setEmiAmount(e.target.value)}
                  className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-blue-700 py-3 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-50 transition-colors"
            >
              {loading ? "Recording..." : "Apply EMI Scenario"}
            </button>
          </form>
        )}

        {/* Transaction form */}
        {tab === "transaction" && (
          <form onSubmit={handleTxSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                  Date
                </label>
                <input
                  type="date"
                  value={txDate}
                  onChange={(e) => setTxDate(e.target.value)}
                  className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                  Amount (₹)
                </label>
                <input
                  type="number"
                  min="1"
                  value={txAmount}
                  onChange={(e) => setTxAmount(e.target.value)}
                  className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                  Category
                </label>
                <select
                  value={txCategory}
                  onChange={(e) => setTxCategory(e.target.value)}
                  className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
                >
                  <option value="Dining">Dining</option>
                  <option value="Food Delivery">Food Delivery</option>
                  <option value="Shopping">Shopping</option>
                  <option value="Groceries">Groceries</option>
                  <option value="Transport">Transport</option>
                  <option value="Entertainment">Entertainment</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                  Merchant / Note
                </label>
                <input
                  type="text"
                  value={txMerchant}
                  onChange={(e) => setTxMerchant(e.target.value)}
                  className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-blue-700 py-3 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-50 transition-colors"
            >
              {loading ? "Adding..." : "Add Expense"}
            </button>
          </form>
        )}

        {/* Income form */}
        {tab === "income" && (
          <form onSubmit={handleIncomeSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                  Amount (₹)
                </label>
                <input
                  type="number"
                  min="1"
                  value={incomeAmount}
                  onChange={(e) => setIncomeAmount(e.target.value)}
                  className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                  Date
                </label>
                <input
                  type="date"
                  value={incomeDate}
                  onChange={(e) => setIncomeDate(e.target.value)}
                  className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
                />
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
                Description / Source
              </label>
              <input
                type="text"
                value={incomeDesc}
                onChange={(e) => setIncomeDesc(e.target.value)}
                className="mt-1 block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold focus:border-blue-600 focus:outline-hidden"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-blue-700 py-3 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-50 transition-colors"
            >
              {loading ? "Adding..." : "Add Income"}
            </button>
          </form>
        )}

        {/* Upload form */}
        {tab === "upload" && (
          <form onSubmit={handleUploadSubmit} className="space-y-4">
            <div className="border-2 border-dashed border-slate-200 rounded-xl p-6 text-center hover:border-blue-400 transition-colors">
              <Upload className="h-8 w-8 mx-auto text-slate-400" />
              <p className="mt-2 text-xs font-medium text-slate-600">
                Upload CSV, XLSX, or PDF bank statement
              </p>
              <input
                type="file"
                accept=".csv,.xlsx,.pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="mt-3 block w-full text-xs text-slate-500 file:mr-3 file:rounded-lg file:border-0 file:bg-blue-50 file:px-3 file:py-1.5 file:text-xs file:font-semibold file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !file}
              className="w-full rounded-xl bg-blue-700 py-3 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-50 transition-colors"
            >
              {loading ? "Processing Statement..." : "Upload & Ingest"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
