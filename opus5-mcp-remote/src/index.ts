import { readFile, writeFile, mkdir } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

const RELAY_URL = process.env.OPUS5_RELAY_URL?.replace(/\/$/, "");
const RELAY_TOKEN = process.env.OPUS5_RELAY_TOKEN?.trim();
const STATE_FILE =
  process.env.OPUS5_REMOTE_STATE_FILE ??
  join(homedir(), ".config", "opus5-mcp-remote", "session.json");

interface LocalState {
  session_id?: string;
}

async function loadState(): Promise<LocalState> {
  try {
    return JSON.parse(await readFile(STATE_FILE, "utf8")) as LocalState;
  } catch {
    return {};
  }
}

async function saveState(state: LocalState): Promise<void> {
  await mkdir(dirname(STATE_FILE), { recursive: true });
  await writeFile(STATE_FILE, JSON.stringify(state, null, 2), "utf8");
}

function requireConfig(): { relayUrl: string; token: string } {
  if (!RELAY_URL) {
    throw new Error("缺少 OPUS5_RELAY_URL，例如 https://your-relay.com");
  }
  if (!RELAY_TOKEN) {
    throw new Error("缺少 OPUS5_RELAY_TOKEN（中转站访问令牌）");
  }
  return { relayUrl: RELAY_URL, token: RELAY_TOKEN };
}

async function relayAsk(body: Record<string, unknown>): Promise<{
  session_id: string;
  reply: string;
  agent_url?: string;
}> {
  const { relayUrl, token } = requireConfig();
  const response = await fetch(`${relayUrl}/api/v1/ask`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = (await response.json()) as { error?: string; session_id?: string; reply?: string; agent_url?: string };
  if (!response.ok) {
    throw new Error(data.error ?? response.statusText);
  }

  return {
    session_id: data.session_id ?? "",
    reply: data.reply ?? "",
    agent_url: data.agent_url,
  };
}

const askSchema = z.object({
  message: z.string().min(1),
  reset: z.boolean().optional(),
});

const server = new Server(
  { name: "opus5-mcp-remote", version: "1.0.0" },
  { capabilities: { tools: {} } },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "ask_opus5",
      description:
        "通过远程中转站调用 Claude Opus 5。Cursor API Key 在中转服务器，本机只需 RELAY 令牌。",
      inputSchema: {
        type: "object",
        properties: {
          message: { type: "string", description: "发送给 Opus 5 的消息" },
          reset: { type: "boolean", description: "是否重置会话" },
        },
        required: ["message"],
      },
    },
    {
      name: "opus5_reset",
      description: "清除本地与中转会话绑定",
      inputSchema: { type: "object", properties: {} },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    if (request.params.name === "ask_opus5") {
      const input = askSchema.parse(request.params.arguments ?? {});
      const state = await loadState();
      const result = await relayAsk({
        message: input.message,
        reset: input.reset,
        session_id: input.reset ? undefined : state.session_id,
      });
      await saveState({ session_id: result.session_id });
      return { content: [{ type: "text", text: result.reply }] };
    }

    if (request.params.name === "opus5_reset") {
      await saveState({});
      return { content: [{ type: "text", text: "已清除远程会话绑定" }] };
    }

    throw new Error(`Unknown tool: ${request.params.name}`);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { isError: true, content: [{ type: "text", text: message }] };
  }
});

async function main(): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
