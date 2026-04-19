
/**
 * VisualizationPage.jsx
 * =====================
 * Full analytics dashboard: summary cards + 5 charts + real-time log.
 *
 * Place in: frontend/src/components/VisualizationPage.jsx
 * (create the pages/ folder if it doesn't exist yet)
 */

import { useState, useEffect } from 'react';
import {
  BarChart2, AlertCircle, CheckCircle, TrendingUp, Database, RefreshCw
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import {
  FraudPieChart,
  RiskBarChart,
  VolumeLineChart,
  AmountBarChart,
  HourlyChart,
} from '../components/FraudChart';

const API_URL = 'http://localhost:8000';

// ── Reusable chart card wrapper ───────────────────────────────────────────────
const ChartCard = ({ title, children }) => (
  <div className="bg-white/5 border border-white/10 rounded-xl p-5">
    <h3 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-4">
      {title}
    </h3>
    {children}
  </div>
);

// ── Summary stat card ─────────────────────────────────────────────────────────
const StatCard = ({ icon: Icon, label, value, colorClass }) => (
  <div className={`bg-white/5 border border-white/10 rounded-xl p-5 transition-colors hover:border-white/20`}>
    <Icon className={`w-6 h-6 mb-2 ${colorClass}`} />
    <p className="text-3xl font-bold text-white">{value}</p>
    <p className="text-sm text-white/50 mt-1">{label}</p>
  </div>
);

// ── Main page ─────────────────────────────────────────────────────────────────
export default function VisualizationPage() {
  const { token } = useAuth();
  const [data, setData]             = useState(null);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/viz/charts`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const json = await res.json();
      setData(json);
      setLastRefresh(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [token]);

  // ── Loading state ────────────────────────────────────────────────────────
  if (loading) return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900
                    flex items-center justify-center">
      <div className="text-center">
        <div className="w-10 h-10 border-2 border-blue-400 border-t-transparent rounded-full
                        animate-spin mx-auto mb-3" />
        <p className="text-white/50 text-sm">Loading chart data…</p>
      </div>
    </div>
  );

  // ── Error state ──────────────────────────────────────────────────────────
  if (error) return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900
                    flex items-center justify-center">
      <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-8 text-center max-w-md">
        <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
        <p className="text-white font-semibold mb-1">Failed to load data</p>
        <p className="text-white/50 text-sm mb-4">{error}</p>
        <button
          onClick={fetchData}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Retry
        </button>
      </div>
    </div>
  );

  const s = data.summary;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900">
      <div className="max-w-7xl mx-auto p-6 space-y-6">

        {/* ── Page header ───────────────────────────────────────────────── */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 border-t-4 border-blue-500
                        flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BarChart2 className="w-10 h-10 text-blue-400" />
            <div>
              <h1 className="text-2xl font-bold text-white">Visualization</h1>
              <p className="text-sm text-blue-300">Charts · Analytics · Live Feed</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {lastRefresh && (
              <span className="text-xs text-white/30">Updated {lastRefresh}</span>
            )}
            <button
              onClick={fetchData}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500
                         text-white rounded-lg text-sm font-medium transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* ── Summary stat cards ────────────────────────────────────────── */}
        <div className="grid grid-cols-4 gap-4">
          <StatCard
            icon={Database}
            label="Total Transactions"
            value={s.total}
            colorClass="text-blue-400"
          />
          <StatCard
            icon={AlertCircle}
            label="Fraud Detected"
            value={s.fraud}
            colorClass="text-red-400"
          />
          <StatCard
            icon={CheckCircle}
            label="Legitimate"
            value={s.legit}
            colorClass="text-green-400"
          />
          <StatCard
            icon={TrendingUp}
            label="Fraud Rate"
            value={`${s.fraud_rate}%`}
            colorClass="text-purple-400"
          />
        </div>

        {/* ── Charts row 1: Pie · Risk bars · Amount bars ───────────────── */}
        <div className="grid grid-cols-3 gap-4">
          <ChartCard title="Fraud vs Legitimate">
            <FraudPieChart data={data.fraud_vs_legit} />
          </ChartCard>

          <ChartCard title="Risk Level Distribution">
            <RiskBarChart data={data.risk_distribution} />
          </ChartCard>

          <ChartCard title="Amount Distribution">
            <AmountBarChart data={data.amount_distribution} />
          </ChartCard>
        </div>

        {/* ── Charts row 2: Volume over time · Hourly pattern ───────────── */}
        <div className="grid grid-cols-2 gap-4">
          <ChartCard title="Transaction Volume — Last 14 Days">
            {data.volume_over_time.length > 0 ? (
              <VolumeLineChart data={data.volume_over_time} />
            ) : (
              <div className="flex items-center justify-center h-[220px] text-white/30 text-sm text-center px-4">
                Not enough data yet.<br />
                Run a few predictions to populate this chart.
              </div>
            )}
          </ChartCard>

          <ChartCard title="Fraud by Hour of Day">
            <HourlyChart data={data.hourly_pattern} />
          </ChartCard>
        </div>

      </div>
    </div>
  );
}