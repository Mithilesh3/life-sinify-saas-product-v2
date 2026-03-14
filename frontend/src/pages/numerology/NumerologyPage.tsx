import { motion } from "framer-motion";
import AnimatedButton from "../../components/ui/AnimatedButton";
import DashboardCard from "../../components/ui/DashboardCard";
import PageHero from "../../components/ui/PageHero";

const numerologyServices = [
  "Name Numerology Correction",
  "Business Name Numerology",
  "Mobile Number Numerology",
  "Vehicle Number Numerology",
  "House Number Numerology",
  "Signature Numerology",
];

const aiNumerologyTools = [
  {
    title: "AI Numerology Report Generator",
    copy: "Enter name and birth date to generate a detailed numerology profile with strengths, challenges, and remedies.",
  },
  {
    title: "Lucky Number Generator",
    copy: "Instantly compute your day, month, and life-path lucky numbers with practical guidance.",
  },
  {
    title: "Name Correction Tool",
    copy: "Suggest optimized spellings for personal and brand names based on numerology alignment.",
  },
];

export default function NumerologyPage() {
  return (
    <div className="premium-page">
      <PageHero
        eyebrow="Workspace / Numerology"
        title="AI-powered numerology services for modern decisions."
        description="From personal identity correction to business-number alignment, LifeSignify NumAI now supports a full numerology service stack across India."
        badges={["Vedic aligned", "AI ready", "India wide"]}
        action={<AnimatedButton>Generate Numerology Report</AnimatedButton>}
      />

      <section className="grid gap-4 xl:grid-cols-[1.02fr_0.98fr]">
        <DashboardCard
          title="Numerology Services Catalog"
          description="Premium consultations and guided corrections."
          floating
          floatDelay={0.1}
        >
          <div className="grid gap-3 sm:grid-cols-2">
            {numerologyServices.map((service) => (
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
          title="Intelligent AI Tools"
          description="Automation-first workflows for faster spiritual intelligence."
          floating
          floatDelay={0.2}
        >
          <div className="space-y-3">
            {aiNumerologyTools.map((tool) => (
              <motion.div
                key={tool.title}
                whileHover={{ y: -4, boxShadow: "0 15px 40px rgba(0, 0, 0, 0.45)" }}
                className="rounded-[14px] border border-white/10 bg-black/20 p-4"
              >
                <p className="text-[15px] font-semibold text-white">{tool.title}</p>
                <p className="type-body mt-2">{tool.copy}</p>
              </motion.div>
            ))}
          </div>
        </DashboardCard>
      </section>
    </div>
  );
}
