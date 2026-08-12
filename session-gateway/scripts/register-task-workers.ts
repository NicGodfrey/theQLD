/**
 * Register workers that were hot-started via Cursor Task(cloud) into the local pool registry.
 * Usage:
 *   npx tsx scripts/register-task-workers.ts <<'JSON'
 *   [{"slot":1,"bcId":"bc-...","url":"https://cursor.com/agents/bc-..."}]
 *   JSON
 */
import { readFileSync } from "node:fs";
import { registerExternalWorker } from "../src/pool.js";

type Item = { slot: number; bcId: string; url: string; name?: string };

async function main() {
  const raw = process.argv[2]
    ? readFileSync(process.argv[2], "utf8")
    : readFileSync(0, "utf8");
  const items = JSON.parse(raw) as Item[];
  const out = [];
  for (const item of items) {
    out.push(
      registerExternalWorker({
        slot: item.slot,
        bcId: item.bcId,
        url: item.url,
        name: item.name,
        source: "task",
      }),
    );
  }
  console.log(JSON.stringify({ workers: out }, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
