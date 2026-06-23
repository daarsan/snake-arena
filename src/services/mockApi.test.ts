import { describe, it, expect, beforeEach } from "vitest";
import { createMockApi, resetMockApi } from "./mockApi";

describe("mockApi", () => {
  beforeEach(() => resetMockApi());

  it("signs up and logs in users", async () => {
    const api = createMockApi();
    const u = await api.signup("alice", "pw");
    expect(u.username).toBe("alice");
    const me = await api.getCurrentUser();
    expect(me?.username).toBe("alice");
    await api.logout();
    expect(await api.getCurrentUser()).toBeNull();
    const back = await api.login("alice", "pw");
    expect(back.id).toBe(u.id);
  });

  it("rejects duplicate signups and bad logins", async () => {
    const api = createMockApi();
    await api.signup("bob", "pw");
    await expect(api.signup("bob", "x")).rejects.toThrow(/taken/);
    await expect(api.login("bob", "wrong")).rejects.toThrow(/invalid/i);
  });

  it("submits and ranks scores per mode", async () => {
    const api = createMockApi();
    await api.signup("a", "pw");
    await api.submitScore({ mode: "walls", score: 5 });
    await api.submitScore({ mode: "walls", score: 12 });
    await api.submitScore({ mode: "wrap", score: 99 });
    const walls = await api.getLeaderboard("walls");
    expect(walls.map((s) => s.score)).toEqual([12, 5]);
    const wrap = await api.getLeaderboard("wrap");
    expect(wrap).toHaveLength(1);
    expect(wrap[0].score).toBe(99);
  });

  it("tracks active games and notifies subscribers", async () => {
    const api = createMockApi();
    await api.signup("c", "pw");
    const updates: number[] = [];
    const unsub = api.subscribeActiveGames((g) => updates.push(g.length));
    const g = await api.startGame({ mode: "walls", gridSize: 20 });
    await api.updateGame({ ...g, score: 3, alive: true });
    await api.endGame(g.id);
    unsub();
    expect(updates[0]).toBe(0); // initial
    expect(updates.at(-1)).toBe(0); // after end
    expect(Math.max(...updates)).toBeGreaterThanOrEqual(1);
  });
});
