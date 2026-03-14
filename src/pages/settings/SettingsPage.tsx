import { motion } from "framer-motion";
import PageHero from "../../components/ui/PageHero";
import DashboardCard from "../../components/ui/DashboardCard";
import StatCard from "../../components/ui/StatCard";
import { useAuth } from "../../context/AuthContext";

const revealTransition = { duration: 0.35, ease: [0.22, 1, 0.36, 1] as const };

export default function SettingsPage() {
  const { user } = useAuth();

  const plan = user?.subscription?.plan_name || user?.organization?.plan || "free";
  const isActive = user?.subscription?.is_active ?? false;
  const reportsUsed = user?.subscription?.reports_used ?? 0;

  return (
    <div className="premium-page">
      <PageHero
        eyebrow="Workspace / Settings"
        title="A calmer settings experience for everyday workspace control."
        description="The same backend user payload, refined into a more deliberate workspace settings surface with clearer hierarchy and lighter density."
        badges={[String(plan).toUpperCase(), isActive ? "Subscription active" : "Subscription inactive", `${reportsUsed} reports used`]}
        aside={
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
            <QuickFact label="Organization" value={user?.organization?.name ?? "LifeSignify"} />
            <QuickFact label="Role" value={user?.role ?? "user"} />
          </div>
        }
      />

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.05 }}
        className="grid gap-3 md:grid-cols-3"
      >
        <StatCard compact label="Plan" value={String(plan).toUpperCase()} detail="Workspace subscription tier." />
        <StatCard compact label="Subscription" value={isActive ? "Active" : "Inactive"} detail="Current billing status." />
        <StatCard compact label="Reports Used" value={reportsUsed} detail="Usage from the subscription object." />
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.1 }}
        className="grid gap-3 xl:grid-cols-[1fr_0.9fr]"
      >
        <DashboardCard compact title="Workspace identity" description="Core account details in a tighter, scan-friendly layout.">
          <div className="grid gap-3 md:grid-cols-2">
            <InfoCard label="Email" value={user?.email ?? "Not available"} />
            <InfoCard label="Organization" value={user?.organization?.name ?? "Not available"} />
            <InfoCard label="Role" value={user?.role ?? "user"} />
            <InfoCard label="Tenant ID" value={String(user?.organization?.id ?? user?.id ?? "-")} />
          </div>
        </DashboardCard>

        <DashboardCard compact title="Plan status" description="Subscription and ownership signals at a glance.">
          <div className="space-y-3">
            <StatusRow label="Subscription" value={isActive ? "Active" : "Inactive"} tone={isActive ? "success" : "muted"} />
            <StatusRow
              label="Plan source"
              value={user?.subscription?.plan_name ? "Subscription" : "Organization fallback"}
              tone="muted"
            />
            <StatusRow label="Workspace" value={user?.organization?.name ?? "LifeSignify"} tone="muted" />
          </div>
        </DashboardCard>
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.15 }}
      >
        <DashboardCard compact title="Future preferences" description="A reserved surface for theme, collaboration, security, and notification settings.">
          <div className="premium-panel border-dashed p-5 type-body">
            This page stays frontend-led: cleaner hierarchy, better density, and no changes to the backend user model.
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
      <p className="mt-2 text-[15px] font-medium text-white break-words">{value}</p>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[20px] border border-white/10 bg-black/20 p-4">
      <p className="stat-label text-[10px] tracking-[0.28em]">{label}</p>
      <p className="mt-3 text-[15px] font-medium text-white break-words">{value}</p>
    </div>
  );
}

function StatusRow({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "success" | "muted";
}) {
  const valueClass = tone === "success" ? "text-emerald-300" : "text-slate-200";

  return (
    <div className="flex items-center justify-between rounded-[20px] border border-white/10 bg-black/20 px-4 py-3.5">
      <span className="stat-label text-[10px] tracking-[0.28em]">{label}</span>
      <span className={`text-[15px] font-medium ${valueClass}`}>
        {value}
      </span>
    </div>
  );
}
