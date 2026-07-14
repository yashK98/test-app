import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api";
import DriftDiffView from "../components/DriftDiffView";
import ParityGauge from "../components/ParityGauge";
import ReadinessPill from "../components/ReadinessPill";

const CAUSE_LABEL = {
  manual_kubectl_edit: "Manual kubectl edit",
  bad_helm_deploy: "Bad Helm deploy",
  config_drift: "Config drift",
  stale_dr_sync: "Stale DR sync",
};

function readinessFor(score) {
  if (score >= 90) return "green";
  if (score >= 70) return "yellow";
  return "red";
}

export default function AppDetail() {
  const { app } = useParams();
  const [report, setReport] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [applying, setApplying] = useState(null);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const load = async () => {
    try {
      const r = await api.getReport(app);
      setReport(r);
      const s = await api.getSuggestions(app);
      setSuggestions(s);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [app]);

  const applyAction = async (action) => {
    setApplying(action);
    setMessage(null);
    try {
      const res = await api.applyRemediation(app, action);
      setMessage(res.message);
      await load();
    } finally {
      setApplying(null);
    }
  };

  if (error) {
    return <div className="max-w-4xl mx-auto px-6 py-16 text-red font-mono text-sm">{error}</div>;
  }
  if (!report) {
    return <div className="max-w-4xl mx-auto px-6 py-16 text-ink-500 font-mono text-sm">loading…</div>;
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <Link to="/" className="text-ink-500 hover:text-ink-300 text-sm font-mono inline-block mb-6">
        ← back to dashboard
      </Link>

      <div className="flex items-start justify-between flex-wrap gap-4 mb-2">
        <div>
          <h1 className="font-display font-semibold text-3xl text-ink-100 tracking-tight">{report.app}</h1>
          <div className="mt-2"><ReadinessPill readiness={readinessFor(report.parity_score)} /></div>
        </div>
        <ParityGauge score={report.parity_score} size={96} />
      </div>

      {report.summary && (
        <div className="mt-6 rounded-lg border border-line bg-base-800 px-5 py-4">
          <p className="font-mono text-xs text-ink-500 uppercase tracking-wider mb-2">Summary</p>
          <p className="text-ink-100 text-sm leading-relaxed">{report.summary}</p>
        </div>
      )}

      {report.root_cause && (
        <div className="mt-4 rounded-lg border border-blue/30 bg-blue/5 px-5 py-4 flex items-center justify-between flex-wrap gap-2">
          <div>
            <p className="font-mono text-xs text-blue uppercase tracking-wider mb-1">ML root cause prediction</p>
            <p className="text-ink-100 text-sm">{CAUSE_LABEL[report.root_cause] || report.root_cause}</p>
          </div>
          <div className="text-right">
            <p className="font-mono text-2xl text-blue font-semibold">
              {Math.round((report.root_cause_confidence || 0) * 100)}%
            </p>
            <p className="text-ink-500 text-xs">confidence</p>
          </div>
        </div>
      )}

      <div className="mt-8">
        <p className="font-mono text-xs text-ink-500 uppercase tracking-wider mb-3">
          Drift detail — {report.baseline_env} vs {report.target_env}
        </p>
        <DriftDiffView items={report.drift_items} baselineEnv={report.baseline_env} targetEnv={report.target_env} />
      </div>

      {suggestions.length > 0 && (
        <div className="mt-8">
          <p className="font-mono text-xs text-ink-500 uppercase tracking-wider mb-3">Remediation</p>
          <div className="rounded-lg border border-line bg-base-800 divide-y divide-line">
            {suggestions.map((s) => (
              <div key={s.action} className="px-5 py-4 flex items-center justify-between gap-4 flex-wrap">
                <div>
                  <p className="text-ink-100 text-sm font-medium">{s.description}</p>
                  <p className="text-ink-500 text-xs font-mono mt-1">
                    predicted success: {Math.round(s.success_likelihood * 100)}%
                  </p>
                </div>
                <button
                  onClick={() => applyAction(s.action)}
                  disabled={applying === s.action}
                  className="font-mono text-xs px-3.5 py-2 rounded-md border border-mint/40 text-mint hover:bg-mint/10 disabled:opacity-50 transition whitespace-nowrap"
                >
                  {applying === s.action ? "applying…" : "apply fix"}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {message && (
        <div className="mt-4 rounded-lg border border-mint/30 bg-mint/5 px-5 py-3 text-mint text-sm font-mono">
          {message}
        </div>
      )}
    </div>
  );
}
