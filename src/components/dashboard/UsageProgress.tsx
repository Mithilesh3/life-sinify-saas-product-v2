import { useUsage } from "../../context/UsageContext";

export default function UsageProgress() {
  const { usage } = useUsage();
  if (!usage) return null;

  const percent = usage.reports_limit > 0 ? (usage.reports_used / usage.reports_limit) * 100 : 0;

  return (
    <div className="chart-shell p-5">
      <p className="type-body mb-3">
        Usage: {usage.reports_used} / {usage.reports_limit}
      </p>
      <div className="h-3 w-full overflow-hidden rounded-full bg-slate-950/80">
        <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}