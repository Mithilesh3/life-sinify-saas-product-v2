import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { cn } from "../../utils/cn";
import { cardHover } from "../../utils/motion";

interface DashboardCardProps {
  title?: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  hover?: boolean;
  floating?: boolean;
  floatDelay?: number;
  compact?: boolean;
}

export default function DashboardCard({
  title,
  description,
  action,
  children,
  className,
  hover = true,
  floating = false,
  floatDelay = 0,
  compact = false,
}: DashboardCardProps) {
  return (
    <motion.section
      animate={floating ? { y: [0, -4, 0] } : undefined}
      whileHover={hover ? cardHover : undefined}
      transition={{
        duration: 0.24,
        ease: "easeOut",
        y: floating
          ? {
              duration: 10,
              repeat: Infinity,
              repeatType: "mirror",
              ease: "easeInOut",
              delay: floatDelay,
            }
          : undefined,
      }}
      className={cn("premium-panel", compact && "!p-5", className)}
      style={{ willChange: "transform, box-shadow" }}
    >
      {(title || description || action) && (
        <div className={cn("flex flex-col gap-3 md:flex-row md:items-start md:justify-between", compact ? "mb-4" : "mb-5")}>
          <div>
            {title && <h3 className="surface-title text-white">{title}</h3>}
            {description && <p className="type-body mt-3 max-w-2xl">{description}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </motion.section>
  );
}