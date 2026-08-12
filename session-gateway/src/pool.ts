import { existsSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { config, workerDisplayName } from "./config.js";
import { cursorClient, CursorApiError } from "./cursorClient.js";
import { store } from "./store.js";
import type { PoolRegistryFile, WorkerSlot } from "./types.js";

function nowIso(): string {
  return new Date().toISOString();
}

function writeRegistry(): void {
  const db = store.get();
  const file: PoolRegistryFile = {
    version: 1,
    orchestratorUrl: config.orchestratorUrl,
    modelId: config.workerModelId,
    updatedAt: nowIso(),
    workers: db.workers
      .filter((w) => w.bcId && w.url)
      .map((w) => ({
        slot: w.slot,
        name: w.name,
        bcId: w.bcId!,
        url: w.url!,
        source: "api" as const,
      })),
  };
  const tmp = `${config.poolRegistryPath}.tmp`;
  writeFileSync(tmp, JSON.stringify(file, null, 2));
  renameSync(tmp, config.poolRegistryPath);
}

export function loadRegistryIntoStore(): void {
  if (!existsSync(config.poolRegistryPath)) return;
  const file = JSON.parse(
    readFileSync(config.poolRegistryPath, "utf8"),
  ) as PoolRegistryFile;
  store.update((db) => {
    for (const w of file.workers) {
      const slot = db.workers.find((x) => x.slot === w.slot);
      if (!slot) continue;
      if (slot.status === "BOUND" || slot.status === "BUSY") continue;
      slot.bcId = w.bcId;
      slot.url = w.url;
      slot.name = w.name || workerDisplayName(w.slot);
      slot.modelId = file.modelId || config.workerModelId;
      slot.status = "FREE";
      slot.updatedAt = nowIso();
    }
  });
}

export function listWorkers(): WorkerSlot[] {
  return store.get().workers;
}

export async function hotStartMissingSlots(
  slots?: number[],
): Promise<WorkerSlot[]> {
  const wanted =
    slots ??
    Array.from({ length: config.poolSize }, (_, i) => i + 1);

  for (const slotNum of wanted) {
    const worker = store.get().workers.find((w) => w.slot === slotNum);
    if (!worker) continue;
    if (worker.bcId && worker.status !== "ERROR") continue;

    store.update((db) => {
      const w = db.workers.find((x) => x.slot === slotNum)!;
      w.status = "RESETTING";
      w.lastError = null;
      w.updatedAt = nowIso();
    });

    try {
      const name = workerDisplayName(slotNum);
      const created = await cursorClient.createWorker(slotNum, name);
      store.update((db) => {
        const w = db.workers.find((x) => x.slot === slotNum)!;
        w.bcId = created.agent.id;
        w.url = created.agent.url;
        w.name = name;
        w.generation += 1;
        w.status = "FREE";
        w.sessionId = null;
        w.updatedAt = nowIso();
      });
    } catch (err) {
      const message =
        err instanceof CursorApiError
          ? `${err.message} ${err.body}`
          : err instanceof Error
            ? err.message
            : String(err);
      store.update((db) => {
        const w = db.workers.find((x) => x.slot === slotNum)!;
        w.status = "ERROR";
        w.lastError = message;
        w.updatedAt = nowIso();
      });
    }
  }

  writeRegistry();
  return listWorkers();
}

export async function hardResetWorker(
  slotNum: number,
  reason: string,
): Promise<WorkerSlot> {
  const worker = store.get().workers.find((w) => w.slot === slotNum);
  if (!worker) throw new Error(`Unknown slot ${slotNum}`);

  const oldBcId = worker.bcId;
  store.update((db) => {
    const w = db.workers.find((x) => x.slot === slotNum)!;
    w.status = "RESETTING";
    w.sessionId = null;
    w.lastError = null;
    w.updatedAt = nowIso();
  });

  if (oldBcId) {
    try {
      await cursorClient.archive(oldBcId);
    } catch {
      // best-effort
    }
    try {
      await cursorClient.delete(oldBcId);
    } catch {
      // archive may be enough if delete denied
    }
  }

  try {
    const name = workerDisplayName(slotNum);
    const created = await cursorClient.createWorker(slotNum, name);
    store.update((db) => {
      const w = db.workers.find((x) => x.slot === slotNum)!;
      w.bcId = created.agent.id;
      w.url = created.agent.url;
      w.name = name;
      w.generation += 1;
      w.status = "FREE";
      w.sessionId = null;
      w.updatedAt = nowIso();
      w.lastError = null;
    });
  } catch (err) {
    const message =
      err instanceof Error ? err.message : String(err);
    store.update((db) => {
      const w = db.workers.find((x) => x.slot === slotNum)!;
      w.bcId = null;
      w.url = null;
      w.status = "ERROR";
      w.lastError = `reset failed (${reason}): ${message}`;
      w.updatedAt = nowIso();
    });
  }

  writeRegistry();
  return store.get().workers.find((w) => w.slot === slotNum)!;
}

export function registerExternalWorker(params: {
  slot: number;
  bcId: string;
  url: string;
  name?: string;
  source?: "api" | "task" | "manual";
}): WorkerSlot {
  store.update((db) => {
    const w = db.workers.find((x) => x.slot === params.slot);
    if (!w) throw new Error(`Unknown slot ${params.slot}`);
    if (w.status === "BOUND" || w.status === "BUSY") {
      throw new Error(`Slot ${params.slot} is leased; release first`);
    }
    w.bcId = params.bcId;
    w.url = params.url;
    w.name = params.name || workerDisplayName(params.slot);
    w.status = "FREE";
    w.sessionId = null;
    w.generation += 1;
    w.lastError = null;
    w.updatedAt = nowIso();
  });

  // Merge into registry preserving source tags
  let existing: PoolRegistryFile = {
    version: 1,
    orchestratorUrl: config.orchestratorUrl,
    modelId: config.workerModelId,
    updatedAt: nowIso(),
    workers: [],
  };
  if (existsSync(config.poolRegistryPath)) {
    existing = JSON.parse(
      readFileSync(config.poolRegistryPath, "utf8"),
    ) as PoolRegistryFile;
  }
  existing.workers = existing.workers.filter((w) => w.slot !== params.slot);
  existing.workers.push({
    slot: params.slot,
    name: params.name || workerDisplayName(params.slot),
    bcId: params.bcId,
    url: params.url,
    source: params.source || "manual",
    readyAt: nowIso(),
  });
  existing.workers.sort((a, b) => a.slot - b.slot);
  existing.updatedAt = nowIso();
  writeFileSync(config.poolRegistryPath, JSON.stringify(existing, null, 2));

  return store.get().workers.find((w) => w.slot === params.slot)!;
}
