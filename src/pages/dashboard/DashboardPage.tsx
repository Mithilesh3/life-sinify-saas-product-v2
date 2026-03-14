import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import InsightsSummaryChart from "../../components/charts/InsightsSummaryChart";
import UsageOverviewChart from "../../components/charts/UsageOverviewChart";
import AmbientBackground from "../../components/layout/AmbientBackground";
import AnimatedButton from "../../components/ui/AnimatedButton";
import DashboardCard from "../../components/ui/DashboardCard";
import Skeleton from "../../components/ui/Skeleton";
import StatCard from "../../components/ui/StatCard";
import { useAuth } from "../../context/AuthContext";
import { useUsage } from "../../context/UsageContext";
import API from "../../services/api";
import type { Report } from "../../types/report";

const revealTransition = { duration: 0.38, ease: [0.22, 1, 0.36, 1] as const };
const heroLineVariants = {
  hidden: { opacity: 0, y: 18 },
  visible: (index: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.42,
      delay: 0.08 + index * 0.08,
      ease: [0.22, 1, 0.36, 1] as const,
    },
  }),
};

function formatDateTime(value?: string | null) {
  if (!value) return "Not available";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { usage } = useUsage();
  const navigate = useNavigate();

  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await API.get<Report[]>("/reports/");
        setReports(response.data);
      } catch {
        toast.error("Failed to fetch reports");
      } finally {
        setLoading(false);
      }
    };

    void fetchReports();
  }, []);

  const currentPlan =
    usage?.subscription_plan ||
    user?.subscription?.plan_name ||
    user?.organization?.plan ||
    "basic";

  const heroName = user?.organization?.name ?? user?.email?.split("@")[0] ?? "Operator";
  const latestReport = reports[0];
  const latestMetrics = latestReport?.content.core_metrics;
  const latestBrief = latestReport?.content.executive_brief;
  const numerologyCore = latestReport?.content.numerology_core?.pythagorean;

  const used = usage?.reports_used ?? 0;
  const limit = usage?.reports_limit ?? 0;
  const remaining = usage?.reports_remaining ?? Math.max(limit - used, 0);
  const totalReports = usage?.total_reports ?? reports.length;
  const usagePercent = limit > 0 ? Math.min((used / limit) * 100, 100) : 0;
  const luckyNumber = ((heroName.length + used + (latestReport?.confidence_score ?? 0)) % 9) + 1;

  const widgetValues = [
    { label: "Lucky Number", value: String(luckyNumber), detail: "Numerology formula" },
    { label: "Today's Horoscope", value: "Growth day", detail: "Action + patience" },
    { label: "Compatibility Score", value: `${Math.max(72, (latestReport?.confidence_score ?? 72) - 8)}%`, detail: "Love, marriage, business" },
    { label: "Numerology Insights", value: `${(numerologyCore?.destiny_number ?? numerologyCore?.expression_number ?? luckyNumber).toString()}`, detail: "Destiny and expression" },
    { label: "Recommended Gemstone", value: luckyNumber % 2 === 0 ? "Emerald" : "Yellow Sapphire", detail: "Based on current pattern" },
  ];

  const insightData = useMemo(
    () => [
      { label: "Stability", value: latestMetrics?.life_stability_index ?? 0 },
      { label: "Dharma", value: latestMetrics?.dharma_alignment_score ?? 0 },
      { label: "Emotion", value: latestMetrics?.emotional_regulation_index ?? 0 },
      { label: "Finance", value: latestMetrics?.financial_discipline_index ?? 0 },
    ],
    [latestMetrics]
  );

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="premium-page">
      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={revealTransition}
        className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"
      >
        <StatCard label="Total Reports" value={totalReports} detail="All generated reports returned by the existing backend endpoints." floatDelay={0} />
        <StatCard label="Latest Confidence" value={latestReport?.confidence_score ?? 0} detail="Confidence score from the most recent executive brief." floatDelay={0.12} />
        <StatCard label="Life Stability" value={latestMetrics?.life_stability_index ?? 0} detail="A premium readout of the latest core metrics block." floatDelay={0.24} />
        <StatCard label="Dharma Alignment" value={latestMetrics?.dharma_alignment_score ?? 0} detail="Strategic fit surfaced directly from report content." floatDelay={0.36} />
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.05 }}
        className="grid gap-4 md:grid-cols-2 xl:grid-cols-5"
      >
        {widgetValues.map((widget, index) => (
          <WidgetCard
            key={widget.label}
            label={widget.label}
            value={widget.value}
            detail={widget.detail}
            delay={index * 0.05}
          />
        ))}
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.08 }}
        className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]"
      >
        <DashboardCard title="Report usage" description="A visual on consumed, remaining, and total report capacity for the current billing cycle." floating floatDelay={0.15}>
          <UsageOverviewChart used={used} remaining={remaining} limit={limit} />
        </DashboardCard>

        <DashboardCard title="Insights summary" description="A compact comparison drawn from the latest report metrics block." floating floatDelay={0.3}>
          <InsightsSummaryChart data={insightData} />
        </DashboardCard>
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.11 }}
        className="grid gap-4 xl:grid-cols-[1.08fr_0.92fr]"
      >
        <DashboardCard className="relative overflow-hidden" hover={false} floating floatDelay={0.22}>
          <AmbientBackground className="absolute inset-0 opacity-80" withParticles particleCount={12} />
          <div className="relative">
            <p className="section-kicker">Latest report summary</p>
            <motion.h2
              initial="hidden"
              animate="visible"
              className="dashboard-hero-title mt-4 text-white"
            >
              <motion.span custom={0} variants={heroLineVariants} className="block">
                Welcome back,
              </motion.span>
              <motion.span custom={1} variants={heroLineVariants} className="hero-gradient-text mt-1 block">
                {heroName}
              </motion.span>
            </motion.h2>

            <p className="type-body mt-3 max-w-2xl">
              {latestBrief?.summary ||
                "Generate your first report to unlock executive summaries, score charts, and premium insight cards."}
            </p>

            <div className="mt-4 flex flex-wrap gap-2.5">
              <span className="premium-badge">{String(currentPlan).toUpperCase()} plan</span>
              <span className="premium-badge">{remaining} reports left</span>
              <span className="premium-badge">{Math.round(usagePercent)}% utilization</span>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <MiniKpi label="Reports used" value={`${used} / ${limit || 0}`} />
              <MiniKpi label="Workspace" value={user?.organization?.name ?? "LifeSignify"} />
              <MiniKpi label="Status" value={user?.subscription?.is_active ? "Active" : "Review"} />
            </div>
          </div>
        </DashboardCard>

        <DashboardCard
          title="Latest delivery"
          description={latestReport?.title ?? "No reports yet"}
          action={<span className="premium-badge">{latestReport ? "Ready" : "Pending"}</span>}
          floating
          floatDelay={0.3}
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <MiniKpi label="Last updated" value={formatDateTime(latestReport?.updated_at ?? latestReport?.created_at)} />
            <MiniKpi label="Confidence" value={latestReport ? String(latestReport.confidence_score) : "--"} />
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            <InsightCard label="Key strength" value={latestBrief?.key_strength} />
            <InsightCard label="Key risk" value={latestBrief?.key_risk} />
            <InsightCard label="Strategic focus" value={latestBrief?.strategic_focus} />
          </div>
        </DashboardCard>
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.16 }}
        className="grid gap-4 md:grid-cols-2 xl:grid-cols-3"
      >
        <ActionPanel
          title={remaining > 0 ? "Create your next report" : "Usage limit reached"}
          copy="Open the guided generation flow with premium frontend interactions while keeping the backend intake contract intact."
          buttonLabel={remaining > 0 ? "Open generator" : "Manage billing"}
          onClick={() => navigate(remaining > 0 ? "/generate-report" : "/billing")}
          variant="primary"
          floatDelay={0.08}
        />
        <ActionPanel
          title="Review reports"
          copy="Browse every generated report with richer cards, better spacing, and smoother hover behavior."
          buttonLabel="Go to reports"
          onClick={() => navigate("/reports")}
          variant="secondary"
          floatDelay={0.18}
        />
        <ActionPanel
          title="Tune subscription"
          copy="Compare plans, review payment history, and upgrade without changing the backend billing flow."
          buttonLabel="Open billing"
          onClick={() => navigate("/billing")}
          variant="success"
          floatDelay={0.28}
        />
      </motion.section>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="premium-page">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Skeleton key={index} className="h-32 rounded-[14px]" />
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Skeleton className="h-[300px] rounded-[14px]" />
        <Skeleton className="h-[300px] rounded-[14px]" />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {Array.from({ length: 5 }).map((_, index) => (
          <Skeleton key={index} className="h-28 rounded-[14px]" />
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.08fr_0.92fr]">
        <Skeleton className="h-[290px] rounded-[14px]" />
        <Skeleton className="h-[290px] rounded-[14px]" />
      </div>
    </div>
  );
}

