export type WorkerStatus = "FREE" | "BOUND" | "BUSY" | "RESETTING" | "ERROR";

export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  cacheWriteTokens: number;
  cacheReadTokens: number;
  totalTokens: number;
}

export interface WorkerSlot {
  slot: number;
  name: string;
  bcId: string | null;
  url: string | null;
  modelId: string;
  status: WorkerStatus;
  sessionId: string | null;
  generation: number;
  lastError: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface SessionRecord {
  sessionId: string;
  clientId: string;
  workerSlot: number;
  workerBcId: string;
  status: "ACTIVE" | "RELEASED" | "TIMED_OUT" | "RESET";
  acquiredAt: string;
  lastHeartbeatAt: string;
  releasedAt: string | null;
  releaseReason: string | null;
}

export interface TurnRecord {
  turnId: string;
  sessionId: string;
  workerSlot: number;
  workerBcId: string;
  runId: string | null;
  modelId: string;
  status: "RUNNING" | "FINISHED" | "ERROR" | "CANCELLED";
  startedAt: string;
  endedAt: string | null;
  usage: TokenUsage;
  estimatedUsdCents: number;
  settled: boolean;
  error: string | null;
}

export type ArtifactKind =
  | "user"
  | "assistant"
  | "thinking"
  | "tool_call"
  | "tool_result"
  | "system"
  | "status";

export interface ArtifactMeta {
  artifactId: string;
  turnId: string;
  sessionId: string;
  kind: ArtifactKind;
  seq: number;
  sha256: string;
  path: string;
  createdAt: string;
}

export interface PoolRegistryFile {
  version: 1;
  orchestratorUrl: string;
  modelId: string;
  updatedAt: string;
  workers: Array<{
    slot: number;
    name: string;
    bcId: string;
    url: string;
    source: "api" | "task" | "manual";
    readyAt?: string;
  }>;
}

export interface DbState {
  workers: WorkerSlot[];
  sessions: SessionRecord[];
  turns: TurnRecord[];
  artifacts: ArtifactMeta[];
}
