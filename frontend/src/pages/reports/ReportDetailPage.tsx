import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import API from "../../services/api";
import AnimatedButton from "../../components/ui/AnimatedButton";
import DashboardCard from "../../components/ui/DashboardCard";
import StatCard from "../../components/ui/StatCard";
import { useAuth } from "../../context/AuthContext";
import { type Report } from "../../types/report";

type SectionCard = {
  label?: string;
  value?: string;
};

type SectionPayload = {
  title?: string;
  narrative?: string;
  purpose?: string;
  cards?: SectionCard[];
  bullets?: string[];
  key_inputs?: string[];
  section_key?: string;
};

type BlueprintSection = {
  key?: string;
  title?: string;
  order?: number;
};

const INPUT_LABELS: Record<string, string> = {
  identity: "Identity",
  birth_details: "Birth Details",
  focus: "Focus",
  current_problem: "Current Problem",
  financial: "Financial Snapshot",
  career: "Career Profile",
  emotional: "Emotional State",
  business_history: "Business History",
  health: "Health Profile",
  calibration: "Behavior Calibration",
  contact: "Contact Layer",
  preferences: "Preferences",
};

const INPUT_ALIAS: Record<string, string[]> = {
  intake_context: ["identity", "birth_details", "focus", "current_problem"],
  profile: ["identity", "birth_details"],
  user_profile: ["identity", "birth_details"],
};

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

  useEffect(() => {
    const cleanupPrintMode = () => {
      document.body.classList.remove("report-print-mode");
    };
    window.addEventListener("afterprint", cleanupPrintMode);
    return () => window.removeEventListener("afterprint", cleanupPrintMode);
  }, []);

  const reportPlan =
    report?.content.meta?.plan_tier?.toLowerCase() ||
    user?.subscription?.plan_name?.toLowerCase() ||
    "basic";

  const downloadPDF = async () => {
    if (!id || !report) return;

    const loadingToast = toast.loading("Preparing PDF (this can take some time)...");
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

  const printWebReport = () => {
    document.body.classList.add("report-print-mode");
    window.setTimeout(() => {
      window.print();
    }, 60);
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
          <AnimatedButton variant="secondary" onClick={() => navigate("/reports")}>
            Back to reports
          </AnimatedButton>
        </DashboardCard>
      </div>
    );
  }

  const coreMetrics = report.content.core_metrics;
  const executiveBrief = report.content.executive_brief;
  const sectionPayloads = toSectionPayloads(report.content["section_payloads"]);
  const blueprintSections = toBlueprintSections(report.content.report_blueprint?.sections);
  const orderedSections = buildSectionOrder(sectionPayloads, blueprintSections);
  const inputAvailability = toInputAvailability(report.content["input_availability"]);

  return (
    <div className="premium-page report-print-root report-gold-shell">
      <DashboardCard hover={false} className="relative overflow-hidden report-hero-card">
        <div className="lotus-watermark" aria-hidden />
        <div className="relative z-10 flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
          <div className="max-w-4xl">
            <p className="sidebar-label text-amber-200/70">Report Detail</p>
            <h1 className="section-title-premium mt-4 text-amber-100">{report.title}</h1>
            <p className="type-body mt-4 max-w-3xl text-amber-100/80">
              Created {new Date(report.created_at).toLocaleString()} with confidence {report.confidence_score}. Engine version: {report.engine_version}.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <span className="premium-badge">{reportPlan}</span>
              <span className="premium-badge">Confidence {report.confidence_score}</span>
              <span className="premium-badge">{report.engine_version}</span>
            </div>
          </div>

          <div className="print-hide flex w-full flex-col gap-3 sm:flex-row sm:flex-wrap xl:w-auto xl:justify-end">
            <AnimatedButton className="w-full sm:w-auto" variant="secondary" onClick={() => navigate("/generate-report")}>
              Generate another
            </AnimatedButton>
            <AnimatedButton className="w-full sm:w-auto" onClick={printWebReport}>
              Print from web
            </AnimatedButton>
            <AnimatedButton className="w-full sm:w-auto" variant="ghost" onClick={downloadPDF} loading={downloading}>
              {downloading ? "Preparing..." : "Download PDF (optional)"}
            </AnimatedButton>
          </div>
        </div>
      </DashboardCard>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5 print-hide">
        <StatCard label="Life Stability" value={coreMetrics?.life_stability_index ?? "--"} detail="Core metric from the latest report payload." />
        <StatCard label="Decision Clarity" value={coreMetrics?.confidence_score ?? report.confidence_score} detail="Confidence signal returned by the report engine." />
        <StatCard label="Dharma Alignment" value={coreMetrics?.dharma_alignment_score ?? "--"} detail="Strategic alignment score from the analysis." />
        <StatCard label="Emotional Regulation" value={coreMetrics?.emotional_regulation_index ?? "--"} detail="Emotional steadiness and regulation score." />
        <StatCard label="Financial Discipline" value={coreMetrics?.financial_discipline_index ?? "--"} detail="Financial discipline index pulled from report content." />
      </section>

      <DashboardCard compact title="Executive brief" className="report-page-section">
        <p className="type-body text-slate-100">
          {executiveBrief?.summary ?? "No executive summary is available for this report yet."}
        </p>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <InsightCard label="Key strength" value={executiveBrief?.key_strength ?? "Not available"} />
          <InsightCard label="Key risk" value={executiveBrief?.key_risk ?? "Not available"} />
          <InsightCard label="Strategic focus" value={executiveBrief?.strategic_focus ?? "Not available"} />
        </div>
      </DashboardCard>

      {orderedSections.map(([sectionKey, section]) => {
        const missingInputs = getMissingInputs(section, inputAvailability);
        return (
          <DashboardCard key={sectionKey} compact className="report-page-section report-section-card">
            <h2 className="surface-title text-amber-100">{section.title || formatLabel(sectionKey)}</h2>

            {section.purpose && (
              <p className="type-body mt-3 text-amber-100/80">{section.purpose}</p>
            )}

            {section.narrative && (
              <p className="type-body mt-4 text-slate-100">{section.narrative}</p>
            )}

            {section.cards && section.cards.length > 0 && (
              <div className="mt-5 grid gap-4 md:grid-cols-2">
                {section.cards.map((card, index) => (
                  <div key={`${sectionKey}-card-${index}`} className="section-soft report-note-card">
                    <p className="stat-label text-amber-300">{card.label || "Insight"}</p>
                    <p className="type-body mt-3 text-slate-100">{formatValue(card.value)}</p>
                  </div>
                ))}
              </div>
            )}

            {section.bullets && section.bullets.length > 0 && (
              <ul className="mt-5 list-disc space-y-2 pl-5 text-sm text-slate-100">
                {section.bullets.map((bullet, index) => (
                  <li key={`${sectionKey}-bullet-${index}`}>{bullet}</li>
                ))}
              </ul>
            )}

            {missingInputs.length > 0 && (
              <div className="mt-5 rounded-2xl border border-amber-300/25 bg-amber-300/10 px-4 py-3 text-sm text-amber-100">
                Limited detail in this section because these inputs were not provided: {missingInputs.join(", ")}.
              </div>
            )}
          </DashboardCard>
        );
      })}

      {orderedSections.length === 0 && (
        <DashboardCard compact title="Detailed sections are unavailable right now.">
          <p className="type-body">
            Section payloads were missing in this report response. Generate a fresh report with more complete intake data.
          </p>
        </DashboardCard>
      )}

      {report.content.disclaimer?.note && (
        <DashboardCard compact title="Disclaimer" description="Advisory note returned by the backend.">
          <p className="type-body">{report.content.disclaimer.note}</p>
        </DashboardCard>
      )}
    </div>
  );
}

function InsightCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="section-soft report-note-card">
      <p className="stat-label text-amber-300">{label}</p>
      <p className="type-body mt-3 text-slate-100">{value}</p>
    </div>
  );
}

function toSectionPayloads(value: unknown): Record<string, SectionPayload> {
  if (!value || typeof value !== "object") {
    return {};
  }
  return value as Record<string, SectionPayload>;
}

function toBlueprintSections(value: unknown): BlueprintSection[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item) => item && typeof item === "object") as BlueprintSection[];
}

function toInputAvailability(value: unknown): Record<string, boolean> {
  if (!value || typeof value !== "object") {
    return {};
  }
  const output: Record<string, boolean> = {};
  Object.entries(value as Record<string, unknown>).forEach(([key, raw]) => {
    output[key] = Boolean(raw);
  });
  return output;
}

function buildSectionOrder(
  sectionPayloads: Record<string, SectionPayload>,
  blueprintSections: BlueprintSection[]
): Array<[string, SectionPayload]> {
  const payloadEntries = Object.entries(sectionPayloads);
  if (payloadEntries.length === 0) return [];

  const sortedFromBlueprint = blueprintSections
    .slice()
    .sort((a, b) => Number(a.order ?? 999) - Number(b.order ?? 999))
    .map((section) => section.key)
    .filter((key): key is string => Boolean(key))
    .filter((key) => Boolean(sectionPayloads[key]))
    .map((key) => [key, sectionPayloads[key]] as [string, SectionPayload]);

  const knownKeys = new Set(sortedFromBlueprint.map(([key]) => key));
  const remaining = payloadEntries
    .filter(([key]) => !knownKeys.has(key))
    .sort((a, b) => a[0].localeCompare(b[0]));

  return [...sortedFromBlueprint, ...remaining];
}

function getMissingInputs(
  section: SectionPayload,
  availability: Record<string, boolean>
): string[] {
  const keys = Array.isArray(section.key_inputs) ? section.key_inputs : [];
  if (keys.length === 0) return [];

  const normalizedKeys = keys.flatMap((key) => {
    const normalized = key.trim().toLowerCase();
    if (INPUT_ALIAS[normalized]) {
      return INPUT_ALIAS[normalized];
    }
    return [normalized];
  });

  const uniqueKeys = Array.from(new Set(normalizedKeys));

  const missing = uniqueKeys.filter((key) => {
    if (!(key in availability)) {
      return false;
    }
    return !availability[key];
  });

  return missing.map((key) => INPUT_LABELS[key] || formatLabel(key));
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

  if (value === null || value === undefined || value === "") {
    return "Not provided";
  }

  return String(value);
}
