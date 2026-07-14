import SeverityBadge from "./SeverityBadge";

const CATEGORY_LABEL = {
  image: "image",
  replicas: "replicas",
  resources: "resources",
  env_vars: "env",
  config: "configmap",
  secret: "secret",
};

function DiffLine({ item }) {
  const removedOnly = item.target_value === "missing";
  const addedOnly = item.baseline_value === "missing";

  return (
    <div className="group grid grid-cols-[auto_1fr] gap-3 py-2.5 px-4 border-b border-line/60 last:border-b-0 hover:bg-base-700/40 transition-colors">
      <div className="pt-0.5">
        <SeverityBadge severity={item.severity} />
      </div>
      <div className="min-w-0">
        <div className="flex items-baseline gap-2 flex-wrap">
          <span className="font-mono text-xs text-ink-500 uppercase tracking-wider">
            {CATEGORY_LABEL[item.category] || item.category}
          </span>
          <span className="font-mono text-sm text-ink-100">{item.field}</span>
        </div>
        <div className="mt-1.5 font-mono text-[13px] leading-relaxed">
          {!addedOnly && (
            <div className="text-red/90">
              <span className="select-none mr-2 text-red/60">−</span>
              {item.baseline_value ?? "∅"}
            </div>
          )}
          {!removedOnly && (
            <div className="text-mint/90">
              <span className="select-none mr-2 text-mint/60">+</span>
              {item.target_value ?? "∅"}
            </div>
          )}
        </div>
        <p className="mt-1 text-xs text-ink-500">{item.description}</p>
      </div>
    </div>
  );
}

export default function DriftDiffView({ items, baselineEnv, targetEnv }) {
  if (!items || items.length === 0) {
    return (
      <div className="rounded-lg border border-line bg-base-800 px-6 py-10 text-center">
        <p className="font-mono text-mint text-sm">✓ no drift detected</p>
        <p className="text-ink-500 text-sm mt-1">
          {baselineEnv} and {targetEnv} are in full parity.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-line bg-base-800 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2.5 bg-base-700/60 border-b border-line font-mono text-xs text-ink-500">
        <span>
          <span className="text-red">− {baselineEnv}</span>
          <span className="mx-2">/</span>
          <span className="text-mint">+ {targetEnv}</span>
        </span>
        <span>{items.length} drift item{items.length !== 1 ? "s" : ""}</span>
      </div>
      <div>
        {items.map((item, idx) => (
          <DiffLine key={idx} item={item} />
        ))}
      </div>
    </div>
  );
}
