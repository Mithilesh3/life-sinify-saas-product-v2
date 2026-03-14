import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import InsightsSummaryChart from "../../components/charts/InsightsSummaryChart";
import DashboardCard from "../../components/ui/DashboardCard";
import PageHero from "../../components/ui/PageHero";
import Skeleton from "../../components/ui/Skeleton";
import StatCard from "../../components/ui/StatCard";
import { fetchAdminAnalytics } from "../../services/adminService";

interface AdminAnalytics {
  total_users: number;
  total_reports: number;
  total_organizations: number;
  active_subscriptions: number;
}

const initialAnalytics: AdminAnalytics = {
  total_users: 0,
  total_reports: 0,
  total_organizations: 0,
  active_subscriptions: 0,
};

const revealTransition = { duration: 0.35, ease: [0.22, 1, 0.36, 1] as const };

export default function AdminDashboard() {
  const [analytics, setAnalytics] = useState<AdminAnalytics>(initialAnalytics);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const data = await fetchAdminAnalytics();
        setAnalytics(data);
      } catch {
        toast.error("Failed to load admin analytics");
      } finally {
        setLoading(false);
      }
    };

    void loadAnalytics();
  }, []);

  const summaryData = useMemo(
    () => [
      { label: "Users", value: analytics.total_users },
      { label: "Reports", value: analytics.total_reports },
      { label: "Orgs", value: analytics.total_organizations },
      { label: "Active", value: analytics.active_subscriptions },
    ],
    [analytics]
  );

  if (loading) {
    return (
      <div className="premium-page">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-32 rounded-[22px]" />
          ))}
        </div>
        <Skeleton className="h-[260px] rounded-[26px]" />
      </div>
    );
  }

  return (
    <div className="premium-page">
      <PageHero
        eyebrow="Workspace / Admin"
        title="Sharper admin analytics with less visual noise."
        description="Tenant-wide health and operational totals, arranged in a tighter executive surface that stays aligned with the backend analytics endpoint."
        badges={[`${analytics.total_users} users`, `${analytics.total_reports} reports`, `${analytics.active_subscriptions} active`]}
        aside={
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-2">
            <QuickFact label="Users" value={String(analytics.total_users)} />
            <QuickFact label="Reports" value={String(analytics.total_reports)} />
            <QuickFact label="Organizations" value={String(analytics.total_organizations)} />
            <QuickFact label="Active" value={String(analytics.active_subscriptions)} />
          </div>
        }
      />

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.06 }}
        className="grid gap-3 md:grid-cols-2 xl:grid-cols-4"
      >
        <StatCard compact label="Total Users" value={analytics.total_users} detail="Users across all organizations." />
        <StatCard compact label="Total Reports" value={analytics.total_reports} detail="Reports tracked by the analytics endpoint." />
        <StatCard compact label="Organizations" value={analytics.total_organizations} detail="Provisioned tenant organizations." />
        <StatCard compact label="Active Subscriptions" value={analytics.active_subscriptions} detail="Subscriptions currently marked active." />
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.12 }}
        className="grid gap-3 xl:grid-cols-[1fr_0.92fr]"
      >
        <DashboardCard compact title="Analytics snapshot" description="A compact visual distribution of the core admin counters returned by the backend.">
          <InsightsSummaryChart data={summaryData} />
        </DashboardCard>

        <DashboardCard compact title="Backend alignment" description="Why this page is safer now: it is a real analytics screen instead of a duplicate users table.">
          <div className="premium-panel p-5 type-body">
            The admin area reads <code>/api/admin/analytics</code>, so these tiles and charts reflect live totals for users, reports, organizations, and active subscriptions without affecting backend behavior.
          </div>
        </DashboardCard>
      </motion.section>
    </div>
  );
}

function QuickFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[18px] border border-white/10 bg-black/20 p-3.5">
      <p className="stat-label text-[10px] tracking-[0.28em]">{label}</p>
      <p className="mt-2 text-[15px] font-medium text-white">{value}</p>
    </div>
  );
}
