import { describe, it, expect } from "vitest";
import { createInitialState, tick, changeDir } from "@/lib/snake-engine";

describe("snake-engine", () => {
  it("creates initial state with snake in the middle", () => {
    const s = createInitialState("walls", 20);
    expect(s.snake).toHaveLength(1);
    expect(s.snake[0]).toEqual({ x: 10, y: 10 });
    expect(s.alive).toBe(true);
    expect(s.score).toBe(0);
  });

  it("moves snake right by default", () => {
    const s = tick(createInitialState("walls", 20));
    expect(s.snake[0]).toEqual({ x: 11, y: 10 });
  });

  it("dies hitting walls in walls mode", () => {
    let s = createInitialState("walls", 5);
    s = { ...s, snake: [{ x: 4, y: 2 }], dir: "right" };
    s = tick(s);
    expect(s.alive).toBe(false);
  });

  it("wraps around edges in pass-through mode", () => {
    let s = createInitialState("wrap", 5);
    s = { ...s, snake: [{ x: 4, y: 2 }], dir: "right" };
    s = tick(s);
    expect(s.alive).toBe(true);
    expect(s.snake[0]).toEqual({ x: 0, y: 2 });
  });

  it("grows and scores when eating food", () => {
    let s = createInitialState("wrap", 10);
    s = { ...s, snake: [{ x: 3, y: 3 }], dir: "right", food: { x: 4, y: 3 } };
    s = tick(s, () => 0);
    expect(s.score).toBe(1);
    expect(s.snake).toHaveLength(2);
  });

  it("ignores reverse direction when snake has length > 1", () => {
    const s = { ...createInitialState("wrap", 10), snake: [{ x: 5, y: 5 }, { x: 4, y: 5 }], dir: "right" as const };
    const next = changeDir(s, "left");
    expect(next.dir).toBe("right");
  });

  it("dies on self-collision", () => {
    let s = createInitialState("wrap", 10);
    // Build a square: head will collide with body
    s = {
      ...s,
      snake: [
        { x: 5, y: 5 },
        { x: 5, y: 6 },
        { x: 4, y: 6 },
        { x: 4, y: 5 },
      ],
      dir: "down",
    };
    // ticking down: new head will be (5,6) -> collides with body
    s = tick(s);
    expect(s.alive).toBe(false);
  });
});
