import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { api } from "@/services";
import type { ActiveGame } from "@/services/types";
import { SnakeBoard } from "@/components/SnakeBoard";

export const Route = createFileRoute("/watch/$id")({
  head: () => ({ meta: [{ title: "Spectating — Snake Arena" }] }),
  component: WatchOne,
});

function WatchOne() {
  const { id } = Route.useParams();
  const [game, setGame] = useState<ActiveGame | null>(null);
  useEffect(() => {
    const unsub = api.subscribeActiveGame(id, setGame);
    const t = setInterval(() => api.getActiveGame(id).then(setGame), 500);
    return () => { unsub(); clearInterval(t); };
  }, [id]);

  if (!game) return (
    <div className="text-center">
      <p className="text-muted-foreground">Game not found or ended.</p>
      <Link to="/watch" className="mt-2 inline-block text-primary underline">Back to live games</Link>
    </div>
  );

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex w-full max-w-md items-center justify-between">
        <h1 className="text-xl font-bold">{game.username}</h1>
        <div className="text-sm text-muted-foreground">{game.mode === "wrap" ? "Pass-through" : "Walls"} · score {game.score} · {game.alive ? "alive" : "dead"}</div>
      </div>
      <SnakeBoard state={game} className="rounded-md border border-border" />
      <Link to="/watch" className="text-sm text-primary underline">← All live games</Link>
    </div>
  );
}
