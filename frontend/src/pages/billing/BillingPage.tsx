import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import AnimatedButton from "../../components/ui/AnimatedButton";
import DashboardCard from "../../components/ui/DashboardCard";
import Skeleton from "../../components/ui/Skeleton";
import StatCard from "../../components/ui/StatCard";
import { useAuth } from "../../context/AuthContext";
import billingService from "../../services/billingService";

interface Plan {
  name: string;
  price: number;
  reports_limit: number;
}

interface PaymentHistory {
  id: number;
  amount: number;
  status: string;
  created_at: string;
}

declare global {
  interface Window {
    Razorpay: any;
  }
}

const planDescriptions: Record<string, string> = {
  basic: "Best for lightweight testing and a focused monthly report cadence.",
  pro: "Built for steady delivery with higher report volume and better operational flexibility.",
  premium: "For teams running premium report output at a significantly larger scale.",
};

const revealTransition = { duration: 0.35, ease: [0.22, 1, 0.36, 1] as const };

const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

export default function BillingPage() {
  const { user, refreshUser } = useAuth();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [payments, setPayments] = useState<PaymentHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [upgradingPlan, setUpgradingPlan] = useState<string | null>(null);

  const currentPlan = user?.subscription?.plan_name?.toLowerCase() || "basic";
  const reportsUsed = user?.subscription?.reports_used ?? 0;
  const subscriptionActive = user?.subscription?.is_active ?? false;

  useEffect(() => {
    const loadBillingData = async () => {
      try {
        const [plansResponse, paymentsResponse] = await Promise.all([
          billingService.getPlans(),
          billingService.getPaymentHistory(),
        ]);

        setPlans(plansResponse || []);
        setPayments(paymentsResponse || []);
      } catch {
        toast.error("Failed to load billing data");
        setPlans([]);
        setPayments([]);
      } finally {
        setLoading(false);
      }
    };

    void loadBillingData();
  }, []);

  const handleUpgrade = async (planName: string) => {
    const normalizedPlan = planName.toLowerCase();

    if (upgradingPlan || currentPlan === normalizedPlan) {
      return;
    }

    setUpgradingPlan(normalizedPlan);

    try {
      const order = await billingService.createOrder(planName);

      if (!window.Razorpay) {
        toast.error("Razorpay SDK is not available");
        setUpgradingPlan(null);
        return;
      }

      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY,
        amount: order.amount,
        currency: "INR",
        order_id: order.id,
        name: "LifeSignify",
        description: `${planName} Subscription`,
        handler: async (response: any) => {
          try {
            await billingService.verifyPayment(response);
            await refreshUser();
            toast.success("Subscription upgraded successfully");
          } catch {
            toast.error("Payment verification failed");
          } finally {
            setUpgradingPlan(null);
          }
        },
        modal: {
          ondismiss: () => setUpgradingPlan(null),
        },
        theme: {
          color: "#4f6fff",
        },
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Payment failed");
      setUpgradingPlan(null);
    }
  };

  if (loading) {
    return <BillingSkeleton />;
  }

  return (
    <div className="premium-page">
      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={revealTransition}
      >
        <DashboardCard className="relative overflow-hidden" hover={false}>
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(245,179,95,0.18),transparent_30%),radial-gradient(circle_at_bottom_right,rgba(58,226,176,0.12),transparent_24%)]" />
          <div className="relative grid gap-6 xl:grid-cols-[1.12fr_0.88fr]">
            <div>
              <p className="section-kicker">Subscription and billing</p>
              <h2 className="section-title-premium mt-4">
                Billing that feels premium, not purely transactional.
              </h2>
              <p className="type-body mt-4 max-w-3xl">
                Compare plans, review usage capacity, and keep the payment flow intact while the frontend becomes cleaner and more deliberate.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-1">
              <StatCard
                compact
                label="Current Plan"
                value={String(currentPlan).toUpperCase()}
                detail={planDescriptions[currentPlan] || "Your active subscription plan from the backend."}
              />
              <StatCard
                compact
                label="Reports Used"
                value={reportsUsed}
                detail={subscriptionActive ? "Live usage from your active subscription." : "Subscription is currently inactive."}
              />
            </div>
          </div>
        </DashboardCard>
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.06 }}
        className="grid gap-4 md:grid-cols-2 xl:grid-cols-3"
      >
        {plans.map((plan, index) => {
          const normalizedPlan = plan.name.toLowerCase();
          const isCurrent = currentPlan === normalizedPlan;
          const isPremium = normalizedPlan === "premium";
          const isLoadingUpgrade = upgradingPlan === normalizedPlan;

          return (
            <motion.article
              key={plan.name}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.28, delay: index * 0.04 }}
              whileHover={{ y: -8, boxShadow: "0 28px 70px rgba(2, 6, 23, 0.42)" }}
              className="premium-panel relative overflow-hidden"
            >
              <div
                className={`pointer-events-none absolute inset-0 ${
                  isPremium
                    ? "bg-[radial-gradient(circle_at_top_right,rgba(245,179,95,0.18),transparent_34%)]"
                    : normalizedPlan === "pro"
                    ? "bg-[radial-gradient(circle_at_top_right,rgba(58,226,176,0.12),transparent_30%)]"
                    : "bg-[radial-gradient(circle_at_top_right,rgba(79,111,255,0.12),transparent_28%)]"
                }`}
              />
              <div className="relative flex h-full flex-col justify-between gap-6">
                <div>
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="surface-title text-white">{plan.name}</h3>
                    {isCurrent && <span className="premium-badge">Current</span>}
                  </div>

                  <p className="type-h2 mt-4 text-white">
                    {currencyFormatter.format(plan.price)}
                  </p>
                  <p className="sidebar-label mt-2 text-slate-500">Per month</p>

                  <p className="type-body mt-4">
                    {planDescriptions[normalizedPlan] ||
                      "Plan details and report limits continue to come from the existing backend pricing endpoint."}
                  </p>

                  <div className="mt-6 rounded-[24px] border border-white/10 bg-black/20 p-4">
                    <p className="stat-label">Monthly report capacity</p>
                    <p className="mt-3 text-[15px] font-medium text-white">
                      {plan.reports_limit} AI report{plan.reports_limit > 1 ? "s" : ""}
                    </p>
                  </div>
                </div>

                {isCurrent ? (
                  <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/8 px-4 py-3 text-center text-[13px] font-medium text-emerald-300">
                    You are currently on this plan.
                  </div>
                ) : (
                  <AnimatedButton className="w-full"
                    loading={isLoadingUpgrade}
                    variant={isPremium ? "success" : "primary"}
                    onClick={() => handleUpgrade(plan.name)}
                  >
                    {isLoadingUpgrade ? "Processing..." : `Upgrade to ${plan.name}`}
                  </AnimatedButton>
                )}
              </div>
            </motion.article>
          );
        })}
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...revealTransition, delay: 0.12 }}
      >
        <DashboardCard
          title="Payment history"
          description="A cleaner ledger view for previous payments and their verification status."
          action={<span className="premium-badge">{payments.length} records</span>}
        >
          {payments.length === 0 ? (
            <div className="premium-panel border-dashed p-8 text-center type-body">
              No payments found yet.
            </div>
          ) : (
            <div className="table-shell overflow-x-auto rounded-[18px]">
              <table className="min-w-[560px] w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400">
                    <th className="px-5 py-4 font-medium">Date</th>
                    <th className="px-5 py-4 font-medium">Amount</th>
                    <th className="px-5 py-4 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map((payment) => (
                    <tr key={payment.id} className="border-b border-white/5 text-slate-300 last:border-b-0">
                      <td className="px-5 py-4">
                        {new Date(payment.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-5 py-4">{currencyFormatter.format(payment.amount)}</td>
                      <td className="px-5 py-4">
                        <span
                          className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${
                            payment.status === "success"
                              ? "bg-emerald-400/10 text-emerald-300"
                              : "bg-amber-400/10 text-amber-300"
                          }`}
                        >
                          {payment.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </DashboardCard>
      </motion.section>
    </div>
  );
}

function BillingSkeleton() {
  return (
    <div className="premium-page">
      <div className="premium-panel space-y-6">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-16 max-w-3xl" />
        <Skeleton className="h-5 max-w-2xl" />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <Skeleton key={index} className="h-[360px] rounded-[28px]" />
        ))}
      </div>

      <Skeleton className="h-[320px] rounded-[28px]" />
    </div>
  );
}
