import { createRealApi } from "./realApi";
import type { ApiService } from "./types";

export const api: ApiService = createRealApi();

export type { ApiService, User, Score, ActiveGame, GameMode } from "./types";
