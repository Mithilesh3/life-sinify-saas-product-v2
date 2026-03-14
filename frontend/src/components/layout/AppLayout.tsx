import { AnimatePresence } from "framer-motion";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import PageTransition from "./PageTransition";
import Footer from "./Footer";

export default function AppLayout() {
  const location = useLocation();

  return (
    <div className="dashboard-theme relative min-h-screen overflow-hidden">
      <div className="dashboard-cosmic-bg" aria-hidden>
        <div className="dashboard-orbit dashboard-orbit-1" />
        <div className="dashboard-orbit dashboard-orbit-2" />
        <div className="dashboard-orbit dashboard-orbit-3" />
        <span className="dashboard-num dashboard-num-3">3</span>
        <span className="dashboard-num dashboard-num-7">7</span>
        <span className="dashboard-num dashboard-num-9">9</span>
        <span className="dashboard-star dashboard-star-1" />
        <span className="dashboard-star dashboard-star-2" />
        <span className="dashboard-star dashboard-star-3" />
        <span className="dashboard-star dashboard-star-4" />
        <span className="dashboard-star dashboard-star-5" />
        <span className="dashboard-star dashboard-star-6" />
      </div>

      <div className="app-shell relative z-10 min-h-screen py-4 sm:py-5 lg:grid lg:grid-cols-[220px_minmax(0,1fr)] lg:gap-6 lg:py-6">
        <Sidebar />

        <div className="mt-4 flex min-h-0 flex-col lg:mt-0">
          <Topbar />
          <AnimatePresence mode="wait" initial={false}>
            <PageTransition key={location.pathname} className="mt-5 flex-1 sm:mt-6">
              <main className="h-full">
                <Outlet />
              </main>
            </PageTransition>
          </AnimatePresence>
        </div>
      </div>
      <Footer />
    </div>
  );
}
