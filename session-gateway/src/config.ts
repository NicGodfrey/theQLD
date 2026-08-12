import { existsSync, mkdirSync, readFileSync } from "node:fs";
import path from "node:path";

function loadDotEnv(filePath: string): void {
  if (!existsSync(filePath)) return;
  const text = readFileSync(filePath, "utf8");
  for (const rawLine of text.split("\n")) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq <= 0) continue;
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (process.env[key] === undefined) process.env[key] = value;
  }
}

loadDotEnv(path.resolve(process.cwd(), ".env"));

function num(name: string, fallback: number): number {
  const raw = process.env[name];
  if (raw === undefined || raw === "") return fallback;
  const n = Number(raw);
  if (!Number.isFinite(n)) throw new Error(`Invalid number for ${name}: ${raw}`);
  return n;
}

const dataDir = path.resolve(process.cwd(), process.env.DATA_DIR || "./data");
mkdirSync(path.join(dataDir, "artifacts"), { recursive: true });
mkdirSync(path.join(dataDir, "thinking"), { recursive: true });
mkdirSync(path.join(dataDir, "transcripts"), { recursive: true });

export const config = {
  port: num("PORT", 8787),
  dataDir,
  dbPath: path.join(dataDir, "gateway.db.json"),
  poolRegistryPath: path.join(dataDir, "pool-registry.json"),
  cursorApiKey: process.env.CURSOR_API_KEY || "",
  gatewayApiKey: process.env.GATEWAY_API_KEY || "change-me",
  poolSize: num("POOL_SIZE", 10),
  workerModelId: process.env.WORKER_MODEL_ID || "gpt-5.6-sol-xhigh",
  workerNamePrefix: process.env.WORKER_NAME_PREFIX || "GPT5.6 sol",
  repoUrl: process.env.REPO_URL || "https://github.com/NicGodfrey/theQLD",
  repoRef: process.env.REPO_REF || "main",
  heartbeatTtlMs: num("HEARTBEAT_TTL_MS", 45_000),
  heartbeatSweepMs: num("HEARTBEAT_SWEEP_MS", 5_000),
  usdPerMillionInput: num("USD_PER_MILLION_INPUT_TOKENS", 0),
  usdPerMillionOutput: num("USD_PER_MILLION_OUTPUT_TOKENS", 0),
  orchestratorUrl:
    process.env.ORCHESTRATOR_URL ||
    "https://cursor.com/agents/bc-4c8e891e-d046-4919-a55a-eafe1e62dcea",
  cursorApiBase: process.env.CURSOR_API_BASE || "https://api.cursor.com/v1",
};

export function workerDisplayName(slot: number): string {
  return `${config.workerNamePrefix}-${String(slot).padStart(2, "0")}`;
}

export function requireCursorApiKey(): string {
  if (!config.cursorApiKey) {
    throw new Error(
      "CURSOR_API_KEY is required. Add it to session-gateway/.env (Dashboard → API Keys).",
    );
  }
  return config.cursorApiKey;
}
