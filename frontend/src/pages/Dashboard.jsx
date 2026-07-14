import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { api } from "../api";
import ReadinessPill from "../components/ReadinessPill";
import ParityGauge from "../components/ParityGauge";

const CAUSE_LABEL = {
  manual_kubectl_edit: "manual kubectl edit",
  bad_helm_deploy: "bad helm deploy",
  config_drift: "config drift",
  stale_dr_sync: "stale DR sync",
};

function StatCard({ label, value, accent }) {
  return (
    <div className="rounded-lg border border-line bg-base-800 px-5 py-4">
      <p className="text-ink-500 text-xs font-mono uppercase tracking-wider">{label}</p>
      <p className={`font-display font-semibold text-3xl mt-1.5 ${accent || "text-ink-100"}`}>{value}</p>
    </div>
  );
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [trends, setTrends] = useState({});
  const [error, setError] = useState(null);

  const load = async () => {
    try {
      const data = await api.dashboardSummary();
      setSummary(data);
      const trendEntries = await Promise.all(
        data.apps.slice(0, 3).map(async (a) => [a.app, await api.getTrend(a.app)])
      );
      setTrends(Object.fromEntries(trendEntries));
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const runScan = async () => {
    setScanning(true);
    try {
      await api.triggerScan();
      await load();
    } finally {
      setScanning(false);
    }
  };

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-16 text-center text-red font-mono text-sm">
        Failed to reach backend: {error}. Is the API running on :8000?
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-16 text-center text-ink-500 font-mono text-sm">
        loading cluster state…
      </div>
    );
  }

  const worstTrendApp = summary.apps[0];

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="flex items-start justify-between flex-wrap gap-4 mb-8">
        <div>
          <h1 className="font-display font-semibold text-3xl text-ink-100 tracking-tight">
            Environment parity
          </h1>
          <p className="text-ink-500 mt-1.5 text-sm">
            Prod → DR comparison across {summary.total_apps} applications, refreshed on demand.
          </p>
        </div>
        <button
          onClick={runScan}
          disabled={scanning}
          className="font-mono text-sm px-4 py-2.5 rounded-md bg-mint text-base-900 font-medium hover:brightness-110 active:brightness-95 disabled:opacity-50 transition"
        >
          {scanning ? "scanning…" : "run scan"}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Avg parity" value={`${summary.avg_parity_score}%`} />
        <StatCard label="Drifted apps" value={`${summary.drifted_apps}/${summary.total_apps}`} accent={summary.drifted_apps > 0 ? "text-amber" : "text-mint"} />
        <StatCard label="High severity" value={summary.high_items} accent={summary.high_items > 0 ? "text-amber" : undefined} />
        <StatCard label="Critical" value={summary.critical_items} accent={summary.critical_items > 0 ? "text-red" : undefined} />
      </div>

      {worstTrendApp && trends[worstTrendApp.app] && (
        <div className="rounded-lg border border-line bg-base-800 px-5 py-5 mb-8">
          <div className="flex items-center justify-between mb-3">
            <p className="font-mono text-xs text-ink-500 uppercase tracking-wider">
              Parity trend — {worstTrendApp.app} (lowest scoring)
            </p>
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={trends[worstTrendApp.app]}>
              <CartesianGrid stroke="#1C2942" vertical={false} />
              <XAxis dataKey="date" tick={{ fill: "#7C8AA5", fontSize: 11 }} axisLine={{ stroke: "#26314A" }} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: "#7C8AA5", fontSize: 11 }} axisLine={false} tickLine={false} width={30} />
              <Tooltip
                contentStyle={{ background: "#0F1729", border: "1px solid #26314A", borderRadius: 8, fontFamily: "JetBrains Mono", fontSize: 12 }}
                labelStyle={{ color: "#B7C1D6" }}
              />
              <Line type="monotone" dataKey="parity_score" stroke="#5B8DEF" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <p className="font-mono text-xs text-ink-500 uppercase tracking-wider mb-3">Applications</p>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {summary.apps.map((a) => (
          <Link
            key={a.app}
            to={`/app/${a.app}`}
            className="rounded-lg border border-line bg-base-800 p-5 hover:border-blue/50 hover:bg-base-700/40 transition group"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="font-display font-medium text-ink-100 group-hover:text-blue transition-colors">{a.app}</p>
                <div className="mt-2"><ReadinessPill readiness={a.readiness} /></div>
              </div>
              <ParityGauge score={a.parity_score} size={64} />
            </div>
            <div className="mt-4 pt-4 border-t border-line/60 flex items-center justify-between text-xs font-mono text-ink-500">
              <span>{a.drift_count} drift item{a.drift_count !== 1 ? "s" : ""}</span>
              {a.root_cause && <span className="text-ink-300">{CAUSE_LABEL[a.root_cause] || a.root_cause}</span>}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
