import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";

export interface SessionRecord {
  sessionId: string;
  agentId?: string;
  agentUrl?: string;
  updatedAt: string;
}

export class SessionStore {
  constructor(private readonly filePath: string) {}

  private async readAll(): Promise<Record<string, SessionRecord>> {
    try {
      const raw = await readFile(this.filePath, "utf8");
      return JSON.parse(raw) as Record<string, SessionRecord>;
    } catch {
      return {};
    }
  }

  private async writeAll(data: Record<string, SessionRecord>): Promise<void> {
    await mkdir(dirname(this.filePath), { recursive: true });
    await writeFile(this.filePath, JSON.stringify(data, null, 2), "utf8");
  }

  async get(sessionId: string): Promise<SessionRecord | undefined> {
    const all = await this.readAll();
    return all[sessionId];
  }

  async save(record: SessionRecord): Promise<void> {
    const all = await this.readAll();
    all[record.sessionId] = record;
    await this.writeAll(all);
  }

  async delete(sessionId: string): Promise<void> {
    const all = await this.readAll();
    delete all[sessionId];
    await this.writeAll(all);
  }
}

export function defaultStorePath(dataDir: string): string {
  return join(dataDir, "sessions.json");
}
