"use client";

import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface SpendingData {
  category: string;
  amount_paise: number;
  color: string;
}

const COLORS = ["#2563eb", "#059669", "#d97706", "#7c3aed", "#f97316", "#10b981"];

export function SpendingPieChart({ data }: { data: SpendingData[] }) {
  const total = data.reduce((sum, d) => sum + d.amount_paise, 0);
  const chartData = data.map((d) => ({ name: d.category, value: d.amount_paise }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={70}
          outerRadius={100}
          paddingAngle={2}
          dataKey="value"
          nameKey="name"
        >
          {chartData.map((_, i) => (
            <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number) => `${Math.round((value / total) * 100)}%`}
          contentStyle={{ backgroundColor: "#1e293b", border: "none" }}
          cursor={{ fill: "rgba(255,255,255,0.1)" }}
        />
        <Legend verticalAlign="bottom" height={36} iconSize={12} />
      </PieChart>
    </ResponsiveContainer>
  );
}

export default SpendingPieChart;

