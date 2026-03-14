import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import AnimatedButton from "../ui/AnimatedButton";

interface LoginFormProps {
  loading: boolean;
  onSubmit: (credentials: { phoneNumber: string; password: string }) => Promise<void>;
}

export default function LoginForm({ loading, onSubmit }: LoginFormProps) {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onSubmit({ phoneNumber, password });
  };

  return (
    <form onSubmit={handleSubmit} className="auth-glass-panel auth-login-panel w-full max-w-[430px] space-y-4 p-5 sm:p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="section-kicker">Member Access</p>
          <h1 className="auth-heading auth-card-title mt-2 text-white">
            Sign in
          </h1>
        </div>
        <span className="premium-badge">Secure</span>
      </div>

      <p className="type-body mt-0.5 text-[15px] leading-relaxed">
        Enter your credentials to access your numerology workspace.
      </p>

      <div className="space-y-3.5">
        <div>
          <label className="field-label">Phone Number</label>
          <input
            type="tel"
            className="input auth-input mt-2"
            value={phoneNumber}
            onChange={(event) => setPhoneNumber(event.target.value)}
            placeholder="+91 9876543210"
            autoComplete="tel"
            autoFocus
          />
        </div>

        <div>
          <div className="flex items-center justify-between">
            <label className="field-label">Password</label>
            <button
              type="button"
              onClick={() => setShowPassword((current) => !current)}
              className="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-400 transition hover:text-white"
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>
          <input
            type={showPassword ? "text" : "password"}
            className="input auth-input mt-2"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter your password"
            autoComplete="current-password"
          />
        </div>
      </div>

      <AnimatedButton type="submit" loading={loading} fullWidth className="auth-button">
        {loading ? "Signing in..." : "Login"}
      </AnimatedButton>

      <div className="flex items-center justify-end gap-3 text-[14px] text-slate-400 pt-1">
        <Link to="/register" className="font-medium text-violet-300 transition hover:text-violet-200">
          Create an account
        </Link>
      </div>
    </form>
  );
}
