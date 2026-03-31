"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import createGlobe from "cobe";

interface CyberMarker {
  id: string;
  location: [number, number];
  label: string;
}

interface CyberArc {
  id: string;
  from: [number, number];
  to: [number, number];
}

interface GlobeCyberProps {
  markers?: CyberMarker[];
  arcs?: CyberArc[];
  className?: string;
  speed?: number;
}

const defaultMarkers: CyberMarker[] = [
  { id: "ind-mum", location: [19.08, 72.88], label: "Mumbai" },
  { id: "ind-del", location: [28.61, 77.21], label: "Delhi" },
  { id: "ind-blr", location: [12.97, 77.59], label: "Bangalore" },
  { id: "ind-chn", location: [13.08, 80.27], label: "Chennai" },
  { id: "ind-hyd", location: [17.39, 78.49], label: "Hyderabad" },
  { id: "cn-bej", location: [39.91, 116.40], label: "Beijing" },
  { id: "ru-mos", location: [55.76, 37.62], label: "Moscow" },
  { id: "ng-lag", location: [6.45, 3.39], label: "Lagos" },
  { id: "us-nyc", location: [40.71, -74.01], label: "New York" },
  { id: "ir-teh", location: [35.69, 51.39], label: "Tehran" },
];

const defaultArcs: CyberArc[] = [
  { id: "atk-1", from: [39.91, 116.40], to: [19.08, 72.88] },
  { id: "atk-2", from: [55.76, 37.62], to: [28.61, 77.21] },
  { id: "atk-3", from: [6.45, 3.39], to: [13.08, 80.27] },
  { id: "atk-4", from: [40.71, -74.01], to: [12.97, 77.59] },
  { id: "atk-5", from: [35.69, 51.39], to: [17.39, 78.49] },
  { id: "atk-6", from: [39.91, 116.40], to: [28.61, 77.21] },
];

export function GlobeCyber({
  markers = defaultMarkers,
  arcs = defaultArcs,
  className = "",
  speed = 0.002,
}: GlobeCyberProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pointerInteracting = useRef<{ x: number; y: number } | null>(null);
  const dragOffset = useRef({ phi: 0, theta: 0 });
  const phiOffsetRef = useRef(0);
  const thetaOffsetRef = useRef(0);
  const isPausedRef = useRef(false);
  const [threats, setThreats] = useState(() =>
    defaultArcs.map((a, i) => ({
      id: a.id,
      value: [2847, 1923, 892, 634, 1205, 3102][i] || 500,
    }))
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setThreats((data) =>
        data.map((t) => ({
          ...t,
          value: Math.max(100, t.value + Math.floor(Math.random() * 101) - 50),
        }))
      );
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    pointerInteracting.current = { x: e.clientX, y: e.clientY };
    if (canvasRef.current) canvasRef.current.style.cursor = "grabbing";
    isPausedRef.current = true;
  }, []);

  const handlePointerUp = useCallback(() => {
    if (pointerInteracting.current !== null) {
      phiOffsetRef.current += dragOffset.current.phi;
      thetaOffsetRef.current += dragOffset.current.theta;
      dragOffset.current = { phi: 0, theta: 0 };
    }
    pointerInteracting.current = null;
    if (canvasRef.current) canvasRef.current.style.cursor = "grab";
    isPausedRef.current = false;
  }, []);

  useEffect(() => {
    const handlePointerMove = (e: PointerEvent) => {
      if (pointerInteracting.current !== null) {
        dragOffset.current = {
          phi: (e.clientX - pointerInteracting.current.x) / 300,
          theta: (e.clientY - pointerInteracting.current.y) / 1000,
        };
      }
    };
    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    window.addEventListener("pointerup", handlePointerUp, { passive: true });
    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, [handlePointerUp]);

  useEffect(() => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    let globe: ReturnType<typeof createGlobe> | null = null;
    let animationId: number;
    let phi = -1.3; // Start centered on India

    function init() {
      const width = canvas.offsetWidth;
      if (width === 0 || globe) return;

      globe = createGlobe(canvas, {
        devicePixelRatio: Math.min(window.devicePixelRatio || 1, 2),
        width,
        height: width,
        phi: -1.3,
        theta: 0.25,
        dark: 1,
        diffuse: 1.2,
        mapSamples: 16000,
        mapBrightness: 6,
        baseColor: [0.05, 0.05, 0.08],
        markerColor: [0.024, 0.714, 0.831],
        glowColor: [0.024, 0.35, 0.42],
        markers: markers.map((m) => ({
          location: m.location,
          size: m.id.startsWith("ind") ? 0.06 : 0.03,
        })),
      });

      function animate() {
        if (!isPausedRef.current) phi += speed;
        globe!.update({
          phi: phi + phiOffsetRef.current + dragOffset.current.phi,
          theta: 0.25 + thetaOffsetRef.current + dragOffset.current.theta,
        });
        animationId = requestAnimationFrame(animate);
      }
      animate();
      setTimeout(() => canvas && (canvas.style.opacity = "1"));
    }

    if (canvas.offsetWidth > 0) {
      init();
    } else {
      const ro = new ResizeObserver((entries) => {
        if (entries[0]?.contentRect.width > 0) {
          ro.disconnect();
          init();
        }
      });
      ro.observe(canvas);
    }

    return () => {
      if (animationId) cancelAnimationFrame(animationId);
      if (globe) globe.destroy();
    };
  }, [markers, arcs, speed]);

  return (
    <div className={`relative aspect-square select-none ${className}`}>
      <canvas
        ref={canvasRef}
        onPointerDown={handlePointerDown}
        style={{
          width: "100%",
          height: "100%",
          cursor: "grab",
          opacity: 0,
          transition: "opacity 1.2s ease",
          borderRadius: "50%",
          touchAction: "none",
        }}
      />
      {/* Threat counter overlay */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 flex-wrap justify-center">
        {threats.slice(0, 3).map((t) => (
          <div
            key={t.id}
            className="font-mono text-[10px] text-red-400 bg-red-500/10 border border-red-500/20 px-2 py-1 rounded-md backdrop-blur-sm"
          >
            {t.value.toLocaleString()} threats/hr
          </div>
        ))}
      </div>
    </div>
  );
}