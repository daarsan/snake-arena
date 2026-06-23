import type { ApiService, ActiveGame, Score, User, GameMode } from "./types";

const KEYS = {
  users: "snake.users",
  session: "snake.session",
  scores: "snake.scores",
  games: "snake.games",
};

const isBrowser = typeof window !== "undefined" && typeof localStorage !== "undefined";

function read<T>(key: string, fallback: T): T {
  if (!isBrowser) return fallback;
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function write<T>(key: string, value: T) {
  if (!isBrowser) return;
  localStorage.setItem(key, JSON.stringify(value));
}

interface StoredUser extends User {
  password: string;
}

type Listener<T> = (v: T) => void;

export function createMockApi(): ApiService {
  const gameListeners = new Set<Listener<ActiveGame[]>>();
  const singleGameListeners = new Map<string, Set<Listener<ActiveGame | null>>>();

  // cross-tab sync via storage events
  if (isBrowser) {
    window.addEventListener("storage", (e) => {
      if (e.key === KEYS.games) {
        const games = read<ActiveGame[]>(KEYS.games, []);
        gameListeners.forEach((l) => l(games));
        singleGameListeners.forEach((set, id) => {
          const g = games.find((g) => g.id === id) ?? null;
          set.forEach((l) => l(g));
        });
      }
    });
  }

  function notifyGames() {
    const games = read<ActiveGame[]>(KEYS.games, []);
    gameListeners.forEach((l) => l(games));
    singleGameListeners.forEach((set, id) => {
      const g = games.find((g) => g.id === id) ?? null;
      set.forEach((l) => l(g));
    });
  }

  async function delay<T>(v: T, ms = 30): Promise<T> {
    return new Promise((r) => setTimeout(() => r(v), ms));
  }

  function uid() {
    return Math.random().toString(36).slice(2, 10);
  }

  return {
    async signup(username, password) {
      const users = read<StoredUser[]>(KEYS.users, []);
      if (users.find((u) => u.username.toLowerCase() === username.toLowerCase())) {
        throw new Error("Username already taken");
      }
      const user: StoredUser = { id: uid(), username, password };
      users.push(user);
      write(KEYS.users, users);
      const session: User = { id: user.id, username: user.username };
      write(KEYS.session, session);
      return delay(session);
    },
    async login(username, password) {
      const users = read<StoredUser[]>(KEYS.users, []);
      const u = users.find(
        (x) => x.username.toLowerCase() === username.toLowerCase() && x.password === password,
      );
      if (!u) throw new Error("Invalid username or password");
      const session: User = { id: u.id, username: u.username };
      write(KEYS.session, session);
      return delay(session);
    },
    async logout() {
      if (isBrowser) localStorage.removeItem(KEYS.session);
      return delay(undefined);
    },
    async getCurrentUser() {
      return delay(read<User | null>(KEYS.session, null));
    },
    async submitScore({ mode, score }) {
      const me = read<User | null>(KEYS.session, null);
      if (!me) throw new Error("Not logged in");
      const scores = read<Score[]>(KEYS.scores, []);
      const entry: Score = {
        id: uid(),
        userId: me.id,
        username: me.username,
        mode,
        score,
        createdAt: Date.now(),
      };
      scores.push(entry);
      write(KEYS.scores, scores);
      return delay(entry);
    },
    async getLeaderboard(mode, limit = 10) {
      const scores = read<Score[]>(KEYS.scores, [])
        .filter((s) => s.mode === mode)
        .sort((a, b) => b.score - a.score)
        .slice(0, limit);
      return delay(scores);
    },
    async startGame({ mode, gridSize }) {
      const me = read<User | null>(KEYS.session, null);
      if (!me) throw new Error("Not logged in");
      const games = read<ActiveGame[]>(KEYS.games, []);
      // Remove any prior active game for this user
      const filtered = games.filter((g) => g.userId !== me.id);
      const game: ActiveGame = {
        id: uid(),
        userId: me.id,
        username: me.username,
        mode,
        score: 0,
        snake: [{ x: Math.floor(gridSize / 2), y: Math.floor(gridSize / 2) }],
        food: { x: 2, y: 2 },
        gridSize,
        alive: true,
        updatedAt: Date.now(),
      };
      filtered.push(game);
      write(KEYS.games, filtered);
      notifyGames();
      return delay(game, 5);
    },
    async updateGame(input) {
      const games = read<ActiveGame[]>(KEYS.games, []);
      const idx = games.findIndex((g) => g.id === input.id);
      if (idx === -1) throw new Error("Game not found");
      const updated: ActiveGame = {
        ...games[idx],
        ...input,
        updatedAt: Date.now(),
      };
      games[idx] = updated;
      write(KEYS.games, games);
      notifyGames();
      return updated;
    },
    async endGame(id) {
      const games = read<ActiveGame[]>(KEYS.games, []).filter((g) => g.id !== id);
      write(KEYS.games, games);
      notifyGames();
    },
    async listActiveGames() {
      // prune stale (>30s)
      const cutoff = Date.now() - 30_000;
      const games = read<ActiveGame[]>(KEYS.games, []).filter((g) => g.updatedAt > cutoff);
      return delay(games);
    },
    async getActiveGame(id) {
      const games = read<ActiveGame[]>(KEYS.games, []);
      return delay(games.find((g) => g.id === id) ?? null);
    },
    subscribeActiveGames(cb) {
      gameListeners.add(cb);
      cb(read<ActiveGame[]>(KEYS.games, []));
      return () => gameListeners.delete(cb);
    },
    subscribeActiveGame(id, cb) {
      let set = singleGameListeners.get(id);
      if (!set) {
        set = new Set();
        singleGameListeners.set(id, set);
      }
      set.add(cb);
      const games = read<ActiveGame[]>(KEYS.games, []);
      cb(games.find((g) => g.id === id) ?? null);
      return () => {
        set!.delete(cb);
        if (set!.size === 0) singleGameListeners.delete(id);
      };
    },
  };
}

// Test helper - clear all state
export function resetMockApi() {
  if (!isBrowser) return;
  Object.values(KEYS).forEach((k) => localStorage.removeItem(k));
}
