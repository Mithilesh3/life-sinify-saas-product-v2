import { motion } from "framer-motion";
import { useAnimatedCounter } from "../../hooks/useAnimatedCounter";
import { cn } from "../../utils/cn";
import { cardHover } from "../../utils/motion";

interface StatCardProps {
  label: string;
  value: number | string;
  suffix?: string;
  prefix?: string;
  detail?: string;
  className?: string;
  floatDelay?: number;
  compact?: boolean;
}

export default function StatCard({
  label,
  value,
  suffix = "",
  prefix = "",
  detail,
  className,
  floatDelay = 0,
  compact = false,
}: StatCardProps) {
  const numericTarget = typeof value === "number" ? value : Number.NaN;
  const animatedValue = useAnimatedCounter(Number.isFinite(numericTarget) ? numericTarget : 0);
  const displayValue = typeof value === "number" ? `${prefix}${animatedValue}${suffix}` : value;

  return (
    <motion.div
      animate={{ y: [0, -4, 0] }}
      whileHover={cardHover}
      transition={{
        duration: 0.24,
        ease: "easeOut",
        y: {
          duration: 9,
          repeat: Infinity,
          repeatType: "mirror",
          ease: "easeInOut",
          delay: floatDelay,
        },
      }}
      className={cn("stat-card", compact && "!p-4", className)}
      style={{ willChange: "transform, box-shadow" }}
    >
      <p className="stat-label">{label}</p>
      <p className={cn("stat-value", compact && "mt-2 text-[28px]")}>{displayValue}</p>
      {detail && <p className="type-body mt-3">{detail}</p>}
    </motion.div>
  );
}