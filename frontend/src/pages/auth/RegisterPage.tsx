import { useState, type ChangeEvent, type FormEvent } from "react";
import { motion } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import AnimatedButton from "../../components/ui/AnimatedButton";
import { useAuth } from "../../context/AuthContext";
import API from "../../services/api";
import { COUNTRIES, COUNTRY_STATE_MAP } from "../../constants/locations";

declare global {
  interface Window {
    Razorpay: any;
  }
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login, refreshUser } = useAuth();

  const [form, setForm] = useState({
    full_name: "",
    mobile_no: "",
    country: "",
    state: "",
    email: "",
    organization_name: "",
    password: "",
    payment_method: "",
  });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const hasConfiguredRazorpayKey = () => {
    const key = String(import.meta.env.VITE_RAZORPAY_KEY ?? "").trim().toLowerCase();
    if (!key) return false;
    return !key.includes("xxxxxxxx") && !key.includes("your-");
  };

  const handleChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    if (name === "country") {
      setForm((current) => ({ ...current, country: value, state: "" }));
      return;
    }
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (loading) return;

    if (
      !form.full_name ||
      !form.mobile_no ||
      !form.country ||
      !form.state ||
      !form.email ||
      !form.organization_name ||
      !form.password ||
      !form.payment_method
    ) {
      toast.error("All fields are required");
      return;
    }

    if (form.password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    const loadingToast = toast.loading("Creating account...");

    try {
      await API.post("/users/register", {
        full_name: form.full_name,
        mobile_no: form.mobile_no,
        country: form.country,
        state: form.state,
        email: form.email,
        organization_name: form.organization_name,
        password: form.password,
        payment_method: form.payment_method,
      });
      await login(form.email, form.password);
      await refreshUser();

      if (!hasConfiguredRazorpayKey()) {
        toast.error("Payment setup is incomplete. Please complete KYC from Billing.", { id: loadingToast });
        navigate("/billing", { replace: true });
        return;
      }

      let id = "";
      let amount = 0;
      let currency = "INR";

      try {
        const orderRes = await API.post("/payments/create-kyc-order");
        id = orderRes.data?.id;
        amount = orderRes.data?.amount;
        currency = orderRes.data?.currency ?? "INR";
      } catch (orderError: any) {
        toast.error(
          orderError?.response?.data?.detail || "Could not start KYC payment. Please continue from Billing.",
          { id: loadingToast }
        );
        navigate("/billing", { replace: true });
        return;
      }

      if (!window.Razorpay) {
        toast.error("Payment UI is unavailable right now. Please continue from Billing.", { id: loadingToast });
        navigate("/billing", { replace: true });
        return;
      }

      await new Promise<void>((resolve, reject) => {
        const instance = new window.Razorpay({
          key: import.meta.env.VITE_RAZORPAY_KEY,
          amount,
          currency,
          name: "LifeSignify NumAI",
          description: "Registration KYC Verification (Rs. 1)",
          order_id: id,
          handler: async (response: any) => {
            try {
              await API.post("/payments/verify-kyc", {
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              });
              await refreshUser();
              resolve();
            } catch (verificationError) {
              reject(verificationError);
            }
          },
          modal: {
            ondismiss: () => reject(new Error("KYC payment cancelled")),
          },
          theme: {
            color: "#4f46e5",
          },
        });
        instance.open();
      });

      toast.success("Account created and KYC verified", { id: loadingToast });
      navigate("/dashboard", { replace: true });
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || error?.message || "Registration failed", {
        id: loadingToast,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <div className="register-cosmic-bg" aria-hidden>
        <div className="register-orbit register-orbit-1" />
        <div className="register-orbit register-orbit-2" />
        <div className="register-orbit register-orbit-3" />

        <div className="register-number-grid">
          <span>1</span>
          <span>2</span>
          <span>3</span>
          <span>4</span>
          <span>5</span>
          <span>6</span>
          <span>7</span>
          <span>8</span>
          <span>9</span>
        </div>

        <span className="register-digit register-digit-3">3</span>
        <span className="register-digit register-digit-7">7</span>
        <span className="register-digit register-digit-9">9</span>
        <span className="register-digit register-digit-11">11</span>
        <span className="register-digit register-digit-22">22</span>
        <span className="register-digit register-digit-33">33</span>

        <span className="register-particle register-particle-1" />
        <span className="register-particle register-particle-2" />
        <span className="register-particle register-particle-3" />
        <span className="register-particle register-particle-4" />
        <span className="register-particle register-particle-5" />
        <span className="register-particle register-particle-6" />
        <span className="register-particle register-particle-7" />
        <span className="register-particle register-particle-8" />
        <span className="register-particle register-particle-9" />
        <span className="register-particle register-particle-10" />
        <span className="register-particle register-particle-11" />
        <span className="register-particle register-particle-12" />
      </div>

      <div className="register-shell">
        <motion.form
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          onSubmit={handleSubmit}
          className="register-card"
        >
          <p className="register-kicker">New account</p>
          <h1 className="register-title">Create account</h1>
          <p className="register-copy">Build your team workspace, then drop directly into the dashboard after signup.</p>

          <div className="mt-6 space-y-4">
            <div>
              <label className="register-label">Name</label>
              <input
                name="full_name"
                value={form.full_name}
                onChange={handleChange}
                className="register-input mt-2"
                placeholder="Your full name"
              />
            </div>

            <div>
              <label className="register-label">Mobile Number</label>
              <input
                name="mobile_no"
                value={form.mobile_no}
                onChange={handleChange}
                className="register-input mt-2"
                placeholder="+91 9876543210"
              />
            </div>

            <div>
              <label className="register-label">Country</label>
              <select
                name="country"
                value={form.country}
                onChange={handleChange}
                className="register-input mt-2"
              >
                <option value="">Select country</option>
                {COUNTRIES.map((country) => (
                  <option key={country} value={country}>
                    {country}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="register-label">State</label>
              <select
                name="state"
                value={form.state}
                onChange={handleChange}
                className="register-input mt-2"
                disabled={!form.country}
              >
                <option value="">Select state</option>
                {(COUNTRY_STATE_MAP[form.country] ?? []).map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="register-label">Email</label>
              <input
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                className="register-input mt-2"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="register-label">Organization Name</label>
              <input
                name="organization_name"
                value={form.organization_name}
                onChange={handleChange}
                className="register-input mt-2"
                placeholder="Acme Ventures"
              />
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label className="register-label">Password</label>
                <button
                  type="button"
                  onClick={() => setShowPassword((current) => !current)}
                  className="text-[11px] uppercase tracking-[0.18em] text-slate-400 transition hover:text-white"
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
              <input
                name="password"
                type={showPassword ? "text" : "password"}
                value={form.password}
                onChange={handleChange}
                className="register-input mt-2"
                placeholder="Choose a secure password"
              />
              <p className="register-hint mt-2">Minimum 6 characters.</p>
            </div>

            <div>
              <label className="register-label">Payment Method</label>
              <select
                name="payment_method"
                value={form.payment_method}
                onChange={handleChange}
                className="register-input mt-2"
              >
                <option value="">Select payment method</option>
                <option value="UPI">UPI</option>
                <option value="Credit/Debit Card">Credit/Debit Card</option>
                <option value="Net Banking">Net Banking</option>
              </select>
            </div>
          </div>

          <div className="mt-7 space-y-4">
            <AnimatedButton type="submit" loading={loading} fullWidth className="register-button">
              {loading ? "Creating account..." : "Create account"}
            </AnimatedButton>

            <p className="register-footer">
              Already have an account?{" "}
              <Link to="/login" className="register-link">
                Log in
              </Link>
            </p>
          </div>
        </motion.form>
      </div>
    </div>
  );
}
