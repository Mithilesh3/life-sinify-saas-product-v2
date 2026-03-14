import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import AnimatedButton from "../../components/ui/AnimatedButton";
import DashboardCard from "../../components/ui/DashboardCard";
import PageHero from "../../components/ui/PageHero";

const astrologyServices = [
  "Birth Chart Analysis",
  "Kundli Matching",
  "Career Prediction",
  "Love and Relationship Prediction",
  "Health Astrology",
  "Wealth Prediction",
];

const premiumAstroFeatures = [
  "Live Astrologer Chat",
  "Compatibility Calculator (Love, Marriage, Business)",
  "AI Birth Chart Reader",
];

export default function AstrologyPage() {
  const navigate = useNavigate();

  return (
    <div className="premium-page">
      <PageHero
        eyebrow="Workspace / Astrology"
        title="Vedic astrology intelligence with real-time expert support."
        description="Move from static horoscope content to actionable guidance using AI-driven chart reading and astrologer-assisted interpretation."
        badges={["Birth chart AI", "Kundli insights", "Live astrologers"]}
        action={
          <AnimatedButton onClick={() => navigate("/chat-with-astrologer")}>
            Chat with Astrologer
          </AnimatedButton>
        }
      />

      <section className="grid gap-4 xl:grid-cols-[1.02fr_0.98fr]">
        <DashboardCard
          title="Astrology Services Catalog"
          description="Consultation and prediction modules."
          floating
          floatDelay={0.1}
        >
          <div className="grid gap-3 sm:grid-cols-2">
            {astrologyServices.map((service) => (
              <motion.div
                key={service}
                whileHover={{ y: -4, boxShadow: "0 15px 40px rgba(0, 0, 0, 0.45)" }}
                className="rounded-[14px] border border-white/10 bg-black/20 p-4"
              >
                <p className="text-[15px] font-semibold text-white">{service}</p>
              </motion.div>
            ))}
          </div>
        </DashboardCard>

        <DashboardCard
          title="Premium Astrology Features"
          description="AI + human hybrid platform capabilities."
          floating
          floatDelay={0.2}
        >
          <div className="space-y-3">
            {premiumAstroFeatures.map((feature) => (
              <motion.div
                key={feature}
                whileHover={{ y: -4, boxShadow: "0 15px 40px rgba(0, 0, 0, 0.45)" }}
                className="rounded-[14px] border border-white/10 bg-black/20 p-4"
              >
                <p className="text-[15px] font-semibold text-white">{feature}</p>
              </motion.div>
            ))}
          </div>
        </DashboardCard>
      </section>
    </div>
  );
}
