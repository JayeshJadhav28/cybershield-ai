"use client"

import { useEffect, useRef, useCallback, useState } from "react"
import createGlobe from "cobe"

interface AttackMarker {
  id: string
  location: [number, number]
  label: string
  type: "source" | "target"
}

interface AttackArc {
  id: string
  from: [number, number]
  to: [number, number]
}

interface GlobeAttackProps {
  markers?: AttackMarker[]
  arcs?: AttackArc[]
  className?: string
  speed?: number
}

// Attack sources → India targets
const defaultMarkers: AttackMarker[] = [
  // Indian target cities
  { id: "ind-mum", location: [19.09, 72.87], label: "Mumbai", type: "target" },
  { id: "ind-del", location: [28.61, 77.21], label: "Delhi", type: "target" },
  { id: "ind-blr", location: [12.97, 77.59], label: "Bangalore", type: "target" },
  { id: "ind-chn", location: [13.08, 80.27], label: "Chennai", type: "target" },
  { id: "ind-hyd", location: [17.39, 78.49], label: "Hyderabad", type: "target" },
  // Attack origin cities
  { id: "atk-bej", location: [39.91, 116.40], label: "Beijing", type: "source" },
  { id: "atk-mos", location: [55.76, 37.62], label: "Moscow", type: "source" },
  { id: "atk-lag", location: [6.45, 3.39], label: "Lagos", type: "source" },
  { id: "atk-nyc", location: [40.71, -74.01], label: "New York", type: "source" },
  { id: "atk-teh", location: [35.69, 51.39], label: "Tehran", type: "source" },
  { id: "atk-pyo", location: [39.03, 125.75], label: "Pyongyang", type: "source" },
  { id: "atk-sao", location: [-23.55, -46.63], label: "São Paulo", type: "source" },
]

const defaultArcs: AttackArc[] = [
  { id: "arc-1", from: [39.91, 116.40], to: [19.09, 72.87] },   // Beijing → Mumbai
  { id: "arc-2", from: [55.76, 37.62], to: [28.61, 77.21] },    // Moscow → Delhi
  { id: "arc-3", from: [6.45, 3.39], to: [13.08, 80.27] },      // Lagos → Chennai
  { id: "arc-4", from: [40.71, -74.01], to: [12.97, 77.59] },   // New York → Bangalore
  { id: "arc-5", from: [35.69, 51.39], to: [17.39, 78.49] },    // Tehran → Hyderabad
  { id: "arc-6", from: [39.03, 125.75], to: [28.61, 77.21] },   // Pyongyang → Delhi
  { id: "arc-7", from: [-23.55, -46.63], to: [19.09, 72.87] },  // São Paulo → Mumbai
  { id: "arc-8", from: [55.76, 37.62], to: [12.97, 77.59] },    // Moscow → Bangalore
]

