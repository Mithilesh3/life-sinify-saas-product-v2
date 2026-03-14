import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { getUsage } from "../services/usageService";
import { useAuth } from "./AuthContext";
import type { UsageSummary } from "../types/report";

const PLAN_LIMITS: Record<string, number> = {
  basic: 1,
  pro: 5,
  premium: 50,
  enterprise: 200,
};

const UsageContext = createContext<{
  usage: UsageSummary | null;
  refreshUsage: () => Promise<void>;
} | null>(null);

export const UsageProvider = ({ children }: { children: ReactNode }) => {
  const { user } = useAuth();
  const [usage, setUsage] = useState<UsageSummary | null>(null);

  const loadUsage = async () => {
    if (!user) {
      setUsage(null);
      return;
    }

    try {
      const data = await getUsage();
      setUsage(data);
    } catch {
      if (!user.subscription) {
        setUsage(null);
        return;
      }

      const reportsLimit = user.subscription.is_active
        ? PLAN_LIMITS[user.subscription.plan_name?.toLowerCase()] ?? 0
        : 0;

      setUsage({
        total_reports: 0,
        subscription_plan: user.subscription.plan_name ?? "none",
        reports_used: user.subscription.reports_used,
        reports_limit: reportsLimit,
        reports_remaining: Math.max(
          reportsLimit - user.subscription.reports_used,
          0
        ),
      });
    }
  };

  useEffect(() => {
    if (user) {
      void loadUsage();
    } else {
      setUsage(null);
    }
  }, [user]);

  return (
    <UsageContext.Provider value={{ usage, refreshUsage: loadUsage }}>
      {children}
    </UsageContext.Provider>
  );
};

export const useUsage = () => {
  const ctx = useContext(UsageContext);
  if (!ctx) throw new Error("useUsage must be inside UsageProvider");
  return ctx;
};