function WidgetCard({
  label,
  value,
  detail,
  delay,
}: {
  label: string;
  value: string;
  detail: string;
  delay: number;
}) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.32, delay }}
      whileHover={{ y: -4, boxShadow: "0 15px 40px rgba(0, 0, 0, 0.45)" }}
      className="rounded-[14px] border border-white/10 bg-[rgba(15,23,42,0.6)] p-4 backdrop-blur-[16px]"
    >
      <p className="stat-label">{label}</p>
      <p className="mt-2 text-[15px] font-semibold text-white">{value}</p>
      <p className="mt-2 text-[12px] text-slate-400">{detail}</p>
    </motion.article>
  );
}

function MiniKpi({ label, value }: { label: string; value: string }) {
  return (
    <motion.div
      whileHover={{ y: -4, boxShadow: "0 18px 40px rgba(2, 6, 23, 0.28)" }}
      className="rounded-[14px] border border-white/10 bg-black/20 p-3.5 backdrop-blur-xl"
    >
      <p className="stat-label">{label}</p>
      <p className="mt-2 text-[15px] font-semibold text-white">{value}</p>
    </motion.div>
  );
}

function InsightCard({ label, value }: { label: string; value?: string }) {
  return (
    <motion.div
      whileHover={{ y: -4, boxShadow: "0 18px 40px rgba(2, 6, 23, 0.26)" }}
      className="rounded-[14px] border border-white/10 bg-black/15 p-3.5"
    >
      <p className="stat-label">{label}</p>
      <p className="type-body mt-3 text-slate-300">
        {value || "This insight will appear once a report is available."}
      </p>
    </motion.div>
  );
}

function ActionPanel({
  title,
  copy,
  buttonLabel,
  onClick,
  variant,
  floatDelay,
}: {
  title: string;
  copy: string;
  buttonLabel: string;
  onClick: () => void;
  variant: "primary" | "secondary" | "success";
  floatDelay: number;
}) {
  return (
    <DashboardCard hover floating floatDelay={floatDelay} className="flex h-full flex-col justify-between">
      <div>
        <p className="section-kicker">Quick action</p>
        <h3 className="surface-title mt-4 text-white">{title}</h3>
        <p className="type-body mt-4">{copy}</p>
      </div>
      <AnimatedButton className="mt-6 w-full" variant={variant} onClick={onClick}>
        {buttonLabel}
      </AnimatedButton>
    </DashboardCard>
  );
}


