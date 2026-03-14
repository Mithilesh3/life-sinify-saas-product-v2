import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { pageTransition, pageTransitionVariants } from "../../utils/motion";

interface PageTransitionProps {
  children: ReactNode;
  className?: string;
}

export default function PageTransition({
  children,
  className,
}: PageTransitionProps) {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageTransitionVariants}
      transition={pageTransition}
      className={className}
    >
      {children}
    </motion.div>
  );
}
