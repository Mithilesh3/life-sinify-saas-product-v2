interface AdminStatsCardProps {
  label: string;
  value: number;
}

export default function AdminStatsCard({ label, value }: AdminStatsCardProps) {
  return (
    <div className="stat-card">
      <p className="stat-label">{label}</p>
      <p className="stat-value">{value}</p>
    </div>
  );
}