import { useEffect, useRef } from "react";
import { useReducedMotion } from "framer-motion";
import { cn } from "../../utils/cn";

interface ParticleFieldProps {
  className?: string;
  count?: number;
}

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  alpha: number;
}

export default function ParticleField({
  className,
  count = 24,
}: ParticleFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const context = canvas.getContext("2d");
    if (!context) return;

    let frameId = 0;
    let width = 0;
    let height = 0;
    let particles: Particle[] = [];
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    const createParticle = (): Particle => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.18,
      vy: (Math.random() - 0.5) * 0.18,
      radius: Math.random() * 1.8 + 0.8,
      alpha: Math.random() * 0.45 + 0.12,
    });

    const resize = () => {
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.max(1, Math.floor(width * dpr));
      canvas.height = Math.max(1, Math.floor(height * dpr));
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      particles = Array.from({ length: count }, createParticle);
    };

    const drawParticles = () => {
      context.clearRect(0, 0, width, height);

      for (const particle of particles) {
        particle.x += particle.vx;
        particle.y += particle.vy;

        if (particle.x < -20) particle.x = width + 20;
        if (particle.x > width + 20) particle.x = -20;
        if (particle.y < -20) particle.y = height + 20;
        if (particle.y > height + 20) particle.y = -20;
      }

      for (let index = 0; index < particles.length; index += 1) {
        const particle = particles[index];

        context.beginPath();
        context.fillStyle = `rgba(154, 216, 255, ${particle.alpha})`;
        context.shadowBlur = 18;
        context.shadowColor = "rgba(102, 182, 255, 0.24)";
        context.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        context.fill();
        context.closePath();

        for (let innerIndex = index + 1; innerIndex < particles.length; innerIndex += 1) {
          const nextParticle = particles[innerIndex];
          const deltaX = particle.x - nextParticle.x;
          const deltaY = particle.y - nextParticle.y;
          const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

          if (distance < 120) {
            context.beginPath();
            context.strokeStyle = `rgba(109, 196, 255, ${(1 - distance / 120) * 0.12})`;
            context.lineWidth = 1;
            context.moveTo(particle.x, particle.y);
            context.lineTo(nextParticle.x, nextParticle.y);
            context.stroke();
            context.closePath();
          }
        }
      }
    };

    const render = () => {
      drawParticles();
      frameId = window.requestAnimationFrame(render);
    };

    resize();
    drawParticles();

    if (!prefersReducedMotion) {
      frameId = window.requestAnimationFrame(render);
    }

    window.addEventListener("resize", resize);

    return () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("resize", resize);
    };
  }, [count, prefersReducedMotion]);

  return <canvas ref={canvasRef} className={cn("particle-canvas", className)} aria-hidden />;
}
