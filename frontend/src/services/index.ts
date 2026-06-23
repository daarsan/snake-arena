import { createMockApi } from "./mockApi";
import type { ApiService } from "./types";

// Single centralized service instance. Swap to a real implementation here when ready.
export const api: ApiService = createMockApi();

export type { ApiService, User, Score, ActiveGame, GameMode } from "./types";
