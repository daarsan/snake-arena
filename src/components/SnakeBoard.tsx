import { useEffect, useRef } from "react";
import type { ActiveGame } from "@/services/types";
import type { GameState } from "@/lib/snake-engine";

interface Props {
  state: Pick<GameState, "snake" | "food" | "gridSize"> | ActiveGame;
  cell?: number;
  className?: string;
}

export function SnakeBoard({ state, cell = 20, className }: Props) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const size = state.gridSize * cell;
    canvas.width = size;
    canvas.height = size;

    ctx.fillStyle = "hsl(240 10% 8%)";
    ctx.fillRect(0, 0, size, size);

    // grid
    ctx.strokeStyle = "hsl(240 6% 14%)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= state.gridSize; i++) {
      ctx.beginPath();
      ctx.moveTo(i * cell, 0);
      ctx.lineTo(i * cell, size);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * cell);
      ctx.lineTo(size, i * cell);
      ctx.stroke();
    }

    // food
    ctx.fillStyle = "hsl(0 80% 60%)";
    ctx.beginPath();
    ctx.arc(state.food.x * cell + cell / 2, state.food.y * cell + cell / 2, cell / 2.5, 0, Math.PI * 2);
    ctx.fill();

    // snake
    state.snake.forEach((p, i) => {
      ctx.fillStyle = i === 0 ? "hsl(140 70% 55%)" : "hsl(140 50% 45%)";
      ctx.fillRect(p.x * cell + 1, p.y * cell + 1, cell - 2, cell - 2);
    });
  }, [state, cell]);

  return <canvas ref={ref} className={className} />;
}
