import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface InsightsSummaryChartProps {
  data: Array<{ label: string; value: number }>;
}

export default function InsightsSummaryChart({ data }: InsightsSummaryChartProps) {
  const upperBound = Math.max(...data.map((item) => item.value), 100);

  return (
    <div className="chart-shell">
      <ResponsiveContainer width="100%" height={206}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: -4 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
          <XAxis dataKey="label" stroke="#7d8fb1" tickLine={false} axisLine={false} />
          <YAxis stroke="#7d8fb1" tickLine={false} axisLine={false} domain={[0, upperBound]} />
          <Tooltip
            contentStyle={{
              background: "rgba(8, 14, 28, 0.94)",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 16,
            }}
          />
          <Bar
            dataKey="value"
            radius={[10, 10, 0, 0]}
            fill="url(#insightFill)"
            isAnimationActive
            animationDuration={680}
            animationEasing="ease-out"
          />
          <defs>
            <linearGradient id="insightFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3ae2b0" />
              <stop offset="100%" stopColor="#4f6fff" />
            </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
