import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  Link,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { useEffect, type ReactNode } from "react";

import appCss from "../styles.css?url";
import { reportLovableError } from "../lib/lovable-error-reporting";
import { AuthProvider, useAuth } from "@/lib/auth-context";
import { Toaster } from "@/components/ui/sonner";
import { Button } from "@/components/ui/button";

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-7xl font-bold text-foreground">404</h1>
        <p className="mt-2 text-sm text-muted-foreground">This page slithered away.</p>
        <div className="mt-6">
          <Link to="/" className="text-primary underline">Go home</Link>
        </div>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  const router = useRouter();
  useEffect(() => {
    reportLovableError(error, { boundary: "tanstack_root_error_component" });
  }, [error]);
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-xl font-semibold">Something went wrong</h1>
        <p className="mt-2 text-sm text-muted-foreground">{error.message}</p>
        <Button className="mt-4" onClick={() => { router.invalidate(); reset(); }}>Try again</Button>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "Snake Arena" },
      { name: "description", content: "Multiplayer-ready Snake with leaderboard and spectator mode." },
    ],
    links: [{ rel: "stylesheet", href: appCss }],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head><HeadContent /></head>
      <body>{children}<Scripts /></body>
    </html>
  );
}

function Nav() {
  const { user, logout } = useAuth();
  return (
    <header className="border-b border-border bg-card/50 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link to="/" className="text-lg font-bold tracking-tight">🐍 Snake Arena</Link>
        <nav className="flex items-center gap-1 text-sm">
          <Link to="/play" className="rounded-md px-3 py-1.5 hover:bg-accent" activeProps={{ className: "rounded-md px-3 py-1.5 bg-accent" }}>Play</Link>
          <Link to="/leaderboard" className="rounded-md px-3 py-1.5 hover:bg-accent" activeProps={{ className: "rounded-md px-3 py-1.5 bg-accent" }}>Leaderboard</Link>
          <Link to="/watch" className="rounded-md px-3 py-1.5 hover:bg-accent" activeProps={{ className: "rounded-md px-3 py-1.5 bg-accent" }}>Watch</Link>
          {user ? (
            <div className="ml-2 flex items-center gap-2">
              <span className="text-muted-foreground">{user.username}</span>
              <Button size="sm" variant="ghost" onClick={() => logout()}>Logout</Button>
            </div>
          ) : (
            <div className="ml-2 flex items-center gap-1">
              <Link to="/login" className="rounded-md px-3 py-1.5 hover:bg-accent">Login</Link>
              <Link to="/signup" className="rounded-md bg-primary px-3 py-1.5 text-primary-foreground hover:opacity-90">Sign up</Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <div className="min-h-screen bg-background text-foreground">
          <Nav />
          <main className="mx-auto max-w-5xl px-4 py-8">
            <Outlet />
          </main>
        </div>
        <Toaster />
      </AuthProvider>
    </QueryClientProvider>
  );
}
