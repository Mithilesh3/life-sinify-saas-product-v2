import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface RadarDataItem {
  metric: string;
  score: number;
}

interface Props {
  data: RadarDataItem[];
}

export default function RadarChartComponent({ data }: Props) {
  return (
    <div className="chart-shell p-4">
      <ResponsiveContainer width="100%" height={380}>
        <RadarChart data={data}>
          <PolarGrid stroke="rgba(148, 163, 184, 0.2)" />
          <PolarAngleAxis dataKey="metric" stroke="#cbd5e1" tick={{ fontSize: 12 }} />
          <PolarRadiusAxis stroke="rgba(148, 163, 184, 0.4)" domain={[0, 100]} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Radar name="Score" dataKey="score" stroke="#818cf8" fill="#818cf8" fillOpacity={0.5} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}