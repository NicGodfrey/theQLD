import { config } from "../src/config.js";
import { hotStartMissingSlots, listWorkers, loadRegistryIntoStore } from "../src/pool.js";

async function main() {
  loadRegistryIntoStore();
  if (!config.cursorApiKey) {
    console.error(
      "CURSOR_API_KEY missing. For Task-bootstrapped workers use POST /v1/pool/register instead.",
    );
    process.exit(1);
  }
  console.log(
    `Hot-starting up to ${config.poolSize} workers with model ${config.workerModelId}...`,
  );
  const workers = await hotStartMissingSlots();
  console.log(JSON.stringify({ workers: listWorkers() }, null, 2));
  const ready = workers.filter((w) => w.bcId && w.status !== "ERROR").length;
  const errors = workers.filter((w) => w.status === "ERROR");
  console.log(`Ready: ${ready}/${config.poolSize}`);
  if (errors.length) {
    console.error("Errors:", errors.map((e) => ({ slot: e.slot, lastError: e.lastError })));
    process.exit(2);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
