const colorFor = (score) => {
  if (score >= 90) return "#3DDC97";
  if (score >= 70) return "#F5A623";
  return "#FF5C5C";
};

export default function ParityGauge({ score, size = 88 }) {
  const radius = (size - 10) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - score / 100);
  const color = colorFor(score);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} stroke="#26314A" strokeWidth="6" fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth="6"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-mono font-semibold text-lg text-ink-100">{score}</span>
        <span className="text-[10px] text-ink-500 uppercase tracking-wider">parity</span>
      </div>
    </div>
  );
}