export function GlobeAttack({
  markers = defaultMarkers,
  arcs = defaultArcs,
  className = "",
  speed = 0.002,
}: GlobeAttackProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const pointerInteracting = useRef<{ x: number; y: number } | null>(null)
  const dragOffset = useRef({ phi: 0, theta: 0 })
  const phiOffsetRef = useRef(0)
  const thetaOffsetRef = useRef(0)
  const isPausedRef = useRef(false)

  const [threatData, setThreatData] = useState(() =>
    defaultArcs.map((a, i) => ({
      id: a.id,
      value: [2847, 1923, 892, 1456, 634, 1205, 3102, 756][i] || 500,
      type: ["Phishing", "Deepfake", "Malware", "BEC", "Vishing", "Smishing", "Ransomware", "DDoS"][i] || "Attack",
    }))
  )

  // Animate threat counters
  useEffect(() => {
    const interval = setInterval(() => {
      setThreatData((data) =>
        data.map((t) => ({
          ...t,
          value: Math.max(100, t.value + Math.floor(Math.random() * 201) - 80),
        }))
      )
    }, 1500)
    return () => clearInterval(interval)
  }, [])

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    pointerInteracting.current = { x: e.clientX, y: e.clientY }
    if (canvasRef.current) canvasRef.current.style.cursor = "grabbing"
    isPausedRef.current = true
  }, [])

  const handlePointerUp = useCallback(() => {
    if (pointerInteracting.current !== null) {
      phiOffsetRef.current += dragOffset.current.phi
      thetaOffsetRef.current += dragOffset.current.theta
      dragOffset.current = { phi: 0, theta: 0 }
    }
    pointerInteracting.current = null
    if (canvasRef.current) canvasRef.current.style.cursor = "grab"
    isPausedRef.current = false
  }, [])

  useEffect(() => {
    const handlePointerMove = (e: PointerEvent) => {
      if (pointerInteracting.current !== null) {
        dragOffset.current = {
          phi: (e.clientX - pointerInteracting.current.x) / 300,
          theta: (e.clientY - pointerInteracting.current.y) / 1000,
        }
      }
    }
    window.addEventListener("pointermove", handlePointerMove, { passive: true })
    window.addEventListener("pointerup", handlePointerUp, { passive: true })
    return () => {
      window.removeEventListener("pointermove", handlePointerMove)
      window.removeEventListener("pointerup", handlePointerUp)
    }
  }, [handlePointerUp])

  useEffect(() => {
    if (!canvasRef.current) return
    const canvas = canvasRef.current
    let globe: ReturnType<typeof createGlobe> | null = null
    let animationId: number
    // Start rotation centered on India (lon ~78°E → phi ≈ -1.36 rad)
    let phi = -1.36

    function init() {
      const width = canvas.offsetWidth
      if (width === 0 || globe) return

      globe = createGlobe(canvas, {
        devicePixelRatio: Math.min(window.devicePixelRatio || 1, 2),
        width,
        height: width,
        phi: -1.36,
        theta: 0.2,
        dark: 1,
        diffuse: 1.2,
        mapSamples: 20000,
        mapBrightness: 4,
        baseColor: [0.15, 0.04, 0.04],
        markerColor: [1, 0.2, 0.1],
        glowColor: [0.4, 0.08, 0.06],
        markerElevation: 0.02,
        markers: markers.map((m) => ({
          location: m.location,
          size: m.type === "target" ? 0.07 : 0.03,
          id: m.id,
        })),
        arcs: arcs.map((a) => ({
          from: a.from,
          to: a.to,
          id: a.id,
        })),
        arcColor: [1, 0.15, 0.1],
        arcWidth: 0.6,
        arcHeight: 0.3,
        opacity: 0.85,
      })

      function animate() {
        if (!isPausedRef.current) phi += speed
        globe!.update({
          phi: phi + phiOffsetRef.current + dragOffset.current.phi,
          theta: 0.2 + thetaOffsetRef.current + dragOffset.current.theta,
        })
        animationId = requestAnimationFrame(animate)
      }
      animate()
      setTimeout(() => canvas && (canvas.style.opacity = "1"))
    }

    if (canvas.offsetWidth > 0) {
      init()
    } else {
      const ro = new ResizeObserver((entries) => {
        if (entries[0]?.contentRect.width > 0) {
          ro.disconnect()
          init()
        }
      })
      ro.observe(canvas)
    }

    return () => {
      if (animationId) cancelAnimationFrame(animationId)
      if (globe) globe.destroy()
    }
  }, [markers, arcs, speed])

  return (
    <div className={`relative aspect-square select-none ${className}`}>
      {/* Pulsing ring behind globe */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[85%] h-[85%] rounded-full border border-red-500/20 animate-[pulse_3s_ease-in-out_infinite]" />
      </div>
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[95%] h-[95%] rounded-full border border-red-500/10 animate-[pulse_4s_ease-in-out_infinite_0.5s]" />
      </div>

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

      {/* Marker labels */}
      {markers.map((m) => (
        <div
          key={m.id}
          style={{
            position: "absolute",
            positionAnchor: `--cobe-${m.id}`,
            bottom: "anchor(top)",
            left: "anchor(center)",
            translate: "-50% 0",
            display: "flex",
            flexDirection: "column" as const,
            alignItems: "center",
            gap: 4,
            pointerEvents: "none" as const,
            opacity: `var(--cobe-visible-${m.id}, 0)`,
            filter: `blur(calc((1 - var(--cobe-visible-${m.id}, 0)) * 8px))`,
            transition: "opacity 0.3s, filter 0.3s",
          }}
        >
          {/* Animated dot */}
          <div className="relative">
            <div
              className={`w-2.5 h-2.5 rounded-full ${
                m.type === "target"
                  ? "bg-red-500 shadow-[0_0_8px_2px_rgba(239,68,68,0.6)]"
                  : "bg-orange-500 shadow-[0_0_6px_2px_rgba(249,115,22,0.4)]"
              }`}
            />
            {m.type === "target" && (
              <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-red-500/50 animate-ping" />
            )}
          </div>
          {/* Label */}
          <span
            className={`font-mono text-[10px] px-1.5 py-0.5 rounded whitespace-nowrap ${
              m.type === "target"
                ? "bg-red-500/20 text-red-300 border border-red-500/30"
                : "bg-orange-500/10 text-orange-300/80 border border-orange-500/20"
            }`}
          >
            {m.type === "source" ? "" : ""}
            {m.label}
          </span>
        </div>
      ))}

      {/* Arc threat labels */}
      {threatData.map((t) => (
        <div
          key={t.id}
          style={{
            position: "absolute",
            positionAnchor: `--cobe-arc-${t.id}`,
            bottom: "anchor(top)",
            left: "anchor(center)",
            translate: "-50% 0",
            pointerEvents: "none" as const,
            opacity: `var(--cobe-visible-arc-${t.id}, 0)`,
            filter: `blur(calc((1 - var(--cobe-visible-arc-${t.id}, 0)) * 8px))`,
            transition: "opacity 0.3s, filter 0.3s",
          }}
        >
          <div className="font-mono text-[10px] text-red-300 bg-red-950/80 border border-red-500/30 px-2 py-1 rounded-md whitespace-nowrap backdrop-blur-sm shadow-lg shadow-red-500/10">
            <span className="text-red-400 font-semibold">{t.value.toLocaleString()}</span>
            <span className="text-red-400/60 ml-1">{t.type}/hr</span>
          </div>
        </div>
      ))}

      {/* Bottom threat summary */}
      <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 flex gap-2 flex-wrap justify-center">
        <div className="flex items-center gap-1.5 font-mono text-[10px] text-red-400 bg-red-500/10 border border-red-500/20 px-2.5 py-1.5 rounded-full backdrop-blur-sm">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
          </span>
          <span>{threatData.reduce((sum, t) => sum + t.value, 0).toLocaleString()} total threats/hr</span>
        </div>
      </div>

      {/* Corner label */}
      <div className="absolute top-2 right-2 font-mono text-[9px] text-red-500/50 tracking-wider uppercase">
        Live Threat Map
      </div>
    </div>
  )
}