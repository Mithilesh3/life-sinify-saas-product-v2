import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import AnimatedButton from "../../components/ui/AnimatedButton";
import DashboardCard from "../../components/ui/DashboardCard";
import PageHero from "../../components/ui/PageHero";
import Skeleton from "../../components/ui/Skeleton";
import API from "../../services/api";
import type { Report } from "../../types/report";


function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function ReportsListPage() {
  const navigate = useNavigate();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await API.get<Report[]>("/reports/");
        setReports(response.data);
      } catch {
        setError("Failed to load reports.");
        toast.error("Failed to load reports");
      } finally {
        setLoading(false);
      }
    };

    void fetchReports();
  }, []);

  return (
    <div className="premium-page">
      <PageHero
        eyebrow="Workspace / Reports"
        title="A premium library for every generated report."
        description="Better scanning for metadata, confidence, and executive summaries while keeping the same API contract underneath."
        badges={[`${reports.length} reports`, "Backend contract aligned"]}
        action={<AnimatedButton onClick={() => navigate("/generate-report")}>Generate new report</AnimatedButton>}
        aside={
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
            <QuickFact label="Library state" value={reports.length > 0 ? "Active" : "Empty"} />
            <QuickFact label="Latest engine" value={reports[0]?.engine_version ?? "Pending"} />
          </div>
        }
      />

      {loading ? (
        <ReportsSkeleton />
      ) : error ? (
        <DashboardCard compact title="Unable to load reports" description={error}>
          <AnimatedButton variant="secondary" onClick={() => window.location.reload()}>
            Retry
          </AnimatedButton>
        </DashboardCard>
      ) : reports.length === 0 ? (
        <DashboardCard
          compact
          title="No reports yet"
          description="Generate your first AI insight report to start building the premium report archive."
          action={
            <AnimatedButton onClick={() => navigate("/generate-report")}>
              Create first report
            </AnimatedButton>
          }
        >
          <div className="premium-panel border-dashed p-6 type-body">
            Your list will automatically hydrate from the existing backend endpoint once a report is created.
          </div>
        </DashboardCard>
      ) : (
        <section className="space-y-3">
          {reports.map((report, index) => {
            const planTier = report.content.meta?.plan_tier ?? "basic";
            const summary =
              report.content.executive_brief?.summary ||
              "Open this report to review the executive brief, metrics, and remedies returned by the backend.";

            return (
              <motion.article
                key={report.id}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.28, delay: index * 0.04 }}
                whileHover={{ y: -6, boxShadow: "0 24px 60px rgba(2, 6, 23, 0.36)" }}
                className="premium-panel !rounded-[24px] !p-5 md:!p-6"
              >
                <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
                  <div className="space-y-4">
                    <div className="flex flex-wrap items-center gap-3">
                      <h3 className="surface-title text-white">
                        {report.title}
                      </h3>
                      <span className="premium-badge">{String(planTier).toUpperCase()}</span>
                    </div>

                    <p className="type-body max-w-3xl">{summary}</p>

                    <div className="flex flex-wrap gap-2.5">
                      <MetaPill label="Created" value={formatDate(report.created_at)} />
                      <MetaPill label="Confidence" value={String(report.confidence_score)} />
                      <MetaPill label="Engine" value={report.engine_version} />
                      {report.updated_at && <MetaPill label="Updated" value={formatDate(report.updated_at)} />}
                    </div>
                  </div>

                  <AnimatedButton variant="secondary" className="w-full sm:w-auto self-stretch sm:self-start xl:self-center" onClick={() => navigate(`/reports/${report.id}`)}>
                    View report
                  </AnimatedButton>
                </div>
              </motion.article>
            );
          })}
        </section>
      )}
    </div>
  );
}

function ReportsSkeleton() {
  return (
    <section className="space-y-3">
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="premium-panel !rounded-[24px] !p-5 md:!p-6 space-y-4">
          <div className="flex flex-wrap gap-3">
            <Skeleton className="h-9 w-2/3 max-w-xl" />
            <Skeleton className="h-7 w-28 rounded-full" />
          </div>
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <div className="flex flex-wrap gap-2.5">
            <Skeleton className="h-7 w-40 rounded-full" />
            <Skeleton className="h-7 w-28 rounded-full" />
            <Skeleton className="h-7 w-24 rounded-full" />
          </div>
        </div>
      ))}
    </section>
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

function MetaPill({ label, value }: { label: string; value: string }) {
  return (
    <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-[10px] font-medium uppercase tracking-[0.24em] text-slate-300">
      {label}: {value}
    </span>
  );
}

