import { cn } from "../../utils/cn";

interface SkeletonProps {
  className?: string;
}

export default function Skeleton({ className }: SkeletonProps) {
  return <div className={cn("loading-shimmer rounded-2xl", className)} />;
}
