import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { api } from "@/services";
import type { GameMode, Score } from "@/services/types";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/leaderboard")({
  head: () => ({ meta: [{ title: "Leaderboard — Snake Arena" }] }),
  component: Leaderboard,
});

function Leaderboard() {
  const [mode, setMode] = useState<GameMode>("walls");
  const [scores, setScores] = useState<Score[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getLeaderboard(mode, 10).then((s) => {
      setScores(s);
      setLoading(false);
    });
  }, [mode]);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Leaderboard</h1>
        <div className="flex gap-2">
          <Button size="sm" variant={mode === "walls" ? "default" : "outline"} onClick={() => setMode("walls")}>Walls</Button>
          <Button size="sm" variant={mode === "wrap" ? "default" : "outline"} onClick={() => setMode("wrap")}>Pass-through</Button>
        </div>
      </div>
      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50 text-left">
            <tr>
              <th className="px-4 py-2 w-12">#</th>
              <th className="px-4 py-2">Player</th>
              <th className="px-4 py-2 text-right">Score</th>
              <th className="px-4 py-2 text-right">When</th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">Loading...</td></tr>}
            {!loading && scores.length === 0 && (
              <tr><td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">No scores yet. Be the first!</td></tr>
            )}
            {scores.map((s, i) => (
              <tr key={s.id} className="border-t border-border">
                <td className="px-4 py-2 font-mono">{i + 1}</td>
                <td className="px-4 py-2 font-medium">{s.username}</td>
                <td className="px-4 py-2 text-right font-mono">{s.score}</td>
                <td className="px-4 py-2 text-right text-muted-foreground">{new Date(s.createdAt).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
