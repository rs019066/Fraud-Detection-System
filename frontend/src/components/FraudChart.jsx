/**
 * FraudChart.jsx
 * ==============
 * Recharts-based chart components for the Visualization page.
 * Matches your existing dark blue (slate-900 / blue-950) theme.
 *
 * Place in: frontend/src/components/FraudChart.jsx
 */

import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

// Shared tooltip style — matches dark theme
const tooltipStyle = {
  backgroundColor: '#0f172a',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '8px',
  color: '#fff',
  fontSize: '13px',
};

// ── Fraud vs Legitimate Donut Pie ─────────────────────────────────────────────
export const FraudPieChart = ({ data }) => (
  <ResponsiveContainer width="100%" height={220}>
    <PieChart>
      <Pie
        data={data}
        cx="50%"
        cy="50%"
        innerRadius={60}
        outerRadius={90}
        paddingAngle={3}
        dataKey="value"
        label={({ name, percent }) =>
          percent > 0 ? `${name} ${(percent * 100).toFixed(0)}%` : ''
        }
        labelLine={false}
      >
        {data.map((entry, i) => (
          <Cell key={i} fill={entry.color} />
        ))}
      </Pie>
      <Tooltip contentStyle={tooltipStyle} />
    </PieChart>
  </ResponsiveContainer>
);

// ── Risk Level Bar Chart ──────────────────────────────────────────────────────
export const RiskBarChart = ({ data }) => (
  <ResponsiveContainer width="100%" height={220}>
    <BarChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
      <XAxis
        dataKey="name"
        tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
      />
      <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
      <Tooltip contentStyle={tooltipStyle} />
      <Bar dataKey="count" radius={[4, 4, 0, 0]}>
        {data.map((entry, i) => (
          <Cell key={i} fill={entry.color} />
        ))}
      </Bar>
    </BarChart>
  </ResponsiveContainer>
);

// ── Transaction Volume Over Time Line Chart ───────────────────────────────────
export const VolumeLineChart = ({ data }) => (
  <ResponsiveContainer width="100%" height={220}>
    <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
      <XAxis
        dataKey="date"
        tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
      />
      <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
      <Tooltip contentStyle={tooltipStyle} />
      <Legend wrapperStyle={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }} />
      <Line
        type="monotone" dataKey="total" stroke="#60a5fa"
        strokeWidth={2} dot={false} name="Total"
      />
      <Line
        type="monotone" dataKey="fraud" stroke="#f87171"
        strokeWidth={2} dot={false} name="Fraud"
      />
      <Line
        type="monotone" dataKey="legit" stroke="#4ade80"
        strokeWidth={2} dot={false} name="Legit"
      />
    </LineChart>
  </ResponsiveContainer>
);

// ── Amount Distribution Bar Chart ─────────────────────────────────────────────
export const AmountBarChart = ({ data }) => (
  <ResponsiveContainer width="100%" height={220}>
    <BarChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
      <XAxis
        dataKey="range"
        tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
      />
      <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
      <Tooltip contentStyle={tooltipStyle} />
      <Bar dataKey="count" fill="#818cf8" radius={[4, 4, 0, 0]} />
    </BarChart>
  </ResponsiveContainer>
);

// ── Hourly Fraud Pattern Bar Chart ────────────────────────────────────────────
export const HourlyChart = ({ data }) => (
  <ResponsiveContainer width="100%" height={220}>
    <BarChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
      <XAxis
        dataKey="hour"
        tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }}
        tickFormatter={h => `${h}h`}
      />
      <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
      <Tooltip
        contentStyle={tooltipStyle}
        labelFormatter={h => `Hour: ${h}:00`}
      />
      <Legend wrapperStyle={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }} />
      <Bar dataKey="total" fill="#60a5fa" radius={[2, 2, 0, 0]} name="Total" />
      <Bar dataKey="fraud" fill="#f87171" radius={[2, 2, 0, 0]} name="Fraud" />
    </BarChart>
  </ResponsiveContainer>
);