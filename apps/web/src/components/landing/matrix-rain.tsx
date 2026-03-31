"use client";

import { useEffect, useRef, useCallback } from "react";

export function MatrixRain() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>(0);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const chars =
      "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&";
    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);
    const drops: number[] = new Array(columns).fill(1);

    // Randomize initial positions
    for (let i = 0; i < drops.length; i++) {
      drops[i] = Math.floor(Math.random() * -50);
    }

    function render() {
      ctx!.fillStyle = "rgba(10, 10, 15, 0.06)";
      ctx!.fillRect(0, 0, canvas!.width, canvas!.height);

      for (let i = 0; i < drops.length; i++) {
        const char = chars[Math.floor(Math.random() * chars.length)];
        const x = i * fontSize;
        const y = drops[i] * fontSize;

        // Gradient opacity — brighter at the head
        const brightness = Math.random() * 0.15 + 0.05;
        ctx!.fillStyle = `rgba(6, 182, 212, ${brightness})`;
        ctx!.font = `${fontSize}px monospace`;
        ctx!.fillText(char, x, y);

        // Occasional bright "head" character
        if (Math.random() > 0.98) {
          ctx!.fillStyle = `rgba(6, 182, 212, 0.6)`;
          ctx!.fillText(char, x, y);
        }

        if (y > canvas!.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        drops[i]++;
      }

      animationRef.current = requestAnimationFrame(render);
    }

    render();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    handleResize();
    draw();

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animationRef.current);
    };
  }, [draw]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10 pointer-events-none"
      aria-hidden="true"
    />
  );
}