import API from "./api";
import {
  type ReportMetricsResponse,
  type UsageSummary,
  toUsageSummary,
} from "../types/report";

export const getUsage = async (): Promise<UsageSummary> => {
  const res = await API.get<ReportMetricsResponse>("/reports/metrics/usage");
  return toUsageSummary(res.data);
};
