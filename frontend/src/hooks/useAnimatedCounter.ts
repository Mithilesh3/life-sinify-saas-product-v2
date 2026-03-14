import { useEffect, useRef, useState } from "react";

interface UseAnimatedCounterOptions {
  duration?: number;
  decimals?: number;
}

export function useAnimatedCounter(
  target: number,
  options: UseAnimatedCounterOptions = {}
) {
  const { duration = 900, decimals = 0 } = options;
  const [value, setValue] = useState(0);
  const previousTarget = useRef(0);

  useEffect(() => {
    if (!Number.isFinite(target)) {
      setValue(0);
      previousTarget.current = 0;
      return;
    }

    const startValue = previousTarget.current;
    const startTime = performance.now();
    let frameId = 0;

    const tick = (time: number) => {
      const progress = Math.min((time - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const nextValue = startValue + (target - startValue) * eased;
      setValue(Number(nextValue.toFixed(decimals)));

      if (progress < 1) {
        frameId = requestAnimationFrame(tick);
      } else {
        previousTarget.current = target;
      }
    };

    frameId = requestAnimationFrame(tick);

    return () => cancelAnimationFrame(frameId);
  }, [target, duration, decimals]);

  return value;
}
