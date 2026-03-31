"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { useEffect, useRef } from "react";

const shakeVariants = [
  { shake: { x: [0, -2, 2, -1, 1, 0], transition: { duration: 0.8, repeat: Infinity, repeatType: "loop" as const, ease: "easeInOut" } } },
  { shake: { x: [0, 1.5, -1.5, 2, -2, 0], transition: { duration: 1.2, repeat: Infinity, repeatType: "loop" as const, ease: "easeInOut" } } },
  { shake: { x: [0, -1, 1, -2, 2, -1, 0], transition: { duration: 0.5, repeat: Infinity, repeatType: "loop" as const, ease: "easeInOut" } } },
  { shake: { x: [0, 2, -1, 1.5, -2, 0], transition: { duration: 1.5, repeat: Infinity, repeatType: "loop" as const, ease: "easeInOut" } } },
  { shake: { x: [0, -1.5, 1, -1, 2, -2, 0], transition: { duration: 0.7, repeat: Infinity, repeatType: "loop" as const, ease: "easeInOut" } } },
];

const getVariants = (index: number) => shakeVariants[index % shakeVariants.length];

const FuzzyWrapper = ({ children, baseIntensity = 0.3 }: { children: React.ReactNode; baseIntensity?: number }) => {
  const canvasRef = useRef<HTMLCanvasElement & { cleanupFuzzy?: () => void }>(null);
  const svgContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let animationFrameId: number;
    let isCancelled = false;
    const canvas = canvasRef.current;
    const svgContainer = svgContainerRef.current;
    if (!canvas || !svgContainer) return;
    if (canvas.cleanupFuzzy) canvas.cleanupFuzzy();

    const init = async () => {
      if (isCancelled) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      const svgElement = svgContainer.querySelector("svg");
      if (!svgElement) return;
      await new Promise((resolve) => setTimeout(resolve, 100));
      const svgRect = svgElement.getBoundingClientRect();
      const svgWidth = svgRect.width || 800;
      const svgHeight = svgRect.height || 232;
      const offscreen = document.createElement("canvas");
      const offCtx = offscreen.getContext("2d");
      if (!offCtx) return;
      offscreen.width = svgWidth;
      offscreen.height = svgHeight;

      const convertSvgToCanvas = () =>
        new Promise<void>((resolve) => {
          const svgData = new XMLSerializer().serializeToString(svgElement);
          const img = new Image();
          const svgBlob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
          const url = URL.createObjectURL(svgBlob);
          img.onload = () => {
            offCtx.clearRect(0, 0, offscreen.width, offscreen.height);
            offCtx.drawImage(img, 0, 0, svgWidth, svgHeight);
            URL.revokeObjectURL(url);
            resolve();
          };
          img.src = url;
        });

      const horizontalMargin = 50;
      const verticalMargin = 50;
      canvas.width = svgWidth + horizontalMargin * 2;
      canvas.height = svgHeight + verticalMargin * 2;
      const fuzzRange = 20;

      const run = async () => {
        if (isCancelled) return;
        await convertSvgToCanvas();
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.translate(horizontalMargin, verticalMargin);
        for (let j = 0; j < svgHeight; j++) {
          const dx = Math.floor(baseIntensity * (Math.random() - 0.5) * fuzzRange);
          ctx.drawImage(offscreen, 0, j, svgWidth, 1, dx, j, svgWidth, 1);
        }
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        animationFrameId = window.requestAnimationFrame(run);
      };
      run();
      canvas.cleanupFuzzy = () => window.cancelAnimationFrame(animationFrameId);
    };
    init();
    return () => {
      isCancelled = true;
      window.cancelAnimationFrame(animationFrameId);
      if (canvas?.cleanupFuzzy) canvas.cleanupFuzzy();
    };
  }, [baseIntensity]);

  return (
    <div className="relative">
      <div ref={svgContainerRef} className="absolute inset-0 opacity-0 pointer-events-none" style={{ zIndex: -1 }}>
        {children}
      </div>
      <canvas ref={canvasRef} style={{ display: "block" }} />
    </div>
  );
};

