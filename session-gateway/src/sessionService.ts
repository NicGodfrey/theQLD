import { v4 as uuidv4 } from "uuid";
import { config } from "./config.js";
import { settleTurnUsage, ZERO_USAGE, sessionInvoice } from "./billing.js";
import { cursorClient } from "./cursorClient.js";
import { hardResetWorker } from "./pool.js";
import { store } from "./store.js";
import { appendArtifact } from "./transcript.js";

function nowIso(): string {
  return new Date().toISOString();
}

export class SessionError extends Error {
  constructor(
    message: string,
    readonly code: string,
    readonly status = 400,
  ) {
    super(message);
    this.name = "SessionError";
  }
}

export function acquireSession(clientId: string) {
  const active = store
    .get()
    .sessions.find((s) => s.clientId === clientId && s.status === "ACTIVE");
  if (active) {
    throw new SessionError(
      "This client already holds a session; one session may bind only one worker",
      "session_exists",
      409,
    );
  }

  const free = store
    .get()
    .workers.find((w) => w.status === "FREE" && w.bcId && w.url);
  if (!free) {
    throw new SessionError("No free GPT5.6 sol workers", "pool_full", 503);
  }

  const sessionId = uuidv4();
  const acquiredAt = nowIso();

  store.update((db) => {
    const w = db.workers.find((x) => x.slot === free.slot)!;
    w.status = "BOUND";
    w.sessionId = sessionId;
    w.updatedAt = acquiredAt;
    db.sessions.push({
      sessionId,
      clientId,
      workerSlot: w.slot,
      workerBcId: w.bcId!,
      status: "ACTIVE",
      acquiredAt,
      lastHeartbeatAt: acquiredAt,
      releasedAt: null,
      releaseReason: null,
    });
  });

  const worker = store.get().workers.find((w) => w.slot === free.slot)!;
  return {
    sessionId,
    worker: {
      slot: worker.slot,
      name: worker.name,
      bcId: worker.bcId,
      url: worker.url,
      modelId: worker.modelId,
    },
    heartbeatTtlMs: config.heartbeatTtlMs,
    orchestratorUrl: config.orchestratorUrl,
  };
}

export function heartbeat(sessionId: string) {
  const session = store.get().sessions.find((s) => s.sessionId === sessionId);
  if (!session || session.status !== "ACTIVE") {
    throw new SessionError("Session not active", "session_inactive", 404);
  }
  const ts = nowIso();
  store.update((db) => {
    const s = db.sessions.find((x) => x.sessionId === sessionId)!;
    s.lastHeartbeatAt = ts;
  });
  return { sessionId, lastHeartbeatAt: ts };
}

export async function releaseSession(
  sessionId: string,
  reason: string,
  opts?: { reset?: boolean },
) {
  const session = store.get().sessions.find((s) => s.sessionId === sessionId);
  if (!session) throw new SessionError("Unknown session", "not_found", 404);
  if (session.status !== "ACTIVE") {
    return sessionInvoice(sessionId);
  }

  const releasedAt = nowIso();
  store.update((db) => {
    const s = db.sessions.find((x) => x.sessionId === sessionId)!;
    s.status =
      reason === "heartbeat_timeout"
        ? "TIMED_OUT"
        : reason === "reset"
          ? "RESET"
          : "RELEASED";
    s.releasedAt = releasedAt;
    s.releaseReason = reason;
    const w = db.workers.find((x) => x.slot === s.workerSlot);
    if (w) {
      w.status = "RESETTING";
      w.sessionId = null;
      w.updatedAt = releasedAt;
    }
  });

  const shouldReset = opts?.reset !== false;
  if (shouldReset) {
    await hardResetWorker(session.workerSlot, reason);
  } else {
    store.update((db) => {
      const w = db.workers.find((x) => x.slot === session.workerSlot);
      if (w) {
        w.status = "FREE";
        w.updatedAt = nowIso();
      }
    });
  }

  return sessionInvoice(sessionId);
}

