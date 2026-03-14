import { useEffect, useState, type ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import API from "../../services/api";
import RadarChartComponent from "../../components/dashboard/RadarChartComponent";
import AnimatedButton from "../../components/ui/AnimatedButton";
import DashboardCard from "../../components/ui/DashboardCard";
import StatCard from "../../components/ui/StatCard";
import { useAuth } from "../../context/AuthContext";
import {
  type RadarDataPoint,
  type Report,
  normalizeRadarChartData,
} from "../../types/report";

export default function ReportDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) {
      setError("Report not found.");
      setLoading(false);
      return;
    }

    const fetchReport = async () => {
      try {
        const res = await API.get<Report>(`/reports/${id}`);
        setReport(res.data);
      } catch {
        setError("Failed to load report.");
        toast.error("Failed to load report");
      } finally {
        setLoading(false);
      }
    };

    void fetchReport();
  }, [id]);

  const reportPlan =
    report?.content.meta?.plan_tier?.toLowerCase() ||
    user?.subscription?.plan_name?.toLowerCase() ||
    "basic";

  const downloadPDF = async () => {
    if (!id || !report) return;

    const loadingToast = toast.loading("Preparing PDF...");
    setDownloading(true);

    try {
      const pdfRoute =
        reportPlan === "basic"
          ? `/reports/${id}/preview-pdf`
          : `/reports/${id}/export-pdf`;

      const response = await API.get(pdfRoute, {
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `report-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success("Report downloaded successfully", { id: loadingToast });
    } catch {
      toast.error("Failed to download PDF", { id: loadingToast });
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="premium-page">
        <DashboardCard compact title="Loading report" description="Pulling the latest report content from the backend.">
          <div className="h-40 loading-shimmer rounded-[18px]" />
        </DashboardCard>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="premium-page">
        <DashboardCard compact title="Unable to load report" description={error || "Report not found."}>
          <AnimatedButton variant="secondary" onClick={() => navigate("/reports")}>Back to reports</AnimatedButton>
        </DashboardCard>
      </div>
    );
  }

  const radarData: RadarDataPoint[] = normalizeRadarChartData(report.content.radar_chart_data);
  const coreMetrics = report.content.core_metrics;
  const executiveBrief = report.content.executive_brief;
  const numerologyCore = report.content.numerology_core;

  return (
    <div className="premium-page">
      <DashboardCard hover={false} className="relative overflow-hidden">
        <div className="page-hero-glow" />
        <div className="page-hero-mesh" />
        <div className="relative z-10 flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
          <div className="max-w-4xl">
            <p className="sidebar-label text-slate-400">Report Detail</p>
            <h1 className="section-title-premium mt-4">{report.title}</h1>
            <p className="type-body mt-4 max-w-3xl">
              Created {new Date(report.created_at).toLocaleString()} with confidence {report.confidence_score}. Engine version: {report.engine_version}.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <span className="premium-badge">{reportPlan}</span>
              <span className="premium-badge">Confidence {report.confidence_score}</span>
              <span className="premium-badge">{report.engine_version}</span>
            </div>
          </div>

          <div className="flex w-full flex-col gap-3 sm:flex-row sm:flex-wrap xl:w-auto xl:justify-end">
            <AnimatedButton className="w-full sm:w-auto" variant="secondary" onClick={() => navigate("/generate-report")}>
              Generate another
            </AnimatedButton>
            <AnimatedButton className="w-full sm:w-auto" onClick={downloadPDF} loading={downloading}>
              {downloading ? "Preparing..." : reportPlan === "basic" ? "Preview PDF" : "Download PDF"}
            </AnimatedButton>
          </div>
        </div>
      </DashboardCard>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Life Stability" value={coreMetrics?.life_stability_index ?? "--"} detail="Core metric from the latest report payload." />
        <StatCard label="Decision Clarity" value={coreMetrics?.confidence_score ?? report.confidence_score} detail="Confidence signal returned by the report engine." />
        <StatCard label="Dharma Alignment" value={coreMetrics?.dharma_alignment_score ?? "--"} detail="Strategic alignment score from the analysis." />
        <StatCard label="Emotional Regulation" value={coreMetrics?.emotional_regulation_index ?? "--"} detail="Emotional steadiness and regulation score." />
        <StatCard label="Financial Discipline" value={coreMetrics?.financial_discipline_index ?? "--"} detail="Financial discipline index pulled from report content." />
      </section>

      {radarData.length > 0 && (
        <DashboardCard title="Life stability radar" description="A normalized visual comparison across the current report metrics.">
          <RadarChartComponent data={radarData} />
        </DashboardCard>
      )}

      <Section title="Executive brief">
        <p className="type-body text-slate-200">
          {executiveBrief?.summary ?? "No executive summary is available for this report yet."}
        </p>
        <div className="grid gap-4 md:grid-cols-3">
          <InsightCard label="Key strength" value={executiveBrief?.key_strength ?? "Not available"} />
          <InsightCard label="Key risk" value={executiveBrief?.key_risk ?? "Not available"} />
          <InsightCard label="Strategic focus" value={executiveBrief?.strategic_focus ?? "Not available"} />
        </div>
      </Section>

      <div className="grid gap-4 xl:grid-cols-2">
        <DetailGrid title="Analysis sections" data={report.content.analysis_sections} />
        <DetailGrid title="Growth blueprint" data={report.content.growth_blueprint} />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <DetailGrid title="Strategic guidance" data={report.content.strategic_guidance} />
        <DetailGrid title="Archetype profile" data={report.content.numerology_archetype} />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <DetailGrid title="Pythagorean core" data={numerologyCore?.pythagorean} />
        <DetailGrid
          title="Supportive numerology"
          data={{
            ...(numerologyCore?.chaldean ?? {}),
            ...(numerologyCore?.email_analysis ?? {}),
            ...(numerologyCore?.name_correction ?? {}),
          }}
        />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <DetailGrid title="Lifestyle remedies" data={report.content.lifestyle_remedies} />
        <DetailGrid title="Mobile remedies" data={report.content.mobile_remedies} />
        <DetailGrid title="Vedic remedies" data={report.content.vedic_remedies} />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <DetailGrid title="Business insights" data={report.content.business_block} />
        <DetailGrid title="Compatibility" data={report.content.compatibility_block} />
      </div>

      {report.content.disclaimer?.note && (
        <DashboardCard compact title="Disclaimer" description="Advisory note returned by the backend.">
          <p className="type-body">{report.content.disclaimer.note}</p>
        </DashboardCard>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return <DashboardCard title={title}>{children}</DashboardCard>;
}

function InsightCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="section-soft p-4">
      <p className="stat-label">{label}</p>
      <p className="type-body mt-3 text-slate-200">{value}</p>
    </div>
  );
}

function DetailGrid({
  title,
  data,
}: {
  title: string;
  data?: Record<string, unknown>;
}) {
  const entries = Object.entries(data ?? {}).filter(([, value]) => {
    if (value === undefined || value === null || value === "") {
      return false;
    }

    if (Array.isArray(value)) {
      return value.length > 0;
    }

    if (typeof value === "object") {
      return Object.keys(value as Record<string, unknown>).length > 0;
    }

    return true;
  });

  if (entries.length === 0) {
    return null;
  }

  return (
    <DashboardCard title={title} compact>
      <div className="grid gap-4 md:grid-cols-2">
        {entries.map(([key, value]) => (
          <div key={key} className="section-soft p-4">
            <p className="stat-label">{formatLabel(key)}</p>
            <p className="type-body mt-3 text-slate-200">{formatValue(value)}</p>
          </div>
        ))}
      </div>
    </DashboardCard>
  );
}

function formatLabel(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value.map((item) => formatValue(item)).join(", ");
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  if (typeof value === "object" && value) {
    return Object.entries(value as Record<string, unknown>)
      .map(([key, nestedValue]) => `${formatLabel(key)}: ${formatValue(nestedValue)}`)
      .join(", ");
  }

  return String(value);
}