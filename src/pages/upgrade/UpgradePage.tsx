import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import API from "../../services/api";
import AnimatedButton from "../../components/ui/AnimatedButton";
import { useAuth } from "../../context/AuthContext";

declare global {
  interface Window {
    Razorpay: any;
  }
}

export default function UpgradePage() {
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleUpgrade = async () => {
    if (loading || user?.organization?.plan === "pro") return;

    setLoading(true);

    try {
      const orderRes = await API.post("/payments/create-order", { plan: "pro" });
      const { id, amount, currency } = orderRes.data;

      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY,
        amount,
        currency,
        name: "LifeSignify NumAI",
        description: "Pro Subscription",
        order_id: id,
        handler: async (response: any) => {
          const verifyToast = toast.loading("Verifying payment...");

          try {
            await API.post("/payments/verify", {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });

            await refreshUser();
            toast.success("Subscription activated", { id: verifyToast });
            navigate("/dashboard");
          } catch (error: any) {
            toast.error(
              error?.response?.data?.detail?.[0]?.msg ||
                error?.response?.data?.detail ||
                "Payment verification failed",
              { id: verifyToast }
            );
          } finally {
            setLoading(false);
          }
        },
        modal: {
          ondismiss: () => setLoading(false),
        },
        theme: {
          color: "#6366F1",
        },
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (error: any) {
      toast.error(
        error?.response?.data?.detail?.[0]?.msg ||
          error?.response?.data?.detail ||
          "Failed to create order"
      );
      setLoading(false);
    }
  };

  const isPro = user?.organization?.plan === "pro";

  return (
    <div className="flex min-h-[80vh] items-center justify-center">
      <div className="glass-card w-full max-w-md text-center">
        <p className="sidebar-label text-slate-400">Upgrade</p>
        <h1 className="type-h2 mt-3 text-white">Upgrade to Pro</h1>
        <p className="type-body mt-3">Unlock full AI strategic analysis and premium insights.</p>

        <div className="premium-panel mt-6 p-6">
          <p className="type-h2 text-white">INR 999 / month</p>
          <p className="type-body mt-2">Cancel anytime and keep billing simple.</p>
        </div>

        <AnimatedButton onClick={handleUpgrade} disabled={loading || isPro} fullWidth className="mt-6">
          {isPro ? "Already on Pro Plan" : loading ? "Processing..." : "Upgrade Now"}
        </AnimatedButton>

        {isPro && <p className="mt-4 text-[15px] font-medium text-emerald-300">You are already on Pro.</p>}
      </div>
    </div>
  );
}