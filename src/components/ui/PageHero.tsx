import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { cn } from "../../utils/cn";

interface PageHeroProps {
  eyebrow: string;
  title: string;
  description: string;
  badges?: string[];
  action?: ReactNode;
  aside?: ReactNode;
  className?: string;
  titleClassName?: string;
}

const reveal = {
  duration: 0.4,
  ease: [0.22, 1, 0.36, 1] as const,
};

export default function PageHero({
  eyebrow,
  title,
  description,
  badges = [],
  action,
  aside,
  className,
  titleClassName,
}: PageHeroProps) {
  const hasRightRail = Boolean(action || aside);

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={reveal}
      className={cn("page-hero-shell", className)}
    >
      <div className="page-hero-glow" />
      <div className="page-hero-mesh" />

      <div className={cn("relative z-10 grid gap-6 sm:gap-8", hasRightRail && "xl:grid-cols-[1.1fr_0.9fr] xl:items-start")}>
        <div className="max-w-4xl">
          <p className="sidebar-label text-slate-400">{eyebrow}</p>
          <h2 className={cn("page-hero-title mt-4", titleClassName)}>{title}</h2>
          <p className="page-hero-copy mt-4 max-w-3xl">{description}</p>

          {badges.length > 0 && (
            <div className="mt-5 flex flex-wrap gap-2.5 sm:mt-6 sm:gap-3">
              {badges.map((badge) => (
                <span key={badge} className="premium-badge">
                  {badge}
                </span>
              ))}
            </div>
          )}
        </div>

        {hasRightRail && (
          <div className="flex flex-col gap-4 xl:items-stretch">
            {action && <div className="w-full xl:w-auto xl:self-end">{action}</div>}
            {aside && <div className="page-hero-aside p-4">{aside}</div>}
          </div>
        )}
      </div>
    </motion.section>
  );
}