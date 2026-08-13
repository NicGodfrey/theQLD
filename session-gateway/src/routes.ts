import { Hono } from "hono";
import {
  handleAnthropicMessages,
  handleAnthropicModels,
} from "./anthropicProxy.js";
import { config } from "./config.js";
import { sessionInvoice } from "./billing.js";
import {
  hotStartMissingSlots,
  listWorkers,
  loadRegistryIntoStore,
  registerExternalWorker,
} from "./pool.js";
import {
  acquireSession,
  chat,
  heartbeat,
  releaseSession,
  SessionError,
  sweepExpiredSessions,
} from "./sessionService.js";
import { store } from "./store.js";

type Vars = { requestId: string };

function auth(c: {
  req: { header: (name: string) => string | undefined };
}): boolean {
  const header = c.req.header("authorization") || "";
  const key = c.req.header("x-api-key") || "";
  if (key && key === config.gatewayApiKey) return true;
  if (header.startsWith("Bearer ") && header.slice(7) === config.gatewayApiKey) {
    return true;
  }
  return false;
}

export function buildApp() {
  const app = new Hono<{ Variables: Vars }>();

  app.use("*", async (c, next) => {
    c.set("requestId", crypto.randomUUID());
    await next();
  });

  app.get("/health", (c) =>
    c.json({
      ok: true,
      orchestratorUrl: config.orchestratorUrl,
      poolSize: config.poolSize,
      modelId: config.workerModelId,
      cursorApiConfigured: Boolean(config.cursorApiKey),
    }),
  );

  app.get("/", (c) =>
    c.json({
      service: "session-gateway",
      orchestratorUrl: config.orchestratorUrl,
      endpoints: [
        "GET /health",
        "GET /v1/models  (Anthropic-compatible for Claude Code)",
        "POST /v1/messages  (Anthropic-compatible for Claude Code)",
        "GET /v1/pool",
        "POST /v1/pool/hot-start",
        "POST /v1/pool/register",
        "POST /v1/session/acquire",
        "POST /v1/session/:id/heartbeat",
        "POST /v1/session/:id/chat",
        "POST /v1/session/:id/release",
        "GET /v1/session/:id/invoice",
        "GET /v1/session/:id/transcript",
      ],
    }),
  );

  app.use("/v1/*", async (c, next) => {
    if (!auth(c)) {
      return c.json(
        {
          type: "error",
          error: {
            type: "authentication_error",
            message: "invalid gateway token",
          },
        },
        401,
      );
    }
    await next();
  });

  app.get("/v1/models", (c) => handleAnthropicModels(c));
  app.post("/v1/messages", (c) => handleAnthropicMessages(c));

  app.get("/v1/pool", (c) => {
    loadRegistryIntoStore();
    return c.json({
      orchestratorUrl: config.orchestratorUrl,
      modelId: config.workerModelId,
      workers: listWorkers(),
    });
  });

  app.post("/v1/pool/hot-start", async (c) => {
    const body = await c.req.json().catch(() => ({}));
    const slots = Array.isArray(body.slots) ? body.slots.map(Number) : undefined;
    const workers = await hotStartMissingSlots(slots);
    return c.json({ workers });
  });

  app.post("/v1/pool/register", async (c) => {
    const body = await c.req.json();
    const worker = registerExternalWorker({
      slot: Number(body.slot),
      bcId: String(body.bcId),
      url: String(body.url),
      name: body.name ? String(body.name) : undefined,
      source: body.source || "manual",
    });
    return c.json({ worker });
  });

  app.post("/v1/session/acquire", async (c) => {
    try {
      const body = await c.req.json();
      const clientId = String(body.clientId || "");
      if (!clientId) return c.json({ error: "clientId required" }, 400);
      const preferredSlot =
        body.preferredSlot != null ? Number(body.preferredSlot) : undefined;
      return c.json(
        acquireSession(clientId, {
          preferredSlot,
          reuse: Boolean(body.reuse),
        }),
      );
    } catch (err) {
      if (err instanceof SessionError) {
        return c.json(
          { error: err.code, message: err.message },
          err.status as 400 | 404 | 409 | 500 | 503,
        );
      }
      throw err;
    }
  });

  app.post("/v1/session/:id/heartbeat", async (c) => {
    try {
      return c.json(heartbeat(c.req.param("id")));
    } catch (err) {
      if (err instanceof SessionError) {
        return c.json(
          { error: err.code, message: err.message },
          err.status as 400 | 404 | 409 | 500 | 503,
        );
      }
      throw err;
    }
  });

  app.post("/v1/session/:id/chat", async (c) => {
    try {
      const body = await c.req.json();
      const message = String(body.message || "");
      if (!message) return c.json({ error: "message required" }, 400);
      const result = await chat(c.req.param("id"), message);
      return c.json(result);
    } catch (err) {
      if (err instanceof SessionError) {
        return c.json(
          { error: err.code, message: err.message },
          err.status as 400 | 404 | 409 | 500 | 503,
        );
      }
      return c.json(
        {
          error: "chat_failed",
          message: err instanceof Error ? err.message : String(err),
        },
        500,
      );
    }
  });

  app.post("/v1/session/:id/release", async (c) => {
    try {
      const body = await c.req.json().catch(() => ({}));
      const reason = String(body.reason || "client_release");
      const invoice = await releaseSession(c.req.param("id"), reason, {
        reset: body.reset !== false,
      });
      return c.json({ ok: true, invoice });
    } catch (err) {
      if (err instanceof SessionError) {
        return c.json(
          { error: err.code, message: err.message },
          err.status as 400 | 404 | 409 | 500 | 503,
        );
      }
      throw err;
    }
  });

  app.get("/v1/session/:id/invoice", (c) => {
    return c.json(sessionInvoice(c.req.param("id")));
  });

  app.get("/v1/session/:id/transcript", (c) => {
    const sessionId = c.req.param("id");
    const db = store.get();
    return c.json({
      session: db.sessions.find((s) => s.sessionId === sessionId) || null,
      turns: db.turns.filter((t) => t.sessionId === sessionId),
      artifacts: db.artifacts.filter((a) => a.sessionId === sessionId),
    });
  });

  app.post("/v1/admin/sweep", async (c) => {
    const released = await sweepExpiredSessions();
    return c.json({ released });
  });

  return app;
}
