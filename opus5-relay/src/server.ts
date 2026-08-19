import express, { type NextFunction, type Request, type Response } from "express";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { v4 as uuidv4 } from "uuid";
import { z } from "zod";
import { CursorAgentsClient } from "./cursor-api.js";
import { SessionStore, defaultStorePath } from "./session-store.js";

const PORT = Number(process.env.PORT ?? 8787);
const AUTH_TOKEN = process.env.RELAY_AUTH_TOKEN?.trim();
const CURSOR_API_KEY = process.env.CURSOR_API_KEY?.trim();
const DATA_DIR = process.env.DATA_DIR ?? "./data";

if (!CURSOR_API_KEY) {
  console.error("缺少 CURSOR_API_KEY");
  process.exit(1);
}

if (!AUTH_TOKEN) {
  console.error("缺少 RELAY_AUTH_TOKEN（客户端访问令牌）");
  process.exit(1);
}

const client = new CursorAgentsClient(CURSOR_API_KEY);
const sessions = new SessionStore(defaultStorePath(DATA_DIR));

const askSchema = z.object({
  message: z.string().min(1),
  session_id: z.string().optional(),
  reset: z.boolean().optional(),
  repo_url: z.string().url().optional(),
  starting_ref: z.string().optional(),
});

const app = express();
app.use(express.json({ limit: "2mb" }));

function auth(req: Request, res: Response, next: NextFunction): void {
  if (req.path === "/health" || req.path === "/api/v1/health") {
    next();
    return;
  }

  const header = req.headers.authorization ?? "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : header;
  const queryToken =
    typeof req.query.token === "string" ? req.query.token : undefined;

  if (token === AUTH_TOKEN || queryToken === AUTH_TOKEN) {
    next();
    return;
  }

  res.status(401).json({ error: "Unauthorized" });
}

app.use(auth);

app.get("/health", (_req, res) => {
  res.json({ ok: true, service: "opus5-relay" });
});

app.get("/api/v1/health", (_req, res) => {
  res.json({ ok: true, service: "opus5-relay" });
});

app.post("/api/v1/ask", async (req, res) => {
  try {
    const input = askSchema.parse(req.body);
    const sessionId = input.session_id ?? uuidv4();
    const existing = input.reset ? undefined : await sessions.get(sessionId);

    const result = await client.askOpus5({
      message: input.message,
      reset: input.reset,
      agentId: existing?.agentId,
      repoUrl: input.repo_url ?? process.env.CURSOR_OPUS5_REPO_URL,
      startingRef: input.starting_ref ?? process.env.CURSOR_OPUS5_STARTING_REF,
    });

    await sessions.save({
      sessionId,
      agentId: result.agentId,
      agentUrl: result.agentUrl,
      updatedAt: new Date().toISOString(),
    });

    res.json({
      session_id: sessionId,
      reply: result.text,
      agent_id: result.agentId,
      run_id: result.runId,
      agent_url: result.agentUrl,
      created_agent: result.createdAgent,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    res.status(500).json({ error: message });
  }
});

app.get("/api/v1/session/:id", async (req, res) => {
  const record = await sessions.get(req.params.id);
  if (!record) {
    res.status(404).json({ error: "session not found" });
    return;
  }

  let agentStatus: unknown = null;
  if (record.agentId) {
    try {
      agentStatus = await client.getAgent(record.agentId);
    } catch {
      agentStatus = null;
    }
  }

  res.json({ session: record, agent: agentStatus });
});

app.post("/api/v1/reset", async (req, res) => {
  const sessionId = z.object({ session_id: z.string() }).parse(req.body).session_id;
  await sessions.delete(sessionId);
  res.json({ ok: true, session_id: sessionId });
});

const publicDir = join(fileURLToPath(new URL(".", import.meta.url)), "..", "public");
app.use(express.static(publicDir));

app.listen(PORT, () => {
  console.log(`opus5-relay listening on http://0.0.0.0:${PORT}`);
  console.log(`Web UI: http://localhost:${PORT}/`);
  console.log(`API: POST /api/v1/ask`);
});
