import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import LoginForm from "../../components/auth/LoginForm";
import { useAuth } from "../../context/AuthContext";

export default function LoginPage() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      navigate("/dashboard", { replace: true });
    }
  }, [navigate, user]);

  const handleLogin = async ({ phoneNumber, password }: { phoneNumber: string; password: string }) => {
    if (loading) return;

    if (!phoneNumber || !password) {
      toast.error("Please enter phone number and password");
      return;
    }

    setLoading(true);

    try {
      await login(phoneNumber, password);
      toast.success("Welcome back");
      navigate("/dashboard", { replace: true });
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page auth-cosmic-shell">
      <div className="solar-system-bg" aria-hidden>
        <div className="solar-stars-layer" />
        <div className="solar-nebula" />
        <div className="solar-particles-layer">
          <span className="solar-particle solar-particle-1" />
          <span className="solar-particle solar-particle-2" />
          <span className="solar-particle solar-particle-3" />
          <span className="solar-particle solar-particle-4" />
          <span className="solar-particle solar-particle-5" />
          <span className="solar-particle solar-particle-6" />
          <span className="solar-particle solar-particle-7" />
          <span className="solar-particle solar-particle-8" />
        </div>
        <div className="numerology-floaters">
          <span className="numerology-digit digit-1">3</span>
          <span className="numerology-digit digit-2">6</span>
          <span className="numerology-digit digit-3">9</span>
          <span className="numerology-digit digit-4">1</span>
          <span className="numerology-digit digit-5">7</span>
        </div>
        <span className="auth-om-symbol">{`\u0950`}</span>
        <div className="solar-constellation solar-constellation-top" />
        <div className="solar-constellation solar-constellation-bottom" />
        <div className="solar-comet" />

        <div className="solar-planet-large solar-planet-jupiter" />
        <div className="solar-planet-large solar-planet-saturn" />
        <div className="solar-planet-large solar-planet-earth" />
        <div className="solar-planet-large solar-planet-ice" />
        <div className="solar-core" />

        <div className="solar-orbit solar-orbit-1">
          <div className="solar-planet solar-planet-1" />
        </div>
        <div className="solar-orbit solar-orbit-2">
          <div className="solar-planet solar-planet-2" />
        </div>
        <div className="solar-orbit solar-orbit-3">
          <div className="solar-planet solar-planet-3" />
        </div>
        <div className="solar-orbit solar-orbit-4">
          <div className="solar-planet solar-planet-4" />
        </div>
        <div className="solar-orbit solar-orbit-5">
          <div className="solar-planet solar-planet-5" />
        </div>
      </div>
      <div className="app-shell relative z-10 grid min-h-screen items-start gap-5 py-6 sm:gap-6 sm:py-8 lg:min-h-[calc(100vh-4rem)] lg:grid-cols-[1.04fr_0.96fr] lg:items-start lg:gap-8 lg:py-10">
        <div className="hidden lg:block" />

        <motion.div
          initial={{ opacity: 0, x: 24, scale: 0.98 }}
          animate={{ opacity: 1, x: 0, scale: 1, y: [0, -6, 0] }}
          transition={{
            opacity: { duration: 0.55 },
            x: { duration: 0.55, ease: [0.22, 1, 0.36, 1] },
            scale: { duration: 0.55, ease: [0.22, 1, 0.36, 1] },
            y: { duration: 7, repeat: Infinity, ease: "easeInOut" },
          }}
          className="relative order-1 flex justify-center lg:order-2 lg:justify-end"
        >
          <div className="pointer-events-none absolute inset-4 -z-10 rounded-[34px] bg-gradient-to-br from-violet-500/26 via-indigo-500/14 to-cyan-300/16 blur-3xl" />
          <div className="flex w-full max-w-[430px] flex-col items-start gap-3 sm:gap-4 lg:items-end">
            <div className="auth-brand-card">
              <h1 className="auth-heading auth-hero-title auth-brand-title">
                LifeSignify NumAI
              </h1>
            </div>
            <LoginForm loading={loading} onSubmit={handleLogin} />
          </div>
        </motion.div>
      </div>
    </div>
  );
}
