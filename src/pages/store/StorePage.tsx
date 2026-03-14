import { motion } from "framer-motion";
import AnimatedButton from "../../components/ui/AnimatedButton";
import DashboardCard from "../../components/ui/DashboardCard";
import PageHero from "../../components/ui/PageHero";

type ProductItem = {
  name: string;
  description: string;
  price: string;
  image: string;
};

type ProductCategory = {
  title: string;
  items: ProductItem[];
};

const productCatalog: ProductCategory[] = [
  {
    title: "Rudraksha",
    items: [
      { name: "1 Mukhi Rudraksha", description: "Focused spiritual clarity and authority alignment.", price: "₹4,999", image: "1M" },
      { name: "5 Mukhi Rudraksha", description: "Daily balance and calm-energy support.", price: "₹1,299", image: "5M" },
      { name: "7 Mukhi Rudraksha", description: "Prosperity and stability vibrations.", price: "₹2,199", image: "7M" },
      { name: "9 Mukhi Rudraksha", description: "Protection and courage activation.", price: "₹3,199", image: "9M" },
      { name: "Rudraksha Mala", description: "Classic mala for mantra practice and focus.", price: "₹1,599", image: "M" },
      { name: "Rudraksha Bracelet", description: "Wearable daily spiritual alignment.", price: "₹999", image: "RB" },
    ],
  },
  {
    title: "Gemstones",
    items: [
      { name: "Blue Sapphire (Neelam)", description: "Saturn strength and discipline support.", price: "₹7,999", image: "💎" },
      { name: "Yellow Sapphire (Pukhraj)", description: "Wisdom and prosperity enhancement.", price: "₹6,499", image: "💛" },
      { name: "Emerald (Panna)", description: "Communication and intellect clarity.", price: "₹5,299", image: "💚" },
      { name: "Ruby (Manik)", description: "Confidence and leadership energy.", price: "₹8,299", image: "❤️" },
      { name: "Coral (Moonga)", description: "Vitality and action focus.", price: "₹3,899", image: "🪸" },
      { name: "Pearl (Moti)", description: "Emotional calm and lunar balance.", price: "₹2,999", image: "🤍" },
    ],
  },
  {
    title: "Spiritual Products",
    items: [
      { name: "Shree Yantra", description: "Abundance and sacred geometry activation.", price: "₹1,799", image: "🔺" },
      { name: "Kubera Yantra", description: "Wealth attraction and growth intent.", price: "₹1,499", image: "🪙" },
      { name: "Navgraha Yantra", description: "Planetary harmony balancing aid.", price: "₹2,099", image: "☀️" },
      { name: "Vastu Yantra", description: "Space-energy alignment for homes and offices.", price: "₹1,599", image: "🧭" },
    ],
  },
  {
    title: "Bracelets",
    items: [
      { name: "Money Magnet Bracelet", description: "Abundance-oriented energetic reminder.", price: "₹1,199", image: "💰" },
      { name: "Zodiac Bracelet", description: "Sign-tuned wearable guidance band.", price: "₹1,099", image: "♈" },
      { name: "Navgraha Bracelet", description: "9-planet balancing bracelet.", price: "₹1,699", image: "🪐" },
      { name: "Protection Bracelet", description: "Daily grounding and protection support.", price: "₹1,299", image: "🛡️" },
    ],
  },
];

export default function StorePage() {
  return (
    <div className="premium-page">
      <PageHero
        eyebrow="Workspace / Store"
        title="Spiritual products and remedies marketplace."
        description="A curated Vedic store for Rudraksha, gemstones, yantras, and bracelets with quick-buy actions and trusted quality context."
        badges={["Spiritual products", "Gemstones", "Rudraksha"]}
      />

      <section className="space-y-4">
        {productCatalog.map((category, categoryIndex) => (
          <DashboardCard
            key={category.title}
            title={category.title}
            description={`${category.items.length} curated products`}
            floating
            floatDelay={0.08 + categoryIndex * 0.06}
          >
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {category.items.map((product) => (
                <motion.article
                  key={product.name}
                  whileHover={{ y: -4, boxShadow: "0 15px 40px rgba(0, 0, 0, 0.45)" }}
                  className="rounded-[14px] border border-white/10 bg-black/20 p-4"
                >
                  <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/40 to-cyan-400/40 text-base font-bold text-white">
                    {product.image}
                  </div>
                  <h3 className="text-[15px] font-semibold text-white">{product.name}</h3>
                  <p className="type-body mt-2">{product.description}</p>
                  <div className="mt-3 flex items-center justify-between gap-3">
                    <p className="text-[15px] font-bold text-cyan-200">{product.price}</p>
                    <AnimatedButton className="!px-3 !py-2 text-[12px]">Buy Now</AnimatedButton>
                  </div>
                </motion.article>
              ))}
            </div>
          </DashboardCard>
        ))}
      </section>
    </div>
  );
}
