export interface CoreMetrics {
  risk_band?: string;
  confidence_score?: number;
  karma_pressure_index?: number;
  life_stability_index?: number;
  dharma_alignment_score?: number;
  emotional_regulation_index?: number;
  financial_discipline_index?: number;
}

export interface ExecutiveBrief {
  summary?: string;
  key_strength?: string;
  key_risk?: string;
  strategic_focus?: string;
}

export interface AnalysisSections {
  career_analysis?: string;
  decision_profile?: string;
  emotional_analysis?: string;
  financial_analysis?: string;
  [key: string]: string | undefined;
}

export interface StrategicGuidance {
  short_term?: string;
  mid_term?: string;
  long_term?: string;
  [key: string]: string | undefined;
}

export interface GrowthBlueprint {
  phase_1?: string;
  phase_2?: string;
  phase_3?: string;
  [key: string]: string | undefined;
}

export interface NumerologyArchetype {
  archetype_name?: string;
  core_archetype?: string;
  behavior_style?: string;
  description?: string;
  interpretation?: string;
  [key: string]: string | undefined;
}

export interface NumerologyCore {
  pythagorean?: {
    life_path_number?: number;
    destiny_number?: number;
    expression_number?: number;
  };
  chaldean?: {
    name_number?: number;
  };
  email_analysis?: {
    email_number?: number;
  };
  name_correction?: {
    suggestion?: string;
    current_number?: number;
  };
  loshu_grid?: {
    grid_counts?: Record<string, number>;
    missing_numbers?: string[];
  };
}

export interface ReportMeta {
  plan_tier?: string;
  generated_at?: string;
  engine_version?: string;
  report_version?: string;
  section_count?: number;
  blueprint_version?: string;
}

export interface ReportContent {
  meta?: ReportMeta;
  executive_brief?: ExecutiveBrief;
  core_metrics?: CoreMetrics;
  analysis_sections?: AnalysisSections;
  growth_blueprint?: GrowthBlueprint;
  strategic_guidance?: StrategicGuidance;
  numerology_core?: NumerologyCore;
  numerology_archetype?: NumerologyArchetype;
  business_block?: Record<string, unknown>;
  compatibility_block?: Record<string, unknown>;
  lifestyle_remedies?: Record<string, unknown>;
  mobile_remedies?: Record<string, unknown>;
  vedic_remedies?: Record<string, unknown>;
  radar_chart_data?: Record<string, number>;
  disclaimer?: {
    note?: string;
    framework?: string;
    confidence_score?: number;
  };
  report_blueprint?: {
    section_count?: number;
    sections?: string[];
    [key: string]: unknown;
  };
  correction_block?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface Report {
  id: number;
  title: string;
  content: ReportContent;
  engine_version: string;
  confidence_score: number;
  created_at: string;
  updated_at?: string | null;
}

export interface ReportMetricsResponse {
  total_reports: number;
  subscription_plan: string;
  reports_used_this_month: number;
  monthly_limit: number;
  reports_remaining: number;
}

export interface UsageSummary {
  total_reports: number;
  subscription_plan: string;
  reports_used: number;
  reports_limit: number;
  reports_remaining: number;
}

export interface RadarDataPoint {
  metric: string;
  score: number;
}

export const toUsageSummary = (
  metrics: ReportMetricsResponse
): UsageSummary => ({
  total_reports: metrics.total_reports,
  subscription_plan: metrics.subscription_plan,
  reports_used: metrics.reports_used_this_month,
  reports_limit: metrics.monthly_limit,
  reports_remaining: metrics.reports_remaining,
});

export const normalizeRadarChartData = (
  rawData?: Record<string, number> | null
): RadarDataPoint[] =>
  Object.entries(rawData ?? {}).map(([metric, score]) => ({
    metric,
    score,
  }));
