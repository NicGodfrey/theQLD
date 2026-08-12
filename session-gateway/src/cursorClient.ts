import { config, requireCursorApiKey } from "./config.js";
import type { TokenUsage } from "./types.js";

export class CursorApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly body: string,
  ) {
    super(message);
    this.name = "CursorApiError";
  }
}

async function api<T>(
  method: string,
  path: string,
  body?: unknown,
  init?: RequestInit,
): Promise<T> {
  const key = requireCursorApiKey();
  const headers: Record<string, string> = {
    Authorization: `Bearer ${key}`,
    Accept: "application/json",
  };
  if (body !== undefined) headers["Content-Type"] = "application/json";

  const res = await fetch(`${config.cursorApiBase}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    ...init,
  });

  const text = await res.text();
  if (!res.ok) {
    throw new CursorApiError(
      `Cursor API ${method} ${path} failed: ${res.status}`,
      res.status,
      text,
    );
  }
  if (!text) return undefined as T;
  return JSON.parse(text) as T;
}

export interface CreatedAgent {
  agent: {
    id: string;
    name: string;
    status: string;
    url: string;
    latestRunId?: string;
  };
  run: {
    id: string;
    agentId: string;
    status: string;
  };
}

export interface CreatedRun {
  run: {
    id: string;
    agentId: string;
    status: string;
  };
}

export interface RunDetail {
  id: string;
  agentId: string;
  status: string;
  result?: string;
  durationMs?: number;
}

export interface UsageResponse {
  totalUsage: TokenUsage;
  runs: Array<{
    id: string;
    usageUuid?: string;
    usage: TokenUsage;
  }>;
}

const BOOT_PROMPT = (slot: number, name: string) =>
  `You are worker slot ${slot}/10 named "${name}" in a remote session pool.

BOOT PROTOCOL (do only this, then stop):
1. Reply with exactly one line: READY slot=${slot} name=${name}
2. Do NOT modify any repository files. Do NOT create branches, commits, or PRs. Do NOT run destructive commands.
3. Remain idle after READY. Wait for follow-up user questions; when asked a question, answer it helpfully and still avoid repo mutations unless explicitly instructed to change code.
4. If a follow-up says SESSION_RESET, reply RESET_ACK slot=${slot} and treat prior user chat as cleared.

This is a hot-standby boot only.`;

export const cursorClient = {
  createWorker(slot: number, name: string): Promise<CreatedAgent> {
    return api<CreatedAgent>("POST", "/agents", {
      prompt: { text: BOOT_PROMPT(slot, name) },
      model: { id: config.workerModelId },
      name,
      repos: [{ url: config.repoUrl, startingRef: config.repoRef }],
      autoCreatePR: false,
    });
  },

  createRun(agentId: string, text: string): Promise<CreatedRun> {
    return api<CreatedRun>("POST", `/agents/${agentId}/runs`, {
      prompt: { text },
    });
  },

  getRun(agentId: string, runId: string): Promise<RunDetail> {
    return api<RunDetail>("GET", `/agents/${agentId}/runs/${runId}`);
  },

  getUsage(agentId: string, runId?: string): Promise<UsageResponse> {
    const q = runId ? `?runId=${encodeURIComponent(runId)}` : "";
    return api<UsageResponse>("GET", `/agents/${agentId}/usage${q}`);
  },

  archive(agentId: string): Promise<unknown> {
    return api("POST", `/agents/${agentId}/archive`);
  },

  delete(agentId: string): Promise<unknown> {
    return api("DELETE", `/agents/${agentId}`);
  },

  async streamRun(
    agentId: string,
    runId: string,
    onEvent: (event: string, data: unknown, id?: string) => void | Promise<void>,
    signal?: AbortSignal,
  ): Promise<void> {
    const key = requireCursorApiKey();
    const res = await fetch(
      `${config.cursorApiBase}/agents/${agentId}/runs/${runId}/stream`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${key}`,
          Accept: "text/event-stream",
        },
        signal,
      },
    );
    if (!res.ok || !res.body) {
      const body = await res.text();
      throw new CursorApiError(
        `Cursor stream failed: ${res.status}`,
        res.status,
        body,
      );
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let eventName = "message";
    let dataLines: string[] = [];
    let id: string | undefined;

    const flush = async () => {
      if (!dataLines.length) {
        eventName = "message";
        id = undefined;
        return;
      }
      const raw = dataLines.join("\n");
      dataLines = [];
      let data: unknown = raw;
      try {
        data = JSON.parse(raw);
      } catch {
        // keep string
      }
      await onEvent(eventName, data, id);
      eventName = "message";
      id = undefined;
    };

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split(/\r?\n/);
      buffer = parts.pop() || "";
      for (const line of parts) {
        if (line === "") {
          await flush();
          continue;
        }
        if (line.startsWith(":")) continue;
        if (line.startsWith("event:")) {
          eventName = line.slice(6).trim();
          continue;
        }
        if (line.startsWith("data:")) {
          dataLines.push(line.slice(5).trimStart());
          continue;
        }
        if (line.startsWith("id:")) {
          id = line.slice(3).trim();
        }
      }
    }
    await flush();
  },
};
