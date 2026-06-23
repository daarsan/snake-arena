import type { ApiService, ActiveGame, Score, User } from "./types";

const BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? "/api";

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    credentials: "include",
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return undefined as T;
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: `HTTP ${res.status}` }));
    throw new Error(err.message ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function createRealApi(): ApiService {
  return {
    async signup(username, password) {
      return request<User>("POST", "/auth/signup", { username, password });
    },

    async login(username, password) {
      return request<User>("POST", "/auth/login", { username, password });
    },

    async logout() {
      await request<void>("POST", "/auth/logout");
    },

    async getCurrentUser() {
      try {
        return await request<User>("GET", "/auth/me");
      } catch {
        return null;
      }
    },

    async submitScore({ mode, score }) {
      return request<Score>("POST", "/scores", { mode, score });
    },

    async getLeaderboard(mode, limit = 10) {
      return request<Score[]>("GET", `/leaderboard?mode=${mode}&limit=${limit}`);
    },

    async startGame({ mode, gridSize }) {
      return request<ActiveGame>("POST", "/games", { mode, gridSize });
    },

    async updateGame({ id, mode, score, snake, food, gridSize, alive }) {
      return request<ActiveGame>("PUT", `/games/${id}`, { mode, score, snake, food, gridSize, alive });
    },

    async endGame(id) {
      await request<void>("DELETE", `/games/${id}`);
    },

    async listActiveGames() {
      return request<ActiveGame[]>("GET", "/games");
    },

    async getActiveGame(id) {
      try {
        return await request<ActiveGame>("GET", `/games/${id}`);
      } catch {
        return null;
      }
    },

    subscribeActiveGames(cb) {
      const es = new EventSource(`${BASE}/games/events`, { withCredentials: true });
      es.addEventListener("games", (e: MessageEvent) => {
        try {
          cb(JSON.parse(e.data) as ActiveGame[]);
        } catch {}
      });
      request<ActiveGame[]>("GET", "/games").then(cb).catch(() => {});
      return () => es.close();
    },

    subscribeActiveGame(id, cb) {
      const es = new EventSource(`${BASE}/games/${id}/events`, { withCredentials: true });
      es.addEventListener("game", (e: MessageEvent) => {
        try {
          cb(JSON.parse(e.data) as ActiveGame | null);
        } catch {}
      });
      es.onerror = () => cb(null);
      request<ActiveGame>("GET", `/games/${id}`).then(cb).catch(() => cb(null));
      return () => es.close();
    },
  };
}
