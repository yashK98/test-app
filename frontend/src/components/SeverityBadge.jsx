const STYLES = {
  critical: "bg-red/15 text-red border-red/30",
  high: "bg-amber/15 text-amber border-amber/30",
  medium: "bg-blue/15 text-blue border-blue/30",
  low: "bg-ink-500/15 text-ink-300 border-ink-500/30",
};

export default function SeverityBadge({ severity }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full border text-[11px] font-mono uppercase tracking-wider ${STYLES[severity] || STYLES.low}`}
    >
      {severity}
    </span>
  );
}
