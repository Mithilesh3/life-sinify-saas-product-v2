import { motion } from "framer-motion";
import AnimatedButton from "../../components/ui/AnimatedButton";
import DashboardCard from "../../components/ui/DashboardCard";
import PageHero from "../../components/ui/PageHero";

const chatOptions = [
  {
    title: "Live Chat with Astrologer",
    copy: "Connect to verified astrologers for real-time guidance on love, career, health, and spiritual remedies.",
    cta: "Start Chat Session",
  },
  {
    title: "Call with Astrologer",
    copy: "Book instant or scheduled voice consultations with senior Vedic experts.",
    cta: "Book Call Slot",
  },
  {
    title: "Priority Queue Access",
    copy: "Upgrade to premium support to reduce wait times and unlock dedicated astrologer sessions.",
    cta: "View Priority Plans",
  },
];

export default function AstrologerChatPage() {
  return (
    <div className="premium-page">
      <PageHero
        eyebrow="Workspace / Chat with Astrologer"
        title="Live astrologer chat and call support."
        description="Speak to verified experts instantly and combine human wisdom with AI-generated numerology and horoscope reports."
        badges={["24x7 support", "Verified astrologers", "Private and secure"]}
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {chatOptions.map((option, index) => (
          <DashboardCard key={option.title} floating floatDelay={0.08 + index * 0.08} className="flex h-full flex-col">
            <h3 className="surface-title text-white">{option.title}</h3>
            <p className="type-body mt-3 flex-1">{option.copy}</p>
            <AnimatedButton className="mt-5 w-full">{option.cta}</AnimatedButton>
          </DashboardCard>
        ))}
      </section>

      <DashboardCard title="Conversation Snapshot" description="A sample of what users can expect from astrologer-assisted guidance." floating floatDelay={0.2}>
        <div className="grid gap-3">
          <motion.div whileHover={{ y: -3 }} className="rounded-[14px] border border-white/10 bg-black/20 p-4">
            <p className="text-[12px] font-semibold tracking-[0.18em] text-cyan-300 uppercase">User</p>
            <p className="type-body mt-2 text-slate-200">
              I need guidance on career transition and the right month to launch my new business.
            </p>
          </motion.div>
          <motion.div whileHover={{ y: -3 }} className="rounded-[14px] border border-white/10 bg-black/20 p-4">
            <p className="text-[12px] font-semibold tracking-[0.18em] text-violet-300 uppercase">Astrologer</p>
            <p className="type-body mt-2 text-slate-200">
              Your chart supports expansion after the second week of next month. We should pair this with a business opening muhurat and numerology name validation.
            </p>
          </motion.div>
        </div>
      </DashboardCard>
    </div>
  );
}
