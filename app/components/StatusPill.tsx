import type { ReactNode } from "react";

export type Status = "idle" | "running" | "queued" | "failed" | "complete";

const labels: Record<Status, ReactNode> = {
  idle: "Idle",
  running: "Running",
  queued: "Queued",
  failed: "Failed",
  complete: "Complete"
};

export default function StatusPill({ status }: { status: Status }) {
  return (
    <span className="status-pill" data-status={status}>
      {labels[status]}
    </span>
  );
}
