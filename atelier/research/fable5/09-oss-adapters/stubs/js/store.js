// Atelier record store — tldraw-*inspired* architecture, zero code taken.
// (tldraw's SDK is under the non-OSI tldraw license; see ADAPTERS.md #2.)
//
// Patterns implemented:
//   * the whole document is a flat store of typed records keyed by id
//   * listeners receive {added, updated, removed} change sets, not "changed!"
//   * undo/redo via inverse patches, grouped by user-level "marks"
//
// Plain ES module. No dependencies, no build step.

export class Store {
  #records = new Map(); // id -> record (records are plain frozen-ish objects)
  #listeners = new Set();
  #undoStack = []; // array of "entries": [{id, before, after}, ...]
  #redoStack = [];
  #pending = null; // entries accumulated since the last mark

  get(id) {
    return this.#records.get(id);
  }

  ids() {
    return [...this.#records.keys()];
  }

  allOf(typeName) {
    return [...this.#records.values()].filter((r) => r.typeName === typeName);
  }

  /** Insert or update records. Each record must have `id` and `typeName`. */
  put(records) {
    const added = [], updated = [];
    for (const rec of records) {
      const before = this.#records.get(rec.id) ?? null;
      this.#records.set(rec.id, rec);
      this.#track(rec.id, before, rec);
      (before ? updated : added).push(rec);
    }
    this.#emit({ added, updated, removed: [] });
  }

  remove(ids) {
    const removed = [];
    for (const id of ids) {
      const before = this.#records.get(id);
      if (!before) continue;
      this.#records.delete(id);
      this.#track(id, before, null);
      removed.push(before);
    }
    this.#emit({ added: [], updated: [], removed });
  }

  listen(fn) {
    this.#listeners.add(fn);
    return () => this.#listeners.delete(fn);
  }

  // ---- history (inverse patches) ----------------------------------------

  /** Close the current undo group. Call once per user-level operation. */
  mark() {
    if (this.#pending?.length) {
      this.#undoStack.push(this.#pending);
      this.#redoStack.length = 0;
    }
    this.#pending = [];
  }

  undo() {
    this.mark();
    this.#applyHistory(this.#undoStack, this.#redoStack, "before");
  }

  redo() {
    this.#applyHistory(this.#redoStack, this.#undoStack, "after");
  }

  #applyHistory(from, to, key) {
    const entry = from.pop();
    if (!entry) return;
    const changes = { added: [], updated: [], removed: [] };
    for (const patch of [...entry].reverse()) {
      const value = patch[key];
      if (value === null) {
        const cur = this.#records.get(patch.id);
        this.#records.delete(patch.id);
        if (cur) changes.removed.push(cur);
      } else {
        const before = this.#records.get(patch.id) ?? null;
        this.#records.set(patch.id, value);
        (before ? changes.updated : changes.added).push(value);
      }
    }
    to.push(entry);
    this.#emit(changes);
  }

  #track(id, before, after) {
    if (this.#pending === null) this.#pending = [];
    this.#pending.push({ id, before, after });
  }

  #emit(changes) {
    if (!changes.added.length && !changes.updated.length && !changes.removed.length) return;
    for (const fn of this.#listeners) fn(changes);
  }

  // ---- persistence --------------------------------------------------------

  serialize() {
    return JSON.stringify({ schemaVersion: 1, records: [...this.#records.values()] });
  }

  static deserialize(json) {
    const store = new Store();
    const { records = [] } = JSON.parse(json);
    store.put(records);
    store.mark();
    return store;
  }
}
