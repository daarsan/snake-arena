import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Snake Arena — Play, compete, spectate" },
      { name: "description", content: "Classic Snake with walls and pass-through modes, leaderboards, and a spectator view." },
    ],
  }),
  component: Home,
});

function Home() {
  return (
    <div className="flex flex-col items-center gap-8 py-12 text-center">
      <h1 className="text-5xl font-bold tracking-tight">Snake Arena</h1>
      <p className="max-w-xl text-muted-foreground">
        Classic Snake — pick your poison: hit walls and die, or wrap around the edges. Submit
        scores, climb the leaderboard, and spectate live games.
      </p>
      <div className="flex gap-3">
        <Link to="/play"><Button size="lg">Play now</Button></Link>
        <Link to="/leaderboard"><Button size="lg" variant="secondary">Leaderboard</Button></Link>
        <Link to="/watch"><Button size="lg" variant="outline">Watch live</Button></Link>
      </div>
    </div>
  );
}
