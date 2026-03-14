import { motion, useReducedMotion } from "framer-motion";
import ParticleField from "./ParticleField";
import { cn } from "../../utils/cn";

interface AmbientBackgroundProps {
  className?: string;
  fixed?: boolean;
  withParticles?: boolean;
  particleCount?: number;
}

const orbTransitions = [20, 24, 28, 32];
const orbAnimations = [
  { x: [0, 56, -18, 0], y: [0, -42, 18, 0], scale: [1, 1.08, 0.96, 1] },
  { x: [0, -48, 20, 0], y: [0, 36, -18, 0], scale: [1, 1.12, 0.94, 1] },
  { x: [0, 34, -28, 0], y: [0, 28, -22, 0], scale: [1, 1.06, 0.98, 1] },
  { x: [0, -30, 24, 0], y: [0, -24, 30, 0], scale: [1, 1.04, 0.95, 1] },
];

const ribbonAnimations = [
  { x: [0, 38, -12, 0], y: [0, -18, 14, 0], opacity: [0.34, 0.48, 0.3, 0.34] },
  { x: [0, -32, 20, 0], y: [0, 20, -16, 0], opacity: [0.28, 0.4, 0.26, 0.28] },
];

export default function AmbientBackground({
  className,
  fixed = false,
  withParticles = false,
  particleCount = 18,
}: AmbientBackgroundProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <div className={cn("ambient-shell", fixed && "ambient-shell-fixed", className)} aria-hidden>
      {orbAnimations.map((animation, index) => (
        <motion.div
          key={index}
          className={cn("ambient-orb", `ambient-orb-${index + 1}`)}
          animate={prefersReducedMotion ? undefined : animation}
          transition={
            prefersReducedMotion
              ? undefined
              : {
                  duration: orbTransitions[index],
                  repeat: Infinity,
                  repeatType: "mirror",
                  ease: "easeInOut",
                }
          }
        />
      ))}

      {ribbonAnimations.map((animation, index) => (
        <motion.div
          key={`ribbon-${index}`}
          className={cn("ambient-ribbon", `ambient-ribbon-${index + 1}`)}
          animate={prefersReducedMotion ? undefined : animation}
          transition={
            prefersReducedMotion
              ? undefined
              : {
                  duration: 22 + index * 6,
                  repeat: Infinity,
                  repeatType: "mirror",
                  ease: "easeInOut",
                }
          }
        />
      ))}

      <div className="ambient-grid" />
      {withParticles && <ParticleField count={particleCount} />}
      <div className="ambient-vignette" />
    </div>
  );
}
