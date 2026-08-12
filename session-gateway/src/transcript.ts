import { createHash } from "node:crypto";
import { appendFileSync, mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { v4 as uuidv4 } from "uuid";
import { config } from "./config.js";
import { store } from "./store.js";
import type { ArtifactKind } from "./types.js";

function ensureDir(dir: string): void {
  mkdirSync(dir, { recursive: true });
}

export function appendArtifact(params: {
  turnId: string;
  sessionId: string;
  kind: ArtifactKind;
  content: string | object;
}): { artifactId: string; sha256: string; path: string; seq: number } {
  const body =
    typeof params.content === "string"
      ? params.content
      : JSON.stringify(params.content, null, 2);
  const sha256 = createHash("sha256").update(body).digest("hex");
  const artifactId = uuidv4();
  const createdAt = new Date().toISOString();

  let seq = 0;
  store.update((db) => {
    seq =
      db.artifacts.filter((a) => a.turnId === params.turnId).length + 1;
    const relDir = path.join("transcripts", params.sessionId, params.turnId);
    ensureDir(path.join(config.dataDir, relDir));
    const fileName = `${String(seq).padStart(4, "0")}-${params.kind}-${artifactId}.json`;
    const relPath = path.join(relDir, fileName);
    const absPath = path.join(config.dataDir, relPath);
    writeFileSync(
      absPath,
      JSON.stringify(
        {
          artifactId,
          turnId: params.turnId,
          sessionId: params.sessionId,
          kind: params.kind,
          seq,
          sha256,
          createdAt,
          content: params.content,
        },
        null,
        2,
      ),
    );

    // Append-only thinking stream for fast replay
    if (params.kind === "thinking" && typeof params.content === "string") {
      const thinkPath = path.join(
        config.dataDir,
        "thinking",
        `${params.sessionId}.ndjson`,
      );
      ensureDir(path.dirname(thinkPath));
      appendFileSync(
        thinkPath,
        `${JSON.stringify({ turnId: params.turnId, seq, sha256, createdAt, text: params.content })}\n`,
      );
    }

    db.artifacts.push({
      artifactId,
      turnId: params.turnId,
      sessionId: params.sessionId,
      kind: params.kind,
      seq,
      sha256,
      path: relPath,
      createdAt,
    });
  });

  return {
    artifactId,
    sha256,
    path: path.join("transcripts", params.sessionId, params.turnId),
    seq,
  };
}
