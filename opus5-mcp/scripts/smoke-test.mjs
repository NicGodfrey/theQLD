#!/usr/bin/env node
import { spawn } from "node:child_process";
import { createInterface } from "node:readline";

if (!process.env.CURSOR_API_KEY?.trim()) {
  console.error("请先设置 CURSOR_API_KEY");
  process.exit(1);
}

const server = spawn("node", ["dist/index.js"], {
  cwd: new URL("..", import.meta.url).pathname,
  env: process.env,
  stdio: ["pipe", "pipe", "inherit"],
});

const request = {
  jsonrpc: "2.0",
  id: 1,
  method: "tools/call",
  params: {
    name: "opus5_list_models",
    arguments: {},
  },
};

const init = {
  jsonrpc: "2.0",
  method: "initialize",
  params: {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "smoke-test", version: "1.0.0" },
  },
  id: 0,
};

server.stdin.write(`${JSON.stringify(init)}\n`);
server.stdin.write(`${JSON.stringify(request)}\n`);

const rl = createInterface({ input: server.stdout });
let sawModels = false;

rl.on("line", (line) => {
  try {
    const payload = JSON.parse(line);
    if (payload.id === 1 && payload.result?.content?.[0]?.text) {
      sawModels = true;
      console.log("MCP smoke test OK");
      console.log(payload.result.content[0].text.slice(0, 500));
      server.kill();
      process.exit(0);
    }
  } catch {
    // ignore non-json lines
  }
});

setTimeout(() => {
  if (!sawModels) {
    console.error("MCP smoke test timed out");
    server.kill();
    process.exit(1);
  }
}, 30000);
