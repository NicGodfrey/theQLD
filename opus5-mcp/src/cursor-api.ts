import { OPUS5_BOOTSTRAP_PROMPT } from "./persona.js";

const API_BASE = "https://api.cursor.com";

export type RunStatus =
  | "CREATING"
  | "RUNNING"
  | "FINISHED"
  | "ERROR"
  | "CANCELLED"
  | "EXPIRED";

export interface ModelSelection {
  id: string;
  params?: Array<{ id: string; value: string }>;
}

export interface AgentSummary {
  id: string;
  status: string;
  latestRunId?: string;
  url?: string;
}

export interface RunSummary {
  id: string;
  agentId: string;
  status: RunStatus;
  result?: string;
  durationMs?: number;
}

export interface ModelCatalogItem {
  id: string;
  displayName?: string;
  aliases?: string[];
  parameters?: Array<{
    id: string;
    values?: Array<{ value: string; displayName?: string }>;
  }>;
  variants?: Array<{
    params: Array<{ id: string; value: string }>;
    displayName?: string;
    isDefault?: boolean;
  }>;
}

export class CursorAgentsClient {
  constructor(private readonly apiKey: string) {}

  private async request<T>(
    path: string,
    init?: RequestInit,
  ): Promise<T> {
    const auth = Buffer.from(`${this.apiKey}:`).toString("base64");
    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        Authorization: `Basic ${auth}`,
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });

    if (!response.ok) {
      const body = await response.text();
      throw new Error(`Cursor API ${response.status} ${response.statusText}: ${body}`);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  }

  async listModels(): Promise<ModelCatalogItem[]> {
    const data = await this.request<{ items: ModelCatalogItem[] }>("/v1/models");
    return data.items ?? [];
  }

  async resolveOpus5Model(): Promise<ModelSelection> {
    const override = process.env.CURSOR_OPUS5_MODEL_ID?.trim();
    if (override) {
      const params = parseModelParams(process.env.CURSOR_OPUS5_MODEL_PARAMS);
      return { id: override, ...(params.length ? { params } : {}) };
    }

    const items = await this.listModels();
    const opus = items.find((item) => {
      const haystack = [
        item.id,
        item.displayName ?? "",
        ...(item.aliases ?? []),
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes("opus") && haystack.includes("5");
    });

    if (!opus) {
      throw new Error(
        "未在 GET /v1/models 中找到 Opus 5。请设置环境变量 CURSOR_OPUS5_MODEL_ID（可选 CURSOR_OPUS5_MODEL_PARAMS）。",
      );
    }

    const preferredVariant =
      opus.variants?.find((variant) => {
        const label = `${variant.displayName ?? ""} ${JSON.stringify(variant.params)}`.toLowerCase();
        return label.includes("high") || label.includes("thinking");
      }) ??
      opus.variants?.find((variant) => variant.isDefault) ??
      opus.variants?.[0];

    return {
      id: opus.id,
      ...(preferredVariant?.params?.length
        ? { params: preferredVariant.params }
        : {}),
    };
  }

  async createAgent(options: {
    prompt: string;
    name?: string;
    model: ModelSelection;
    repoUrl?: string;
    startingRef?: string;
  }): Promise<{ agent: AgentSummary; run: RunSummary }> {
    const body: Record<string, unknown> = {
      name: options.name ?? "Opus 5 主模型",
      model: options.model,
      prompt: { text: options.prompt },
    };

    if (options.repoUrl) {
      body.repos = [
        {
          url: options.repoUrl,
          startingRef: options.startingRef ?? "main",
        },
      ];
    }

    return this.request("/v1/agents", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  async createRun(agentId: string, prompt: string): Promise<RunSummary> {
    const data = await this.request<{ run: RunSummary }>(
      `/v1/agents/${agentId}/runs`,
      {
        method: "POST",
        body: JSON.stringify({ prompt: { text: prompt } }),
      },
    );
    return data.run;
  }

  async getRun(agentId: string, runId: string): Promise<RunSummary> {
    return this.request<RunSummary>(`/v1/agents/${agentId}/runs/${runId}`);
  }

  async getAgent(agentId: string): Promise<AgentSummary> {
    return this.request<AgentSummary>(`/v1/agents/${agentId}`);
  }

  async waitForRun(
    agentId: string,
    runId: string,
    timeoutMs = 10 * 60 * 1000,
    pollMs = 3000,
  ): Promise<RunSummary> {
    const started = Date.now();

    while (Date.now() - started < timeoutMs) {
      const run = await this.getRun(agentId, runId);
      if (isTerminal(run.status)) {
        return run;
      }
      await sleep(pollMs);
    }

    throw new Error(`等待 Opus 5 响应超时（${timeoutMs}ms），run=${runId}`);
  }

  async askOpus5(options: {
    message: string;
    agentId?: string;
    reset?: boolean;
    repoUrl?: string;
    startingRef?: string;
  }): Promise<{
    agentId: string;
    runId: string;
    status: RunStatus;
    text: string;
    agentUrl?: string;
    createdAgent: boolean;
  }> {
    const model = await this.resolveOpus5Model();
    let agentId = options.reset ? undefined : options.agentId;
    let createdAgent = false;
    let run: RunSummary;

    if (!agentId) {
      const created = await this.createAgent({
        prompt: `${OPUS5_BOOTSTRAP_PROMPT}\n\n用户首条消息：\n${options.message}`,
        model,
        repoUrl: options.repoUrl,
        startingRef: options.startingRef,
      });
      agentId = created.agent.id;
      run = created.run;
      createdAgent = true;
    } else {
      try {
        run = await this.createRun(agentId, options.message);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        if (!message.includes("409")) {
          throw error;
        }
        const agent = await this.getAgent(agentId);
        if (agent.latestRunId) {
          const latest = await this.getRun(agentId, agent.latestRunId);
          if (!isTerminal(latest.status)) {
            throw new Error(
              `Agent 正忙（status=${latest.status}）。请稍后再试，或设置 reset=true 创建新会话。`,
            );
          }
        }
        run = await this.createRun(agentId, options.message);
      }
    }

    const finished = await this.waitForRun(agentId, run.id);
    const agent = await this.getAgent(agentId);

    if (finished.status === "ERROR") {
      throw new Error(
        `Opus 5 run 失败：${finished.result ?? "unknown error"}`,
      );
    }

    if (finished.status === "CANCELLED" || finished.status === "EXPIRED") {
      throw new Error(`Opus 5 run 未成功完成：status=${finished.status}`);
    }

    return {
      agentId,
      runId: finished.id,
      status: finished.status,
      text: finished.result?.trim() || "(Opus 5 未返回文本结果)",
      agentUrl: agent.url,
      createdAgent,
    };
  }
}

function parseModelParams(raw?: string): Array<{ id: string; value: string }> {
  if (!raw?.trim()) {
    return [];
  }
  return JSON.parse(raw) as Array<{ id: string; value: string }>;
}

function isTerminal(status: RunStatus): boolean {
  return (
    status === "FINISHED" ||
    status === "ERROR" ||
    status === "CANCELLED" ||
    status === "EXPIRED"
  );
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
