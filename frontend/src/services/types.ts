export type GameMode = "walls" | "wrap";

export interface User {
  id: string;
  username: string;
}

export interface Score {
  id: string;
  userId: string;
  username: string;
  mode: GameMode;
  score: number;
  createdAt: number;
}

export interface ActiveGame {
  id: string;
  userId: string;
  username: string;
  mode: GameMode;
  score: number;
  // Serialized state for spectators
  snake: { x: number; y: number }[];
  food: { x: number; y: number };
  gridSize: number;
  alive: boolean;
  updatedAt: number;
}

export interface ApiService {
  // auth
  signup(username: string, password: string): Promise<User>;
  login(username: string, password: string): Promise<User>;
  logout(): Promise<void>;
  getCurrentUser(): Promise<User | null>;

  // scores
  submitScore(input: { mode: GameMode; score: number }): Promise<Score>;
  getLeaderboard(mode: GameMode, limit?: number): Promise<Score[]>;

  // active games (spectator)
  startGame(input: { mode: GameMode; gridSize: number }): Promise<ActiveGame>;
  updateGame(input: Omit<ActiveGame, "username" | "userId" | "updatedAt">): Promise<ActiveGame>;
  endGame(id: string): Promise<void>;
  listActiveGames(): Promise<ActiveGame[]>;
  getActiveGame(id: string): Promise<ActiveGame | null>;
  subscribeActiveGames(cb: (games: ActiveGame[]) => void): () => void;
  subscribeActiveGame(id: string, cb: (game: ActiveGame | null) => void): () => void;
}