export async function chat(sessionId: string, message: string) {
  const session = store.get().sessions.find((s) => s.sessionId === sessionId);
  if (!session || session.status !== "ACTIVE") {
    throw new SessionError("Session not active", "session_inactive", 404);
  }
  const worker = store.get().workers.find((w) => w.slot === session.workerSlot);
  if (!worker?.bcId) {
    throw new SessionError("Worker missing", "worker_missing", 500);
  }
  if (worker.status === "BUSY") {
    throw new SessionError("Worker busy", "worker_busy", 409);
  }

  const turnId = uuidv4();
  const startedAt = nowIso();
  store.update((db) => {
    const w = db.workers.find((x) => x.slot === worker.slot)!;
    w.status = "BUSY";
    w.updatedAt = startedAt;
    db.turns.push({
      turnId,
      sessionId,
      workerSlot: worker.slot,
      workerBcId: worker.bcId!,
      runId: null,
      modelId: worker.modelId,
      status: "RUNNING",
      startedAt,
      endedAt: null,
      usage: { ...ZERO_USAGE },
      estimatedUsdCents: 0,
      settled: false,
      error: null,
    });
  });

  appendArtifact({
    turnId,
    sessionId,
    kind: "user",
    content: message,
  });

  let assistantText = "";
  let thinkingText = "";
  let runId = "";

  try {
    const created = await cursorClient.createRun(worker.bcId, message);
    runId = created.run.id;
    store.update((db) => {
      const t = db.turns.find((x) => x.turnId === turnId)!;
      t.runId = runId;
    });

    await cursorClient.streamRun(worker.bcId, runId, async (event, data) => {
      if (event === "assistant" && data && typeof data === "object") {
        const text = String((data as { text?: string }).text || "");
        if (text) {
          assistantText += text;
          appendArtifact({ turnId, sessionId, kind: "assistant", content: text });
        }
      } else if (event === "thinking" && data && typeof data === "object") {
        const text = String((data as { text?: string }).text || "");
        if (text) {
          thinkingText += text;
          appendArtifact({ turnId, sessionId, kind: "thinking", content: text });
        }
      } else if (event === "tool_call") {
        appendArtifact({ turnId, sessionId, kind: "tool_call", content: data as object });
      } else if (event === "status" || event === "result") {
        appendArtifact({ turnId, sessionId, kind: "status", content: data as object });
        if (
          event === "result" &&
          data &&
          typeof data === "object" &&
          typeof (data as { text?: string }).text === "string"
        ) {
          assistantText = (data as { text: string }).text || assistantText;
        }
      }
    });

    let usage = ZERO_USAGE;
    try {
      usage = await settleTurnUsage(turnId, worker.bcId, runId);
    } catch {
      // usage may lag; leave unsettled
    }

    const endedAt = nowIso();
    store.update((db) => {
      const t = db.turns.find((x) => x.turnId === turnId)!;
      t.status = "FINISHED";
      t.endedAt = endedAt;
      const w = db.workers.find((x) => x.slot === worker.slot)!;
      if (w.sessionId === sessionId) w.status = "BOUND";
      w.updatedAt = endedAt;
      const s = db.sessions.find((x) => x.sessionId === sessionId);
      if (s && s.status === "ACTIVE") s.lastHeartbeatAt = endedAt;
    });

    return {
      turnId,
      runId,
      assistantText,
      thinkingChars: thinkingText.length,
      usage,
      invoicePreview: sessionInvoice(sessionId),
    };
  } catch (err) {
    const messageText = err instanceof Error ? err.message : String(err);
    store.update((db) => {
      const t = db.turns.find((x) => x.turnId === turnId)!;
      t.status = "ERROR";
      t.endedAt = nowIso();
      t.error = messageText;
      const w = db.workers.find((x) => x.slot === worker.slot)!;
      if (w.sessionId === sessionId) w.status = "BOUND";
      w.updatedAt = nowIso();
    });
    appendArtifact({
      turnId,
      sessionId,
      kind: "system",
      content: { error: messageText },
    });
    throw err;
  }
}

export async function sweepExpiredSessions(): Promise<string[]> {
  const cutoff = Date.now() - config.heartbeatTtlMs;
  const expired = store
    .get()
    .sessions.filter(
      (s) =>
        s.status === "ACTIVE" &&
        new Date(s.lastHeartbeatAt).getTime() < cutoff,
    );
  const released: string[] = [];
  for (const s of expired) {
    await releaseSession(s.sessionId, "heartbeat_timeout");
    released.push(s.sessionId);
  }
  return released;
}
