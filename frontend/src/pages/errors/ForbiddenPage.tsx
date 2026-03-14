import { Link } from "react-router-dom";
import DashboardCard from "../../components/ui/DashboardCard";
import AnimatedButton from "../../components/ui/AnimatedButton";

export default function ForbiddenPage() {
  return (
    <div className="premium-page min-h-screen place-content-center py-8">
      <DashboardCard compact hover={false} className="mx-auto max-w-2xl text-center">
        <p className="section-kicker">Error 403</p>
        <h1 className="section-title-premium mt-4">Access forbidden</h1>
        <p className="type-body mt-4 max-w-xl mx-auto text-slate-300">
          You do not have permission to access this page. Upgrade your plan or contact support if you believe this is a mistake.
        </p>
        <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
          <Link to="/dashboard" className="w-full sm:w-auto">
            <AnimatedButton className="w-full sm:w-auto">Go to dashboard</AnimatedButton>
          </Link>
          <Link to="/upgrade" className="w-full sm:w-auto">
            <AnimatedButton className="w-full sm:w-auto" variant="secondary">Upgrade plan</AnimatedButton>
          </Link>
        </div>
      </DashboardCard>
    </div>
  );
}