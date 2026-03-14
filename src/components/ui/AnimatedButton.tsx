import { motion, type HTMLMotionProps } from "framer-motion";
import type { ReactNode } from "react";
import { cn } from "../../utils/cn";
import { buttonHover, buttonTap } from "../../utils/motion";

type AnimatedButtonProps = Omit<HTMLMotionProps<"button">, "children"> & {
  children: ReactNode;
  variant?: "primary" | "secondary" | "ghost" | "success";
  loading?: boolean;
  fullWidth?: boolean;
};

const variantClasses: Record<NonNullable<AnimatedButtonProps["variant"]>, string> = {
  primary: "premium-button",
  secondary: "premium-button-secondary",
  ghost: "premium-button-ghost",
  success: "premium-button-success",
};

export default function AnimatedButton({
  children,
  className,
  variant = "primary",
  loading = false,
  fullWidth = false,
  disabled,
  ...props
}: AnimatedButtonProps) {
  return (
    <motion.button
      whileHover={disabled ? undefined : buttonHover}
      whileTap={disabled ? undefined : buttonTap}
      disabled={disabled || loading}
      className={cn(
        variantClasses[variant],
        fullWidth && "w-full",
        (disabled || loading) && "cursor-not-allowed opacity-60",
        className
      )}
      {...props}
    >
      <span className="relative z-10 inline-flex items-center gap-2">
        {loading && (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/35 border-t-white" />
        )}
        <span>{children}</span>
      </span>
    </motion.button>
  );
}
