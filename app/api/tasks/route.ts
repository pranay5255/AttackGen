import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const payload = await request.json().catch(() => ({}));
  const taskId = `task_${Date.now()}`;

  return NextResponse.json({
    status: "queued",
    taskId,
    module: payload?.module ?? "unknown"
  });
}
