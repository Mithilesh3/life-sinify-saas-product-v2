export const pageTransitionVariants = {
  initial: { opacity: 0, y: 20, scale: 0.995, filter: "blur(8px)" },
  animate: { opacity: 1, y: 0, scale: 1, filter: "blur(0px)" },
  exit: { opacity: 0, y: -12, scale: 0.992, filter: "blur(6px)" },
};

export const pageTransition = {
  duration: 0.4,
  ease: [0.22, 1, 0.36, 1] as const,
};

export const cardHover = {
  y: -4,
  boxShadow: "0 15px 40px rgba(0, 0, 0, 0.45)",
};

export const buttonTap = { scale: 0.98 };
export const buttonHover = { y: -2, boxShadow: "0 10px 25px rgba(147, 51, 234, 0.5)" };
