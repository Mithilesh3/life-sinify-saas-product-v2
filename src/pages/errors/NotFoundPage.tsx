import { Link } from "react-router-dom";
import DashboardCard from "../../components/ui/DashboardCard";
import AnimatedButton from "../../components/ui/AnimatedButton";

export default function NotFoundPage() {
  return (
    <div className="premium-page min-h-screen place-content-center py-8">
      <DashboardCard compact hover={false} className="mx-auto max-w-xl text-center">
        <p className="section-kicker">Error 404</p>
        <h1 className="section-title-premium mt-4">Page not found</h1>
        <p className="type-body mt-4 max-w-md mx-auto text-slate-300">
          The page you are looking for does not exist or may have been moved.
        </p>
        <div className="mt-6 flex justify-center">
          <Link to="/dashboard">
            <AnimatedButton>Back to dashboard</AnimatedButton>
          </Link>
        </div>
      </DashboardCard>
    </div>
  );
}