import { createHash } from "node:crypto";
import type { Context } from "hono";
import { streamSSE } from "hono/streaming";
import { config } from "./config.js";
import { acquireSession, chat, SessionError } from "./sessionService.js";

type AnthropicContent =
  | string
  | Array<{ type?: string; text?: string; [k: string]: unknown }>;

type AnthropicMessage = {
  role?: string;
  content?: AnthropicContent;
};

function extractText(content: AnthropicContent | undefined): string {
  if (!content) return "";
  if (typeof content === "string") return content;
  return content
    .map((part) => {
      if (typeof part === "string") return part;
      if (part && typeof part.text === "string") return part.text;
      return "";
    })
    .filter(Boolean)
    .join("\n");
}

function latestUserText(messages: AnthropicMessage[]): string {
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i];
    if ((m.role || "").toLowerCase() === "user") {
      const text = extractText(m.content).trim();
      if (text) return text;
    }
  }
  return "";
}

function parsePreferredSlot(model: string | undefined, headerSlot: string | undefined): number | undefined {
  if (headerSlot) {
    const n = Number(headerSlot);
    if (Number.isInteger(n) && n >= 1 && n <= config.poolSize) return n;
  }
  if (!model) return undefined;
  const m = model.match(/(?:sol[-_]?|slot[-_]?)(\d{1,2})\b/i);
  if (!m) return undefined;
  const n = Number(m[1]);
  if (Number.isInteger(n) && n >= 1 && n <= config.poolSize) return n;
  return undefined;
}

function clientIdFromRequest(c: Context): string {
  const explicit =
    c.req.header("x-client-id") ||
    c.req.header("x-session-client") ||
    "";
  if (explicit.trim()) return `cc:${explicit.trim()}`;
  const auth =
    c.req.header("authorization") ||
    c.req.header("x-api-key") ||
    "anon";
  const ua = c.req.header("user-agent") || "claude-code";
  const digest = createHash("sha256")
    .update(`${auth}|${ua}`)
    .digest("hex")
    .slice(0, 16);
  return `cc:${digest}`;
}

function anthropicMessageResponse(params: {
  model: string;
  text: string;
  inputTokens?: number;
  outputTokens?: number;
}) {
  const id = `msg_${crypto.randomUUID().replace(/-/g, "")}`;
  return {
    id,
    type: "message",
    role: "assistant",
    model: params.model,
    content: [{ type: "text", text: params.text }],
    stop_reason: "end_turn",
    stop_sequence: null,
    usage: {
      input_tokens: params.inputTokens ?? 0,
      output_tokens: params.outputTokens ?? 0,
    },
  };
}

export async function handleAnthropicMessages(c: Context) {
  const body = await c.req.json().catch(() => ({}));
  const messages = Array.isArray(body.messages) ? body.messages : [];
  const model = String(body.model || config.workerModelId);
  const stream = Boolean(body.stream);
  const userText = latestUserText(messages);
  if (!userText) {
    return c.json(
      {
        type: "error",
        error: {
          type: "invalid_request_error",
          message: "messages must include a user text turn",
        },
      },
      400,
    );
  }

  const preferredSlot = parsePreferredSlot(
    model,
    c.req.header("x-worker-slot") || undefined,
  );
  const clientId = clientIdFromRequest(c);

  let sessionId = "";
  try {
    const leased = acquireSession(clientId, {
      preferredSlot,
      reuse: true,
    });
    sessionId = leased.sessionId;
    const result = await chat(sessionId, userText);
    const responseModel =
      preferredSlot != null
        ? `gpt-5.6-sol-${String(preferredSlot).padStart(2, "0")}`
        : "gpt-5.6-sol";
    const payload = anthropicMessageResponse({
      model: responseModel,
      text: result.assistantText || "",
      inputTokens: result.usage?.inputTokens,
      outputTokens: result.usage?.outputTokens,
    });

    if (!stream) return c.json(payload);

    return streamSSE(c, async (sse) => {
      const msgId = payload.id;
      await sse.writeSSE({
        event: "message_start",
        data: JSON.stringify({
          type: "message_start",
          message: {
            id: msgId,
            type: "message",
            role: "assistant",
            model: responseModel,
            content: [],
            stop_reason: null,
            stop_sequence: null,
            usage: { input_tokens: payload.usage.input_tokens, output_tokens: 0 },
          },
        }),
      });
      await sse.writeSSE({
        event: "content_block_start",
        data: JSON.stringify({
          type: "content_block_start",
          index: 0,
          content_block: { type: "text", text: "" },
        }),
      });
      await sse.writeSSE({
        event: "content_block_delta",
        data: JSON.stringify({
          type: "content_block_delta",
          index: 0,
          delta: { type: "text_delta", text: payload.content[0].text },
        }),
      });
      await sse.writeSSE({
        event: "content_block_stop",
        data: JSON.stringify({ type: "content_block_stop", index: 0 }),
      });
      await sse.writeSSE({
        event: "message_delta",
        data: JSON.stringify({
          type: "message_delta",
          delta: { stop_reason: "end_turn", stop_sequence: null },
          usage: { output_tokens: payload.usage.output_tokens },
        }),
      });
      await sse.writeSSE({
        event: "message_stop",
        data: JSON.stringify({ type: "message_stop" }),
      });
    });
  } catch (err) {
    if (err instanceof SessionError) {
      return c.json(
        {
          type: "error",
          error: { type: err.code, message: err.message },
        },
        err.status as 400 | 404 | 409 | 500 | 503,
      );
    }
    return c.json(
      {
        type: "error",
        error: {
          type: "api_error",
          message: err instanceof Error ? err.message : String(err),
          sessionId: sessionId || undefined,
        },
      },
      500,
    );
  }
}

export function handleAnthropicModels(c: Context) {
  const data = [
    {
      id: "gpt-5.6-sol",
      display_name: "GPT5.6 sol (auto slot)",
      type: "model",
      created_at: "2026-08-12T00:00:00Z",
    },
    ...Array.from({ length: config.poolSize }, (_, i) => {
      const slot = i + 1;
      const id = `gpt-5.6-sol-${String(slot).padStart(2, "0")}`;
      return {
        id,
        display_name: `GPT5.6 sol slot ${slot}`,
        type: "model",
        created_at: "2026-08-12T00:00:00Z",
      };
    }),
  ];
  return c.json({ data, has_more: false, first_id: data[0]?.id, last_id: data.at(-1)?.id });
}
