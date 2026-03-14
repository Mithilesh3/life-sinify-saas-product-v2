import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface UsageOverviewChartProps {
  used: number;
  remaining: number;
  limit: number;
}

export default function UsageOverviewChart({
  used,
  remaining,
  limit,
}: UsageOverviewChartProps) {
  const data = [
    { label: "Used", value: used },
    { label: "Remaining", value: remaining },
    { label: "Limit", value: limit },
  ];

  return (
    <div className="chart-shell">
      <ResponsiveContainer width="100%" height={206}>
        <AreaChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: -4 }}>
          <defs>
            <linearGradient id="usageFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6aa8ff" stopOpacity={0.6} />
              <stop offset="95%" stopColor="#6aa8ff" stopOpacity={0.03} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
          <XAxis dataKey="label" stroke="#7d8fb1" tickLine={false} axisLine={false} />
          <YAxis stroke="#7d8fb1" tickLine={false} axisLine={false} />
          <Tooltip
            contentStyle={{
              background: "rgba(8, 14, 28, 0.94)",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 16,
            }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#6aa8ff"
            strokeWidth={2.5}
            fill="url(#usageFill)"
            isAnimationActive
            animationDuration={760}
            animationEasing="ease-out"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
