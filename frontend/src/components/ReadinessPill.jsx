const CONFIG = {
  green: { color: "bg-mint", text: "text-mint", label: "ready" },
  yellow: { color: "bg-amber", text: "text-amber", label: "at risk" },
  red: { color: "bg-red", text: "text-red", label: "not ready" },
};

export default function ReadinessPill({ readiness }) {
  const c = CONFIG[readiness] || CONFIG.red;
  return (
    <span className={`inline-flex items-center gap-1.5 font-mono text-xs uppercase tracking-wider ${c.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.color}`} />
      {c.label}
    </span>
  );
}
