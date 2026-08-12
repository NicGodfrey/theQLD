import { existsSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { config } from "./config.js";
import type { DbState, WorkerSlot } from "./types.js";
import { workerDisplayName } from "./config.js";

function emptyWorkers(): WorkerSlot[] {
  const now = new Date().toISOString();
  return Array.from({ length: config.poolSize }, (_, i) => {
    const slot = i + 1;
    return {
      slot,
      name: workerDisplayName(slot),
      bcId: null,
      url: null,
      modelId: config.workerModelId,
      status: "FREE",
      sessionId: null,
      generation: 0,
      lastError: null,
      createdAt: now,
      updatedAt: now,
    };
  });
}

function defaultState(): DbState {
  return { workers: emptyWorkers(), sessions: [], turns: [], artifacts: [] };
}

export class JsonStore {
  private state: DbState;

  constructor(private readonly filePath = config.dbPath) {
    this.state = this.load();
  }

  private load(): DbState {
    if (!existsSync(this.filePath)) return defaultState();
    const parsed = JSON.parse(readFileSync(this.filePath, "utf8")) as DbState;
    if (!parsed.workers?.length) parsed.workers = emptyWorkers();
    while (parsed.workers.length < config.poolSize) {
      const slot = parsed.workers.length + 1;
      const now = new Date().toISOString();
      parsed.workers.push({
        slot,
        name: workerDisplayName(slot),
        bcId: null,
        url: null,
        modelId: config.workerModelId,
        status: "FREE",
        sessionId: null,
        generation: 0,
        lastError: null,
        createdAt: now,
        updatedAt: now,
      });
    }
    return parsed;
  }

  save(): void {
    const tmp = `${this.filePath}.tmp`;
    writeFileSync(tmp, JSON.stringify(this.state, null, 2));
    renameSync(tmp, this.filePath);
  }

  get(): DbState {
    return this.state;
  }

  update(mutator: (state: DbState) => void): DbState {
    mutator(this.state);
    this.save();
    return this.state;
  }
}

export const store = new JsonStore();
