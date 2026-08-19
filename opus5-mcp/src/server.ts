import { mkdir, readFile, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { CursorAgentsClient } from "./cursor-api.js";

const STATE_DIR =
  process.env.OPUS5_MCP_STATE_DIR ?? join(homedir(), ".config", "opus5-mcp");
const STATE_FILE = join(STATE_DIR, "state.json");

interface PersistedState {
  agentId?: string;
  agentUrl?: string;
  updatedAt?: string;
}

async function loadState(): Promise<PersistedState> {
  try {
    const raw = await readFile(STATE_FILE, "utf8");
    return JSON.parse(raw) as PersistedState;
  } catch {
    return {};
  }
}

async function saveState(state: PersistedState): Promise<void> {
  await mkdir(dirname(STATE_FILE), { recursive: true });
  await writeFile(
    STATE_FILE,
    JSON.stringify({ ...state, updatedAt: new Date().toISOString() }, null, 2),
    "utf8",
  );
}

function requireApiKey(): string {
  const apiKey = process.env.CURSOR_API_KEY?.trim();
  if (!apiKey) {
    throw new Error(
      "缺少 CURSOR_API_KEY。请在环境变量中设置 Cursor Dashboard → API Keys 创建的密钥。",
    );
  }
  return apiKey;
}

const askSchema = z.object({
  message: z.string().min(1).describe("要发送给 Opus 5 的消息"),
  reset: z
    .boolean()
    .optional()
    .describe("为 true 时创建新的 Opus 5 会话，忽略历史 agent"),
  repo_url: z
    .string()
    .url()
    .optional()
    .describe("可选 GitHub 仓库 URL；仅在 reset=true 或首次创建时生效"),
  starting_ref: z
    .string()
    .optional()
    .describe("可选分支或 commit，默认 main"),
});

export function createOpus5McpServer(): Server {
  const server = new Server(
    {
      name: "opus5-mcp",
      version: "1.0.0",
    },
    {
      capabilities: {
        tools: {},
      },
    },
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
      {
        name: "ask_opus5",
        description:
          "向 Claude Opus 5（Cursor Cloud Agent，主模型人设）发送消息并等待完整回复。适合复杂推理、架构分析、代码审查等任务。Claude Code 应先用本地工具收集上下文，再调用此工具。",
        inputSchema: {
          type: "object",
          properties: {
            message: {
              type: "string",
              description: "要发送给 Opus 5 的消息",
            },
            reset: {
              type: "boolean",
              description: "为 true 时创建新的 Opus 5 会话",
            },
            repo_url: {
              type: "string",
              description: "可选 GitHub 仓库 URL",
            },
            starting_ref: {
              type: "string",
              description: "可选分支或 commit，默认 main",
            },
          },
          required: ["message"],
        },
      },
      {
        name: "opus5_status",
        description: "查看当前持久化的 Opus 5 agent 会话信息",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "opus5_reset",
        description: "清除本地保存的 Opus 5 agent 会话 ID（不删除远端 agent）",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "opus5_list_models",
        description:
          "列出当前 Cursor API Key 可用的模型（用于排查 Opus 5 model id）",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
    ],
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const client = new CursorAgentsClient(requireApiKey());

    try {
      switch (request.params.name) {
        case "ask_opus5": {
          const input = askSchema.parse(request.params.arguments ?? {});
          const state = await loadState();
          const envAgentId = process.env.CURSOR_OPUS5_AGENT_ID?.trim();
          const agentId = input.reset ? undefined : envAgentId || state.agentId;

          const result = await client.askOpus5({
            message: input.message,
            reset: input.reset,
            agentId,
            repoUrl: input.repo_url ?? process.env.CURSOR_OPUS5_REPO_URL,
            startingRef:
              input.starting_ref ?? process.env.CURSOR_OPUS5_STARTING_REF,
          });

          await saveState({
            agentId: result.agentId,
            agentUrl: result.agentUrl,
          });

          return {
            content: [
              {
                type: "text",
                text: result.text,
              },
            ],
          };
        }

        case "opus5_status": {
          const state = await loadState();
          const envAgentId = process.env.CURSOR_OPUS5_AGENT_ID?.trim();
          const agentId = envAgentId || state.agentId;

          if (!agentId) {
            return {
              content: [
                {
                  type: "text",
                  text: "尚无 Opus 5 会话。先调用 ask_opus5。",
                },
              ],
            };
          }

          const agent = await client.getAgent(agentId);
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(
                  {
                    agentId,
                    agentUrl: agent.url ?? state.agentUrl,
                    status: agent.status,
                    latestRunId: agent.latestRunId,
                  },
                  null,
                  2,
                ),
              },
            ],
          };
        }

        case "opus5_reset": {
          await saveState({});
          return {
            content: [
              {
                type: "text",
                text: "已清除本地 Opus 5 会话 ID。下次 ask_opus5 会创建新 agent。",
              },
            ],
          };
        }

        case "opus5_list_models": {
          const models = await client.listModels();
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify({ models }, null, 2),
              },
            ],
          };
        }

        default:
          throw new Error(`Unknown tool: ${request.params.name}`);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        isError: true,
        content: [{ type: "text", text: message }],
      };
    }
  });

  return server;
}
