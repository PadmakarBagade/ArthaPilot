"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { checkHealth } from "@/lib/api";

export default function Home() {
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(
    null,
  );

  useEffect(() => {
    checkHealth().then(setIsBackendHealthy);
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-background px-6 py-16">
      <div className="w-full max-w-lg space-y-8 text-center">
        <div className="space-y-3">
          <p className="text-sm font-medium uppercase tracking-[0.25em] text-muted-foreground">
            ArthaPilot
          </p>
          <h1 className="text-4xl font-semibold tracking-tight">
            Financial clarity, one step at a time.
          </h1>
          <p className="text-muted-foreground">
            Your personal financial health copilot is getting ready.
          </p>
        </div>

        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <p className="text-sm text-muted-foreground">Backend status</p>
          <p
            className="mt-2 text-lg font-medium"
            role="status"
            aria-live="polite"
          >
            {isBackendHealthy === null
              ? "Checking backend..."
              : isBackendHealthy
                ? "Backend OK"
                : "Backend not reachable"}
          </p>
        </div>

        <Button
          variant="outline"
          onClick={() => {
            setIsBackendHealthy(null);
            checkHealth().then(setIsBackendHealthy);
          }}
        >
          Check again
        </Button>
      </div>
    </main>
  );
}
