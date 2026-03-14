import { motion } from "framer-motion";
import { useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const routeMeta = {
  dashboard: {
    title: "Executive Dashboard",
    subtitle: "Metrics, report activity, and insight trends in one place.",
  },
  numerology: {
    title: "Numerology Services",
    subtitle: "AI-powered numerology correction, naming, and lucky-number tools.",
  },
  astrology: {
    title: "Astrology Services",
    subtitle: "Vedic astrology predictions, birth-chart analysis, and compatibility modules.",
  },
  puja: {
    title: "Puja and Rituals",
    subtitle: "Muhurat services and Vedic ritual support for important life milestones.",
  },
  store: {
    title: "Spiritual Store",
    subtitle: "Rudraksha, gemstones, yantras, and bracelets with premium product presentation.",
  },
  chat: {
    title: "Chat with Astrologer",
    subtitle: "Connect via live chat or call for instant expert guidance.",
  },
  reports: {
    title: "Reports Library",
    subtitle: "Review generated intelligence reports with a cleaner, structured layout.",
  },
  billing: {
    title: "Subscription and Billing",
    subtitle: "Compare plans, review payments, and manage upgrades.",
  },
  settings: {
    title: "Workspace Settings",
    subtitle: "Organization context and account details in one consistent surface.",
  },
  admin: {
    title: "Admin Overview",
    subtitle: "Operational metrics and organization control for administrators.",
  },
} as const;

function resolveRouteKey(pathname: string): keyof typeof routeMeta {
  if (pathname.startsWith("/numerology")) return "numerology";
  if (pathname.startsWith("/astrology")) return "astrology";
  if (pathname.startsWith("/puja-rituals")) return "puja";
  if (pathname.startsWith("/store")) return "store";
  if (pathname.startsWith("/chat-with-astrologer")) return "chat";
  if (pathname.startsWith("/reports")) return "reports";
  if (pathname.startsWith("/billing")) return "billing";
  if (pathname.startsWith("/settings")) return "settings";
  if (pathname.startsWith("/admin")) return "admin";
  return "dashboard";
}

export default function Topbar() {
  const location = useLocation();
  const { user } = useAuth();
  const routeKey = resolveRouteKey(location.pathname);
  const meta = routeMeta[routeKey];
  const today = new Intl.DateTimeFormat(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  }).format(new Date());

  return (
    <motion.header initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }}>
      <div className="topbar-shell flex flex-col gap-4 sm:gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0">
          <p className="sidebar-label text-slate-500">Workspace / {routeKey}</p>
          <h1 className="workspace-title mt-2 sm:mt-3">{meta.title}</h1>
          <p className="type-body mt-2 hidden max-w-2xl sm:block sm:mt-3">{meta.subtitle}</p>
        </div>

        <div className="flex w-full items-center justify-between gap-3 sm:w-auto sm:justify-start lg:self-auto">
          <span className="premium-badge hidden md:inline-flex">{today}</span>
          <div className="glass-card flex min-w-0 items-center gap-3 rounded-full px-3 py-2 sm:px-3.5 sm:py-2.5">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 via-indigo-400 to-violet-500 text-sm font-medium text-white">
              {user?.email?.slice(0, 1).toUpperCase() ?? "U"}
            </div>
            <div className="min-w-0">
              <p className="truncate text-[14px] font-medium text-white">
                {user?.organization?.name ?? "Workspace"}
              </p>
              <p className="sidebar-label mt-1 hidden truncate text-slate-500 md:block">{user?.email}</p>
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
}
