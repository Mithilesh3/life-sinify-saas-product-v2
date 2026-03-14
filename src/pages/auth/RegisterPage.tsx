import { useState, type ChangeEvent, type FormEvent } from "react";
import { motion } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import AnimatedButton from "../../components/ui/AnimatedButton";
import { useAuth } from "../../context/AuthContext";
import API from "../../services/api";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({
    name: "",
    phone_number: "",
    password: "",
    payment_method: "",
  });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (loading) return;

    if (!form.name || !form.phone_number || !form.password || !form.payment_method) {
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
        name: form.name,
        phone_number: form.phone_number,
        password: form.password,
        payment_method: form.payment_method,
      });
      await login(form.phone_number, form.password);
      toast.success("Welcome to LifeSignify", { id: loadingToast });
      navigate("/dashboard", { replace: true });
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Registration failed", {
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
                name="name"
                value={form.name}
                onChange={handleChange}
                className="register-input mt-2"
                placeholder="Your full name"
              />
            </div>

            <div>
              <label className="register-label">Phone Number</label>
              <input
                name="phone_number"
                type="tel"
                value={form.phone_number}
                onChange={handleChange}
                className="register-input mt-2"
                placeholder="+91 9876543210"
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
