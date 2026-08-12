import { serve } from "@hono/node-server";
import { config } from "./config.js";
import { loadRegistryIntoStore } from "./pool.js";
import { buildApp } from "./routes.js";
import { sweepExpiredSessions } from "./sessionService.js";

loadRegistryIntoStore();
const app = buildApp();

serve({ fetch: app.fetch, port: config.port }, (info) => {
  console.log(
    JSON.stringify({
      event: "gateway_listen",
      port: info.port,
      orchestratorUrl: config.orchestratorUrl,
      poolSize: config.poolSize,
      modelId: config.workerModelId,
      cursorApiConfigured: Boolean(config.cursorApiKey),
    }),
  );
});

setInterval(() => {
  sweepExpiredSessions().catch((err) => {
    console.error("heartbeat sweep failed", err);
  });
}, config.heartbeatSweepMs);
