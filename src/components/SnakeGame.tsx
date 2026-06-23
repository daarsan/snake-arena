import { useCallback, useEffect, useRef, useState } from "react";
import { SnakeBoard } from "./SnakeBoard";
import { changeDir, createInitialState, tick, type Direction } from "@/lib/snake-engine";
import type { GameMode } from "@/services/types";
import { api } from "@/services";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

const TICK_MS = 110;
const GRID = 20;

export function SnakeGame({ mode }: { mode: GameMode }) {
  const { user } = useAuth();
  const [state, setState] = useState(() => createInitialState(mode, GRID));
  const stateRef = useRef(state);
  stateRef.current = state;
  const gameIdRef = useRef<string | null>(null);
  const [running, setRunning] = useState(false);
  const [bestSubmitted, setBestSubmitted] = useState(false);

  const startNewGame = useCallback(async () => {
    setState(createInitialState(mode, GRID));
    setBestSubmitted(false);
    if (user) {
      const g = await api.startGame({ mode, gridSize: GRID });
      gameIdRef.current = g.id;
    }
    setRunning(true);
  }, [mode, user]);

  // Keyboard
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const map: Record<string, Direction> = {
        ArrowUp: "up", ArrowDown: "down", ArrowLeft: "left", ArrowRight: "right",
        w: "up", s: "down", a: "left", d: "right",
        W: "up", S: "down", A: "left", D: "right",
      };
      const next = map[e.key];
      if (next) {
        e.preventDefault();
        setState((s) => changeDir(s, next));
      } else if (e.key === " ") {
        e.preventDefault();
        if (!running) startNewGame();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [running, startNewGame]);

  // Tick loop
  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => {
      setState((s) => tick(s));
    }, TICK_MS);
    return () => clearInterval(id);
  }, [running]);

  // Sync to backend (throttled by tick)
  useEffect(() => {
    if (!running || !gameIdRef.current) return;
    const id = gameIdRef.current;
    api
      .updateGame({
        id,
        score: state.score,
        snake: state.snake,
        food: state.food,
        gridSize: state.gridSize,
        alive: state.alive,
        mode: state.mode,
      })
      .catch(() => {});
  }, [state, running]);

  // Death handling
  useEffect(() => {
    if (state.alive || !running) return;
    setRunning(false);
    if (user && !bestSubmitted) {
      setBestSubmitted(true);
      api.submitScore({ mode, score: state.score }).then(() => {
        toast.success(`Game over! Score: ${state.score}`);
      });
      if (gameIdRef.current) {
        const id = gameIdRef.current;
        gameIdRef.current = null;
        setTimeout(() => api.endGame(id).catch(() => {}), 3000);
      }
    } else {
      toast(`Game over! Score: ${state.score}`);
    }
  }, [state.alive, state.score, running, user, mode, bestSubmitted]);

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex items-center gap-6 text-sm">
        <div>Mode: <span className="font-semibold capitalize">{mode === "wrap" ? "Pass-through" : "Walls"}</span></div>
        <div>Score: <span className="font-semibold">{state.score}</span></div>
        <div>Status: <span className="font-semibold">{state.alive ? (running ? "Playing" : "Paused") : "Dead"}</span></div>
      </div>
      <SnakeBoard state={state} className="rounded-md border border-border shadow-lg" />
      <div className="flex gap-2">
        <Button onClick={startNewGame}>{running ? "Restart" : "Start (Space)"}</Button>
      </div>
      <p className="text-xs text-muted-foreground">Arrow keys or WASD to move.</p>
    </div>
  );
}
