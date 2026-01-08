"use client";

import type { CSSProperties } from "react";
import { useEffect, useMemo, useState } from "react";
import {
  ConnectWallet,
  useAuthenticate,
  useMiniKit
} from "@coinbase/onchainkit";
import StatusPill, { Status } from "@/components/StatusPill";
import { MODULES, PIPELINE_STEPS } from "@/lib/modules";

const statusCopy: Record<Status, string> = {
  idle: "Ready to run your next task.",
  running: "Agent is spinning up the sandbox.",
  queued: "Task queued. Waiting for the worker.",
  failed: "Task failed. Check the logs and retry.",
  complete: "Task complete. Review the report."
};

export default function HomePage() {
  const { sdk, context } = useMiniKit() as {
    sdk?: { actions?: { ready?: () => void } };
    context?: Record<string, unknown>;
  };
  const auth = useAuthenticate() as any;
  const [selectedModule, setSelectedModule] = useState(MODULES[0]?.id ?? "learn");
  const [status, setStatus] = useState<Status>("idle");
  const [taskId, setTaskId] = useState<string | null>(null);

  const selected = useMemo(
    () => MODULES.find((module) => module.id === selectedModule),
    [selectedModule]
  );

  useEffect(() => {
    sdk?.actions?.ready?.();
  }, [sdk]);

  const login = auth?.login ?? auth?.authenticate ?? auth?.signIn;
  const logout = auth?.logout ?? auth?.signOut;

  const handleAuth = async () => {
    if (auth?.isAuthenticated) {
      await logout?.();
      return;
    }
    await login?.();
  };

  const runTask = async () => {
    setStatus("running");
    try {
      const response = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ module: selectedModule })
      });

      const data = await response.json();
      setStatus((data.status as Status) ?? "queued");
      setTaskId(data.taskId ?? null);
    } catch (error) {
      setStatus("failed");
    }
  };

  const userLabel =
    auth?.user?.displayName ??
    auth?.user?.username ??
    auth?.user?.fid ??
    "Anonymous";

  return (
    <main className="page">
      <div className="shell">
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark">Y4</div>
            <div>
              <div>YudaiV4</div>
              <div className="tag">Base mini-app</div>
            </div>
          </div>
          <div className="topbar-actions">
            <StatusPill status={status} />
            <ConnectWallet />
            <button className="btn ghost" onClick={handleAuth}>
              {auth?.isAuthenticated ? "Sign out" : "Farcaster sign in"}
            </button>
          </div>
        </header>

        <section className="hero">
          <div className="hero-card">
            <span className="tag">Task-unified security agent</span>
            <h1>Teach, audit, and safely simulate contract exploits on Base.</h1>
            <p>
              YudaiV4 unifies learning, audits, and PR reviews into one pipeline.
              Every flow runs through Foundry, Anvil, and the security toolchain
              so teams can learn and fix fast.
            </p>
            <div className="hero-grid">
              <span className="pill">Foundry-first workflow</span>
              <span className="pill">Exploit simulation</span>
              <span className="pill">Security tooling</span>
              <span className="pill">Education + fixes</span>
            </div>
          </div>

          <div className="panel">
            <h2>Task console</h2>
            <p>
              Select a module to launch, then kick off a local-only task run. All
              runs stay on Anvil forks or local testnets.
            </p>
            <div>
              <div className="tag">Selected module</div>
              <h3>{selected?.title ?? "Pick a module"}</h3>
              <p>{selected?.description}</p>
              <p className="tag">Focus: {selected?.focus}</p>
            </div>
            <div className="topbar-actions">
              <button className="btn primary" onClick={runTask}>
                Run selected module
              </button>
              <div>
                <div className="tag">Status</div>
                <div>{statusCopy[status]}</div>
                {taskId ? <div className="tag">Task: {taskId}</div> : null}
              </div>
            </div>
          </div>
        </section>

        <section>
          <div className="topbar">
            <h2>Choose a learning path</h2>
            <span className="tag">Task primitives inside</span>
          </div>
          <div className="grid">
            {MODULES.map((module, index) => (
              <div
                key={module.id}
                className="module-card"
                data-selected={module.id === selectedModule}
                style={{ "--delay": `${index * 120}ms` } as CSSProperties}
              >
                <h3>{module.title}</h3>
                <p>{module.description}</p>
                <div className="tag">{module.primitives.join(" | ")}</div>
                <button
                  className="btn ghost"
                  onClick={() => setSelectedModule(module.id)}
                >
                  {module.id === selectedModule ? "Selected" : "Select module"}
                </button>
              </div>
            ))}
          </div>
        </section>

        <section className="pipeline">
          <h2>Unified execution pipeline</h2>
          <div className="pipeline-steps">
            {PIPELINE_STEPS.map((step, index) => (
              <div className="step" key={step}>
                <strong>{index + 1}.</strong>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="safety">
          <h2>Safety and trust boundaries</h2>
          <ul>
            <li>All exploits run on Anvil forks or local testnets only.</li>
            <li>No production signing or mainnet transactions in this flow.</li>
            <li>Command execution is confirm-mode gated on the backend.</li>
            <li>Farcaster identity is verified, MiniKit context is untrusted.</li>
          </ul>
        </section>

        <section className="untrusted">
          <strong>MiniKit context (untrusted metadata)</strong>
          <div>Signed in as: {auth?.isAuthenticated ? userLabel : "Guest"}</div>
          <pre>{JSON.stringify(context ?? {}, null, 2)}</pre>
        </section>

        <footer className="footer">
          YudaiV4 on Base. Built for secure, reproducible smart contract
          learning.
        </footer>
      </div>
    </main>
  );
}
