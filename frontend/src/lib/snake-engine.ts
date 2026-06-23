import type { GameMode } from "@/services/types";

export type Point = { x: number; y: number };
export type Direction = "up" | "down" | "left" | "right";

export interface GameState {
  snake: Point[];
  dir: Direction;
  food: Point;
  score: number;
  alive: boolean;
  gridSize: number;
  mode: GameMode;
}

const DIRS: Record<Direction, Point> = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};

const OPP: Record<Direction, Direction> = {
  up: "down",
  down: "up",
  left: "right",
  right: "left",
};

export function createInitialState(mode: GameMode, gridSize = 20): GameState {
  const mid = Math.floor(gridSize / 2);
  return {
    snake: [{ x: mid, y: mid }],
    dir: "right",
    food: randomFood([{ x: mid, y: mid }], gridSize),
    score: 0,
    alive: true,
    gridSize,
    mode,
  };
}

export function randomFood(snake: Point[], gridSize: number, rng: () => number = Math.random): Point {
  const occupied = new Set(snake.map((p) => `${p.x},${p.y}`));
  const free: Point[] = [];
  for (let x = 0; x < gridSize; x++) {
    for (let y = 0; y < gridSize; y++) {
      if (!occupied.has(`${x},${y}`)) free.push({ x, y });
    }
  }
  if (free.length === 0) return { x: 0, y: 0 };
  return free[Math.floor(rng() * free.length)];
}

export function changeDir(state: GameState, next: Direction): GameState {
  if (state.snake.length > 1 && OPP[state.dir] === next) return state;
  return { ...state, dir: next };
}

export function tick(state: GameState, rng: () => number = Math.random): GameState {
  if (!state.alive) return state;
  const head = state.snake[0];
  const d = DIRS[state.dir];
  let nx = head.x + d.x;
  let ny = head.y + d.y;

  if (state.mode === "wrap") {
    nx = (nx + state.gridSize) % state.gridSize;
    ny = (ny + state.gridSize) % state.gridSize;
  } else if (nx < 0 || ny < 0 || nx >= state.gridSize || ny >= state.gridSize) {
    return { ...state, alive: false };
  }

  const ateFood = nx === state.food.x && ny === state.food.y;
  const newHead = { x: nx, y: ny };
  const newSnake = [newHead, ...state.snake];
  if (!ateFood) newSnake.pop();

  // Self-collision (check against body excluding the tail we just moved)
  for (let i = 1; i < newSnake.length; i++) {
    if (newSnake[i].x === nx && newSnake[i].y === ny) {
      return { ...state, alive: false };
    }
  }

  return {
    ...state,
    snake: newSnake,
    food: ateFood ? randomFood(newSnake, state.gridSize, rng) : state.food,
    score: ateFood ? state.score + 1 : state.score,
  };
}
