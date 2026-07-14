import { Link } from "react-router-dom";

export default function NavBar() {
  return (
    <header className="border-b border-line bg-base-800/80 backdrop-blur sticky top-0 z-20">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group">
          <span className="w-2.5 h-2.5 rounded-full bg-mint shadow-[0_0_12px_2px_rgba(61,220,151,0.6)]" />
          <span className="font-display font-semibold text-lg tracking-tight text-ink-100">
            parity
          </span>
          <span className="hidden sm:inline text-ink-500 text-xs font-mono uppercase tracking-widest ml-1">
            k8s drift console
          </span>
        </Link>
        <div className="flex items-center gap-6 text-sm font-mono text-ink-500">
          <span className="hidden md:inline">prod → dr</span>
          <span className="w-px h-4 bg-line hidden md:inline" />
          <span className="text-ink-300">env: production cluster</span>
        </div>
      </div>
    </header>
  );
}
