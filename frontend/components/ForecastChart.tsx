"use client";

import React, { useState } from "react";
import {
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { formatDate, Forecast } from "@/lib/api";
import { Table, Eye } from "lucide-react";

interface ForecastChartProps {
  forecast: Forecast | null;
  height?: number;
}

export function ForecastChart({ forecast, height = 320 }: ForecastChartProps) {
  const [showTable, setShowTable] = useState(false);

  if (!forecast || !forecast.dates.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed text-sm text-slate-400">
        No forecast data available. Load a demo persona to view projection.
      </div>
    );
  }

  const chartData = forecast.dates.map((d, i) => ({
    date: d,
    displayDate: formatDate(d),
    p10: Math.round(forecast.p10_paise[i] / 100),
    p50: Math.round(forecast.p50_paise[i] / 100),
    p90: Math.round(forecast.p90_paise[i] / 100),
    probBelowZero: Math.round((forecast.probability_below_zero[i] || 0) * 100),
  }));

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 text-xs text-slate-600">
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-blue-600" /> Likely (P50)
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-blue-200" /> 10th–90th Range
          </span>
        </div>
        <button
          type="button"
          onClick={() => setShowTable((v) => !v)}
          className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
        >
          {showTable ? <Eye className="h-3.5 w-3.5" /> : <Table className="h-3.5 w-3.5" />}
          {showTable ? "Visual Chart" : "View as Table"}
        </button>
      </div>

      {!showTable ? (
        <div style={{ width: "100%", height }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
              <defs>
                <linearGradient id="bandGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis
                dataKey="displayDate"
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                interval={Math.floor(chartData.length / 6)}
              />
              <YAxis
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                tickFormatter={(val) => `₹${Math.round(val / 1000)}k`}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const d = payload[0].payload;
                    return (
                      <div className="rounded-xl border border-slate-200 bg-white/95 p-3 shadow-lg backdrop-blur-sm text-xs space-y-1">
                        <p className="font-bold text-slate-900">{formatDate(d.date)}</p>
                        <p className="text-blue-700 font-semibold">
                          Likely: ₹{d.p50.toLocaleString("en-IN")}
                        </p>
                        <p className="text-slate-600">
                          Range: ₹{d.p10.toLocaleString("en-IN")} – ₹{d.p90.toLocaleString("en-IN")}
                        </p>
                        {d.probBelowZero > 0 && (
                          <p className="text-red-600 font-bold">
                            Deficit probability: {d.probBelowZero}%
                          </p>
                        )}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area
                type="monotone"
                dataKey="p90"
                stroke="#93c5fd"
                strokeWidth={1}
                fill="url(#bandGradient)"
              />
              <Area
                type="monotone"
                dataKey="p10"
                stroke="#93c5fd"
                strokeWidth={1}
                fill="#ffffff"
              />
              <Line
                type="monotone"
                dataKey="p50"
                stroke="#2563eb"
                strokeWidth={2.5}
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="max-h-72 overflow-y-auto rounded-xl border border-slate-200">
          <table className="min-w-full text-left text-xs">
            <caption className="sr-only">Accessible Cash-flow Projection Table</caption>
            <thead className="sticky top-0 bg-slate-50 border-b text-slate-500 uppercase tracking-wider">
              <tr>
                <th className="p-2.5">Date</th>
                <th className="p-2.5">Worst Case (P10)</th>
                <th className="p-2.5">Likely (P50)</th>
                <th className="p-2.5">Best Case (P90)</th>
                <th className="p-2.5">Risk &lt; ₹0</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {chartData.map((row) => (
                <tr key={row.date} className="hover:bg-slate-50/80">
                  <td className="p-2.5 font-medium">{formatDate(row.date)}</td>
                  <td className="p-2.5 text-slate-600 font-mono">₹{row.p10.toLocaleString("en-IN")}</td>
                  <td className="p-2.5 font-bold text-blue-700 font-mono">₹{row.p50.toLocaleString("en-IN")}</td>
                  <td className="p-2.5 text-slate-600 font-mono">₹{row.p90.toLocaleString("en-IN")}</td>
                  <td className={`p-2.5 font-semibold ${row.probBelowZero > 0 ? "text-red-600" : "text-emerald-600"}`}>
                    {row.probBelowZero}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
