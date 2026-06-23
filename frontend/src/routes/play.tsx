import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { SnakeGame } from "@/components/SnakeGame";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";
import type { GameMode } from "@/services/types";

export const Route = createFileRoute("/play")({
  head: () => ({ meta: [{ title: "Play — Snake Arena" }] }),
  component: Play,
});

function Play() {
  const [mode, setMode] = useState<GameMode>("walls");
  const { user } = useAuth();
  return (
    <div className="flex flex-col items-center gap-6">
      <div className="flex items-center gap-2">
        <Button variant={mode === "walls" ? "default" : "outline"} onClick={() => setMode("walls")}>Walls</Button>
        <Button variant={mode === "wrap" ? "default" : "outline"} onClick={() => setMode("wrap")}>Pass-through</Button>
      </div>
      {!user && (
        <p className="text-sm text-muted-foreground">
          <Link to="/login" className="underline">Log in</Link> to save scores and broadcast your game.
        </p>
      )}
      <SnakeGame key={mode} mode={mode} />
    </div>
  );
}
