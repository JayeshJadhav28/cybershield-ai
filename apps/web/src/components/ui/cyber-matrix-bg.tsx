"use client";

import { useEffect, useRef, useState } from "react";

export function CyberMatrixBg() {
  const gridRef = useRef<HTMLDivElement>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient || !gridRef.current) return;

    const grid = gridRef.current;
    const chars =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789<>/?;:"[]{}\\|!@#$%^&*()_+-=';

    const createTile = () => {
      const tile = document.createElement("div");
      tile.classList.add("cyber-tile");
      tile.onclick = () => {
        tile.textContent = chars[Math.floor(Math.random() * chars.length)];
        tile.classList.add("cyber-glitch");
        setTimeout(() => tile.classList.remove("cyber-glitch"), 200);
      };
      return tile;
    };

    const createGrid = () => {
      grid.innerHTML = "";
      const size = 60;
      const columns = Math.floor(window.innerWidth / size);
      const rows = Math.floor(window.innerHeight / size);
      grid.style.setProperty("--columns", String(columns));
      grid.style.setProperty("--rows", String(rows));

      const total = columns * rows;
      for (let i = 0; i < total; i++) {
        const tile = createTile();
        tile.textContent = chars[Math.floor(Math.random() * chars.length)];
        grid.appendChild(tile);
      }
    };

    const handleMouseMove = (e: MouseEvent) => {
      const radius = window.innerWidth / 4;
      const tiles = grid.children;
      for (let i = 0; i < tiles.length; i++) {
        const tile = tiles[i] as HTMLElement;
        const rect = tile.getBoundingClientRect();
        const tileX = rect.left + rect.width / 2;
        const tileY = rect.top + rect.height / 2;
        const distance = Math.sqrt(
          (e.clientX - tileX) ** 2 + (e.clientY - tileY) ** 2
        );
        tile.style.setProperty(
          "--intensity",
          String(Math.max(0, 1 - distance / radius))
        );
      }
    };

    createGrid();
    window.addEventListener("resize", createGrid);
    window.addEventListener("mousemove", handleMouseMove);

    return () => {
      window.removeEventListener("resize", createGrid);
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, [isClient]);

  if (!isClient) return null;

  return (
    <>
      <div ref={gridRef} className="cyber-matrix-grid" />
      <style>{`
        .cyber-matrix-grid {
          display: grid;
          grid-template-columns: repeat(var(--columns, 1), 1fr);
          grid-template-rows: repeat(var(--rows, 1), 1fr);
          width: 100vw;
          height: 100vh;
          position: fixed;
          top: 0;
          left: 0;
          z-index: 0;
          pointer-events: none;
        }
        .cyber-tile {
          --intensity: 0;
          pointer-events: all;
          display: flex;
          justify-content: center;
          align-items: center;
          font-family: 'Courier New', Courier, monospace;
          font-size: 1.2rem;
          opacity: calc(0.08 + var(--intensity) * 0.9);
          color: hsl(192, 91%, calc(45% + var(--intensity) * 30%));
          text-shadow: 0 0 calc(var(--intensity) * 15px) hsl(192, 91%, 55%);
          transform: scale(calc(1 + var(--intensity) * 0.2));
          transition: color 0.2s ease, text-shadow 0.2s ease,
                      transform 0.2s ease, opacity 0.2s ease;
          cursor: pointer;
        }
        .cyber-tile.cyber-glitch {
          animation: cyber-glitch-anim 0.2s ease;
        }
        @keyframes cyber-glitch-anim {
          0%   { transform: scale(1);   color: #22d3ee; }
          50%  { transform: scale(1.2); color: #fff; text-shadow: 0 0 10px #22d3ee; }
          100% { transform: scale(1);   color: #22d3ee; }
        }
      `}</style>
    </>
  );
}