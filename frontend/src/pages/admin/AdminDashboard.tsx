import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import InsightsSummaryChart from "../../components/charts/InsightsSummaryChart";
import DashboardCard from "../../components/ui/DashboardCard";
import PageHero from "../../components/ui/PageHero";
import Skeleton from "../../components/ui/Skeleton";
import StatCard from "../../components/ui/StatCard";
import { fetchAdminAnalytics, fetchCustomerKycStatus } from "../../services/adminService";

interface AdminAnalytics {
  total_users: number;
  total_reports: number;
  total_organizations: number;
  active_subscriptions: number;
  total_customers: number;
  kyc_verified: number;
  kyc_pending: number;
}

interface CustomerKycStatus {
  id: number;
  full_name?: string;
  mobile_no?: string;
  country?: string;
  state?: string;
  email: string;
  role: string;
  payment_method?: string;
  kyc_verified: boolean;
  created_at: string;
}

const initialAnalytics: AdminAnalytics = {
  total_users: 0,
  total_reports: 0,
  total_organizations: 0,
  active_subscriptions: 0,
  total_customers: 0,
  kyc_verified: 0,
  kyc_pending: 0,
};

const revealTransition = { duration: 0.35, ease: [0.22, 1, 0.36, 1] as const };

export default function AdminDashboard() {
  const [analytics, setAnalytics] = useState<AdminAnalytics>(initialAnalytics);
  const [customers, setCustomers] = useState<CustomerKycStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const [analyticsData, customerData] = await Promise.all([
          fetchAdminAnalytics(),
          fetchCustomerKycStatus(),
        ]);
        setAnalytics(analyticsData);
        setCustomers(customerData);
      } catch {
        toast.error("Failed to load super admin analytics");
      } finally {
        setLoading(false);
      }
    };

    void loadAnalytics();
  }, []);

  const summaryData = useMemo(
    () => [
      { label: "Customers", value: analytics.total_customers },
      { label: "KYC Verified", value: analytics.kyc_verified },
      { label: "KYC Pending", value: analytics.kyc_pending },
      { label: "Reports", value: analytics.total_reports },
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
        eyebrow="Workspace / Super Admin"
        title="Customer registration and KYC control center."
        description="Live visibility into who registered, who completed Rs. 1 KYC, and current business totals."
        badges={[`${analytics.total_customers} customers`, `${analytics.kyc_verified} KYC verified`, `${analytics.kyc_pending} pending`]}
        aside={
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-2">
            <QuickFact label="Customers" value={String(analytics.total_customers)} />
            <QuickFact label="KYC Verified" value={String(analytics.kyc_verified)} />
            <QuickFact label="KYC Pending" value={String(analytics.kyc_pending)} />
            <QuickFact label="Reports" value={String(analytics.total_reports)} />
          </div>
        }
      />

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.06 }}
        className="grid gap-3 md:grid-cols-2 xl:grid-cols-4"
      >
        <StatCard compact label="Total Customers" value={analytics.total_customers} detail="Registered users excluding super admin." />
        <StatCard compact label="KYC Verified" value={analytics.kyc_verified} detail="Customers who completed Rs. 1 verification." />
        <StatCard compact label="KYC Pending" value={analytics.kyc_pending} detail="Customers pending KYC verification." />
        <StatCard compact label="Total Reports" value={analytics.total_reports} detail="Reports tracked by the analytics endpoint." />
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.12 }}
        className="grid gap-3 xl:grid-cols-[1fr_0.92fr]"
      >
        <DashboardCard compact title="Analytics snapshot" description="A compact visual distribution of customer and KYC counters.">
          <InsightsSummaryChart data={summaryData} />
        </DashboardCard>

        <DashboardCard compact title="Latest registrations" description="Recent customers and KYC status.">
          <div className="table-shell overflow-x-auto rounded-[18px]">
            <table className="min-w-[980px] w-full text-left text-sm">
              <thead>
                <tr className="border-b border-white/10 text-slate-400">
                  <th className="px-4 py-3 font-medium">Name</th>
                  <th className="px-4 py-3 font-medium">Email</th>
                  <th className="px-4 py-3 font-medium">Mobile</th>
                  <th className="px-4 py-3 font-medium">Country/State</th>
                  <th className="px-4 py-3 font-medium">Role</th>
                  <th className="px-4 py-3 font-medium">Payment Method</th>
                  <th className="px-4 py-3 font-medium">KYC</th>
                  <th className="px-4 py-3 font-medium">Registered</th>
                </tr>
              </thead>
              <tbody>
                {customers.slice(0, 20).map((customer) => (
                  <tr key={customer.id} className="border-b border-white/5 text-slate-300 last:border-b-0">
                    <td className="px-4 py-3">{customer.full_name || "N/A"}</td>
                    <td className="px-4 py-3">{customer.email}</td>
                    <td className="px-4 py-3">{customer.mobile_no || "N/A"}</td>
                    <td className="px-4 py-3">{`${customer.country || "N/A"} / ${customer.state || "N/A"}`}</td>
                    <td className="px-4 py-3 capitalize">{customer.role}</td>
                    <td className="px-4 py-3">{customer.payment_method || "N/A"}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] ${
                          customer.kyc_verified ? "bg-emerald-400/10 text-emerald-300" : "bg-amber-400/10 text-amber-300"
                        }`}
                      >
                        {customer.kyc_verified ? "Verified" : "Pending"}
                      </span>
                    </td>
                    <td className="px-4 py-3">{new Date(customer.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
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
