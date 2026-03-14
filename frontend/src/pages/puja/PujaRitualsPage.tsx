import { motion } from "framer-motion";
import DashboardCard from "../../components/ui/DashboardCard";
import PageHero from "../../components/ui/PageHero";

const muhuratServices = [
  "Marriage Muhurat",
  "Griha Pravesh Muhurat",
  "Naamkaran Muhurat",
  "Mundan Muhurat",
  "Car/Bike Muhurat",
  "Bhoomi Pujan Muhurat",
  "Business Opening Muhurat",
];

const vedicRitualServices = [
  "Maha Mrityunjaya Jaap",
  "Rudra Abhishek",
  "Navgraha Shanti",
  "Pitru Dosh Puja",
  "Kaal Sarp Dosh Puja",
  "Manglik Dosh Puja",
];

export default function PujaRitualsPage() {
  return (
    <div className="premium-page">
      <PageHero
        eyebrow="Workspace / Puja and Rituals"
        title="Muhurat and Vedic ritual services with structured guidance."
        description="Book auspicious timing and remedy rituals with clear intent notes, preparation checklists, and astrological context."
        badges={["Muhurat ready", "Remedy rituals", "Trusted process"]}
      />

      <section className="grid gap-4 xl:grid-cols-2">
        <DashboardCard
          title="Muhurat Services"
          description="Auspicious timing services for key life events."
          floating
          floatDelay={0.1}
        >
          <div className="grid gap-3">
            {muhuratServices.map((service) => (
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
          title="Vedic Ritual Services"
          description="Spiritual remedies for doshas and life-balance alignment."
          floating
          floatDelay={0.2}
        >
          <div className="grid gap-3">
            {vedicRitualServices.map((service) => (
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
      </section>
    </div>
  );
}
