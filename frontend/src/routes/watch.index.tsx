import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { api } from "@/services";
import type { ActiveGame } from "@/services/types";
import { SnakeBoard } from "@/components/SnakeBoard";

export const Route = createFileRoute("/watch/")({
  head: () => ({ meta: [{ title: "Watch — Snake Arena" }] }),
  component: WatchList,
});

function WatchList() {
  const [games, setGames] = useState<ActiveGame[]>([]);
  useEffect(() => {
    const unsub = api.subscribeActiveGames((g) => {
      const cutoff = Date.now() - 30_000;
      setGames(g.filter((x) => x.updatedAt > cutoff));
    });
    const id = setInterval(() => {
      api.listActiveGames().then(setGames);
    }, 2000);
    return () => { unsub(); clearInterval(id); };
  }, []);

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold">Live games</h1>
      {games.length === 0 ? (
        <p className="text-muted-foreground">No one is playing right now. Open the game in another tab to broadcast!</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
          {games.map((g) => (
            <Link key={g.id} to="/watch/$id" params={{ id: g.id }} className="rounded-lg border border-border p-3 hover:bg-accent">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-semibold">{g.username}</span>
                <span className="text-muted-foreground">{g.mode === "wrap" ? "Pass-through" : "Walls"} · {g.score}</span>
              </div>
              <SnakeBoard state={g} cell={10} className="w-full rounded" />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
