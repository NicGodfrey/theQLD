#!/usr/bin/env node
/**
 * Direct Cursor API smoke test (no MCP stdio).
 * Usage: CURSOR_API_KEY=crsr_xxx node opus5-mcp/scripts/test-api.mjs
 */
import { CursorAgentsClient } from "../dist/cursor-api.js";

const apiKey = process.env.CURSOR_API_KEY?.trim();
if (!apiKey) {
  console.error("请设置 CURSOR_API_KEY");
  process.exit(1);
}

const client = new CursorAgentsClient(apiKey);
const models = await client.listModels();
const opus = models.filter((m) =>
  [m.id, m.displayName ?? "", ...(m.aliases ?? [])]
    .join(" ")
    .toLowerCase()
    .includes("opus"),
);

console.log(
  JSON.stringify(
    {
      ok: true,
      modelCount: models.length,
      opusCandidates: opus.map((m) => ({
        id: m.id,
        displayName: m.displayName,
        variants: m.variants,
      })),
      resolved: await client.resolveOpus5Model(),
    },
    null,
    2,
  ),
);
