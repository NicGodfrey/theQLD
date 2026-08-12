import { config } from "./config.js";
import { cursorClient } from "./cursorClient.js";
import { store } from "./store.js";
import type { TokenUsage } from "./types.js";

export const ZERO_USAGE: TokenUsage = {
  inputTokens: 0,
  outputTokens: 0,
  cacheWriteTokens: 0,
  cacheReadTokens: 0,
  totalTokens: 0,
};

export function estimateUsdCents(usage: TokenUsage): number {
  const input =
    (usage.inputTokens / 1_000_000) * config.usdPerMillionInput;
  const output =
    (usage.outputTokens / 1_000_000) * config.usdPerMillionOutput;
  return Math.round((input + output) * 100);
}

export async function settleTurnUsage(
  turnId: string,
  agentId: string,
  runId: string,
): Promise<TokenUsage> {
  const usageRes = await cursorClient.getUsage(agentId, runId);
  const usage = usageRes.runs[0]?.usage || usageRes.totalUsage || ZERO_USAGE;
  const estimatedUsdCents = estimateUsdCents(usage);

  store.update((db) => {
    const turn = db.turns.find((t) => t.turnId === turnId);
    if (!turn) return;
    turn.usage = usage;
    turn.estimatedUsdCents = estimatedUsdCents;
    turn.settled = true;
  });

  return usage;
}

export function sessionInvoice(sessionId: string) {
  const db = store.get();
  const session = db.sessions.find((s) => s.sessionId === sessionId);
  const turns = db.turns.filter((t) => t.sessionId === sessionId);
  const usage = turns.reduce<TokenUsage>(
    (acc, t) => ({
      inputTokens: acc.inputTokens + t.usage.inputTokens,
      outputTokens: acc.outputTokens + t.usage.outputTokens,
      cacheWriteTokens: acc.cacheWriteTokens + t.usage.cacheWriteTokens,
      cacheReadTokens: acc.cacheReadTokens + t.usage.cacheReadTokens,
      totalTokens: acc.totalTokens + t.usage.totalTokens,
    }),
    { ...ZERO_USAGE },
  );
  const estimatedUsdCents = turns.reduce(
    (sum, t) => sum + t.estimatedUsdCents,
    0,
  );
  return {
    session,
    turns,
    usage,
    estimatedUsdCents,
    settled: turns.length > 0 && turns.every((t) => t.settled),
    artifactCount: db.artifacts.filter((a) => a.sessionId === sessionId)
      .length,
  };
}