export function Glitchy404({ width = 600, height = 170, color = "#06b6d4" }: { width?: number; height?: number; color?: string }) {
  // Simplified 404 SVG paths
  const pathGroups = [
    "M28.364 12.4511V10.8261H25.926V9.95106L23.814 10.0511V18.6511H25.926C25.926 18.6881 28.364 18.7131 28.364 18.7131V13.1511H25.926V12.4511H28.364Z",
    "M26.309 4.62V9.795H23.871V10.308L21.758 10.408V6.082L17.208 10.633L10.445 10.958L10.545 10.858C10.57 10.858 10.57 10.67 10.57 10.67H15.058V9.795H11.608L14.183 7.22H11.02V5.295H18.32V4.007H17.401L18.538 2.87H22.401V1.882H19.521L19.571 1.832C20.123 1.279 20.826 0.902 21.592 0.749 22.357 0.595 23.151 0.673 23.873 0.972 24.595 1.27 25.212 1.776 25.645 2.426 26.079 3.075 26.31 3.839 26.309 4.62Z",
    "M64.324 7.022V8.334L59.774 8.547V8.46L59.674 8.56L57.461 8.66V7.597H54.186L56.561 5.234H41.973C41.47 5.234 40.986 5.434 40.63 5.79 40.274 6.147 40.073 6.63 40.073 7.134V9.522L35.523 9.735V7.022C35.526 5.338 36.196 3.725 37.386 2.534 38.576 1.344 40.19 0.674 41.873 0.672H57.973C59.24 0.677 60.476 1.059 61.524 1.769 62.573 2.479 63.386 3.485 63.861 4.659H57.461V6.084H64.224C64.282 6.393 64.316 6.707 64.324 7.022Z",
    "M64.419 19.138V22.451C64.418 23.335 64.231 24.208 63.869 25.014H54.597V25.826H63.435C62.865 26.735 62.073 27.484 61.135 28.004 60.196 28.524 59.141 28.798 58.068 28.8H47.03V27.214H41.13C42.101 27.896 43.257 28.267 44.443 28.276H39.067V27.214H37.817C37.13 26.624 36.578 25.894 36.199 25.072 35.819 24.25 35.621 23.356 35.617 22.451V18.5L40.168 18.55V21.025L42.618 18.575L48.98 18.65L43.397 24.239H57.956C58.462 24.24 58.947 24.04 59.305 23.684 59.664 23.328 59.866 22.844 59.869 22.339V18.789L62.144 18.814V19.139L64.419 19.138Z",
  ];

  return (
    <FuzzyWrapper baseIntensity={0.4}>
      <svg width={width} height={height} viewBox="0 0 100 29" fill={color} xmlns="http://www.w3.org/2000/svg">
        {pathGroups.map((d, i) => (
          <motion.g key={i} variants={getVariants(i)} animate="shake" transition={{ delay: Math.random() * 2 }}>
            <path d={d} fill={color} />
          </motion.g>
        ))}
        {/* Center "0" */}
        <motion.g variants={getVariants(4)} animate="shake" transition={{ delay: Math.random() * 2 }}>
          <path d="M12.5 10.6L9.988 13.114H11.813V13.727H0V15.214H7.888L5.138 17.964C4.991 18.111 4.858 18.27 4.738 18.439L11.026 18.514L19.264 10.276L12.5 10.6Z" fill={color} />
        </motion.g>
        {/* Second "4" parts */}
        <motion.g variants={getVariants(0)} animate="shake" transition={{ delay: Math.random() * 2 }}>
          <path d="M93.51 4.228V6.891L91.773 6.978V6.778H88.96V6.078L88.26 6.778H86.399V7.241L81.099 7.503L82.049 6.553H80.859V5.891H82.71L83.235 5.366H88.51V4.653H83.947L86.772 1.828C87.325 1.278 88.028 0.903 88.793 0.749 89.557 0.596 90.35 0.671 91.072 0.966 91.952 1.333 92.667 2.009 93.085 2.866H88.022V4.003H93.46C93.471 4.077 93.476 4.152 93.473 4.228H93.51Z" fill={color} />
        </motion.g>
        <motion.g variants={getVariants(2)} animate="shake" transition={{ delay: Math.random() * 2 }}>
          <path d="M98.021 23.386V22.723H94.897V21.748H96.522V22.636H98.222V21.723H98.022V20.235H93.608V19.173L89.058 19.123V20.235H74.219L75.482 18.96L69.532 18.898C69.329 19.381 69.222 19.9 69.219 20.423V20.835C69.221 21.883 69.638 22.886 70.378 23.627 71.118 24.367 72.122 24.784 73.169 24.786H89.058V27.211H90.983V27.948H89.058V28.798H93.608V24.786H94.897V25.136H99.285V23.386H98.021ZM89.183 23.536H81.632V22.723H89.183V23.536ZM92.933 21.748H86.497V21.023H92.935L92.933 21.748ZM96.52 24.548H96.27V23.536H96.52V24.548Z" fill={color} />
        </motion.g>
        <motion.g variants={getVariants(3)} animate="shake" transition={{ delay: Math.random() * 2 }}>
          <path d="M66.377 11.964V7.976L61.827 8.189V19.114L64.102 19.139V18.652H66.377V13.914H64.4V11.964H66.377Z" fill={color} />
        </motion.g>
        <motion.g variants={getVariants(1)} animate="shake" transition={{ delay: Math.random() * 2 }}>
          <path d="M80.4 16.327L89.5 7.239H88.45V6.889L83.15 7.151L81.763 8.539H83.225V9.964H81.054L81.542 9.476H75.491V10.801H79.5L77.187 13.114H79.238V14.727H76.3L77.3 13.727H74.579V15.214H75.091L72.341 17.964C71.981 18.328 71.693 18.757 71.491 19.227L77.441 19.289L79.154 17.577H77.6V16.327H80.4Z" fill={color} />
        </motion.g>
        <motion.g variants={getVariants(4)} animate="shake" transition={{ delay: Math.random() * 2 }}>
          <path d="M94.363 17.877V18.652H92.205V17.577H95.567V6.539L93.83 6.626V7.239H91.017V19.452L95.567 19.502V18.864H97.08V17.877H94.363Z" fill={color} />
        </motion.g>
      </svg>
    </FuzzyWrapper>
  );
}