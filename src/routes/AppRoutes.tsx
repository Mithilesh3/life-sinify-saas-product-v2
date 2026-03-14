import { AnimatePresence } from "framer-motion";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import AppLayout from "../components/layout/AppLayout";
import PageTransition from "../components/layout/PageTransition";

import DashboardPage from "../pages/dashboard/DashboardPage";
import NumerologyPage from "../pages/numerology/NumerologyPage";
import AstrologyPage from "../pages/astrology/AstrologyPage";
import PujaRitualsPage from "../pages/puja/PujaRitualsPage";
import StorePage from "../pages/store/StorePage";
import AstrologerChatPage from "../pages/chat/AstrologerChatPage";
import ReportsListPage from "../pages/reports/ReportsListPage";
import ReportDetailPage from "../pages/reports/ReportDetailPage";
import GenerateReportPage from "../pages/reports/GenerateReportPage";

import UpgradePage from "../pages/upgrade/UpgradePage";
import BillingPage from "../pages/billing/BillingPage";
import SettingsPage from "../pages/settings/SettingsPage";

import AdminDashboard from "../pages/admin/AdminDashboard";
import AdminUsersPage from "../pages/admin/AdminUsersPage";

import LoginPage from "../pages/auth/LoginPage";
import RegisterPage from "../pages/auth/RegisterPage";

import NotFoundPage from "../pages/errors/NotFoundPage";
import ForbiddenPage from "../pages/errors/ForbiddenPage";

import ProtectedRoute from "../components/ProtectedRoute";
import ReportGuard from "../components/guards/ReportGuard";
import AdminRoute from "./AdminRoute";

const appShellPrefixes = [
  "/dashboard",
  "/numerology",
  "/astrology",
  "/puja-rituals",
  "/store",
  "/chat-with-astrologer",
  "/reports",
  "/generate-report",
  "/settings",
  "/upgrade",
  "/billing",
  "/admin",
];

export default function AppRoutes() {
  const { user, loading } = useAuth();
  const location = useLocation();

  const isAppShellRoute =
    location.pathname === "/" ||
    appShellPrefixes.some((prefix) => location.pathname.startsWith(prefix));

  const routeKey = isAppShellRoute ? "app-shell" : location.pathname;

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <div className="glass-card w-full max-w-md text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-2 border-white/20 border-t-cyan-300" />
          <h1 className="type-h2 mt-6 text-white">Loading workspace</h1>
          <p className="type-body mt-3">
            Preparing your dashboard, navigation, and authenticated session.
          </p>
        </div>
      </div>
    );
  }

  return (
    <AnimatePresence mode="wait" initial={false}>
      <PageTransition key={routeKey} className="min-h-screen">
        <Routes location={location}>
          <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
          <Route path="/register" element={user ? <Navigate to="/dashboard" replace /> : <RegisterPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="numerology" element={<NumerologyPage />} />
            <Route path="astrology" element={<AstrologyPage />} />
            <Route path="puja-rituals" element={<PujaRitualsPage />} />
            <Route path="store" element={<StorePage />} />
            <Route path="chat-with-astrologer" element={<AstrologerChatPage />} />
            <Route path="reports" element={<ReportsListPage />} />
            <Route path="reports/:id" element={<ReportDetailPage />} />
            <Route
              path="generate-report"
              element={
                <ReportGuard>
                  <GenerateReportPage />
                </ReportGuard>
              }
            />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="upgrade" element={<UpgradePage />} />
            <Route path="billing" element={<BillingPage />} />
            <Route
              path="admin"
              element={
                <AdminRoute>
                  <AdminDashboard />
                </AdminRoute>
              }
            />
            <Route
              path="admin/users"
              element={
                <AdminRoute>
                  <AdminUsersPage />
                </AdminRoute>
              }
            />
          </Route>
          <Route path="/forbidden" element={<ForbiddenPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </PageTransition>
    </AnimatePresence>
  );
}
