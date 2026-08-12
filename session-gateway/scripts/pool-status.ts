import { listWorkers, loadRegistryIntoStore } from "../src/pool.js";
import { config } from "../src/config.js";

loadRegistryIntoStore();
console.log(
  JSON.stringify(
    {
      orchestratorUrl: config.orchestratorUrl,
      modelId: config.workerModelId,
      workers: listWorkers(),
    },
    null,
    2,
  ),
);
