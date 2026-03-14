import { motion } from "framer-motion";
import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import AnimatedButton from "../ui/AnimatedButton";
import { useAuth } from "../../context/AuthContext";
import { cn } from "../../utils/cn";

const navItems = [
  { label: "Dashboard", path: "/dashboard", hint: "Overview" },
  { label: "Numerology", path: "/numerology", hint: "Services" },
  { label: "Astrology", path: "/astrology", hint: "Predictions" },
  { label: "Puja & Rituals", path: "/puja-rituals", hint: "Muhurat" },
  { label: "Store", path: "/store", hint: "Products" },
  { label: "Reports", path: "/reports", hint: "Library" },
  { label: "Chat with Astrologer", path: "/chat-with-astrologer", hint: "Live support" },
  { label: "Billing", path: "/billing", hint: "Plans" },
  { label: "Settings", path: "/settings", hint: "Workspace" },
];

export default function Sidebar() {
  const location = useLocation();
  const { user, logout } = useAuth();
  const [loggingOut, setLoggingOut] = useState(false);

  const currentPlan =
    user?.subscription?.plan_name?.toUpperCase() ||
    user?.organization?.plan?.toUpperCase() ||
    "BASIC";

  const showAdminLink = user?.role === "admin" || user?.role === "super_admin";

  const handleLogout = async () => {
    if (loggingOut) return;
    setLoggingOut(true);
    await logout();
  };

  const renderLink = (path: string, label: string, hint: string) => {
    const isActive = location.pathname.startsWith(path);

    return (
      <motion.div
        key={path}
        whileHover={{ x: 4 }}
        whileTap={{ scale: 0.995 }}
        transition={{ duration: 0.18 }}
        className="relative"
      >
        {isActive && (
          <motion.span
            layoutId="sidebar-active-card"
            className="absolute inset-0 rounded-[12px] border-l-[3px] border-indigo-500 bg-[rgba(99,102,241,0.15)] shadow-[0_10px_24px_rgba(15,23,42,0.32),0_0_18px_rgba(99,102,241,0.18)]"
            transition={{ type: "spring", bounce: 0.18, duration: 0.36 }}
          />
        )}

        <Link to={path} className={cn("sidebar-item", isActive && "sidebar-item-active text-white") }>
          <span
            className={cn(
              "relative z-10 h-2.5 w-2.5 rounded-full transition",
              isActive ? "bg-cyan-300 shadow-[0_0_18px_rgba(103,232,249,0.45)]" : "bg-slate-600"
            )}
          />

          <div className="relative z-10 min-w-0 flex-1">
            <p className="truncate text-[14px] font-medium text-inherit">{label}</p>
            <p className="sidebar-label mt-1 hidden truncate text-slate-500 lg:block">{hint}</p>
          </div>
        </Link>
      </motion.div>
    );
  };

  return (
    <motion.aside
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
      className="lg:sticky lg:top-8"
    >
      <div className="sidebar-shell flex h-full flex-col gap-5 sm:gap-6 lg:gap-8">
        <div className="flex items-start justify-between gap-4 lg:block">
          <div>
            <Link to="/dashboard" className="inline-block">
              <span className="type-h2 hero-gradient-text">LifeSignify</span>
            </Link>
            <p className="sidebar-label mt-2 text-slate-500">NumAI Dashboard</p>
            <p className="type-body mt-3 hidden max-w-[18rem] text-slate-400 sm:block">
              Reports, billing, and workspace controls in one refined numerology dashboard.
            </p>
          </div>

          <div className="flex shrink-0 flex-col items-end gap-2 lg:hidden">
            <span className="premium-badge">{currentPlan}</span>
            <span className="premium-badge capitalize">{user?.role ?? "member"}</span>
          </div>
        </div>

        <div className="sidebar-panel-note hidden p-4 lg:block">
          <p className="sidebar-label text-slate-500">Current plan</p>
          <div className="mt-3 flex items-center justify-between gap-3">
            <p className="type-h3 text-white">{currentPlan}</p>
            <span className="premium-badge">Live</span>
          </div>
          <p className="type-body mt-3 break-words text-slate-400">
            {user?.organization?.name ?? user?.email}
          </p>
        </div>

        <nav className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-1">
          {navItems.map((item) => renderLink(item.path, item.label, item.hint))}
          {showAdminLink && renderLink("/admin", "Admin", "Operations")}
        </nav>

        <div className="mt-auto grid gap-3 sm:grid-cols-[1fr_auto] lg:grid-cols-1">
          <div className="sidebar-panel-note hidden p-4 md:block lg:block">
            <p className="sidebar-label text-slate-500">Signed in</p>
            <p className="type-body mt-3 break-all text-slate-200">{user?.email}</p>
            <div className="mt-3 flex items-center justify-between gap-3">
              <p className="text-[15px] font-medium capitalize text-slate-400">{user?.role ?? "member"}</p>
              <span className="premium-badge">Secure</span>
            </div>
          </div>

          <AnimatedButton variant="ghost" fullWidth loading={loggingOut} className="sm:min-w-[148px] lg:w-full" onClick={handleLogout}>
            {loggingOut ? "Signing out..." : "Logout"}
          </AnimatedButton>
        </div>
      </div>
    </motion.aside>
  );
}
