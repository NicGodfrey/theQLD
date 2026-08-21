// Atelier scene elements — excalidraw-inspired (excalidraw is MIT; patterns
// re-implemented, no code copied). See ADAPTERS.md #3.
//
// Patterns implemented:
//   * flat element schema with version + versionNonce + isDeleted tombstones
//     -> last-writer-wins merge without a CRDT library
//   * fractional-index z-order: reordering touches ONE record
//   * scene file format: flat, versioned, forward-readable

export function createElement(type, props = {}) {
  return {
    id: crypto.randomUUID(),
    typeName: "element",
    type, // "image" | "text" | "rect" | "ellipse" | "path" | ...
    x: 0,
    y: 0,
    width: 100,
    height: 100,
    angle: 0,
    opacity: 1,
    index: "a1", // fractional z-order key; see indexBetween()
    version: 1,
    versionNonce: randNonce(),
    isDeleted: false,
    fileId: null, // content-addressed blob reference for image elements
    props: {}, // type-specific payload
    ...props,
  };
}

/** Every mutation goes through this so version/versionNonce stay honest. */
export function mutateElement(el, patch) {
  return {
    ...el,
    ...patch,
    version: el.version + 1,
    versionNonce: randNonce(),
  };
}

/** Tombstone, never hard-delete — keeps concurrent merges convergent. */
export function deleteElement(el) {
  return mutateElement(el, { isDeleted: true });
}

/**
 * Last-writer-wins reconciliation (excalidraw's sync core):
 * higher version wins; equal versions tie-break on versionNonce.
 * Deterministic on both peers, no server arbitration required.
 */
export function mergeElement(local, remote) {
  if (!local) return remote;
  if (!remote) return local;
  if (remote.version > local.version) return remote;
  if (remote.version < local.version) return local;
  return remote.versionNonce < local.versionNonce ? remote : local;
}

export function mergeScenes(localEls, remoteEls) {
  const byId = new Map(localEls.map((el) => [el.id, el]));
  for (const remote of remoteEls) {
    byId.set(remote.id, mergeElement(byId.get(remote.id), remote));
  }
  return [...byId.values()];
}

// ---- fractional indexing ---------------------------------------------------
// Generates a string key strictly between two neighbors so z-reordering is a
// single-record update. Digits: base-36. Not the full jitter-hardened algorithm
// (see the "fractional-indexing" reference implementation) — enough for MVP.

const DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz";

export function indexBetween(a = null, b = null) {
  a = a ?? "";
  b = b ?? "";
  let prefix = "";
  for (let i = 0; ; i++) {
    const da = i < a.length ? DIGITS.indexOf(a[i]) : 0;
    const db = i < b.length ? DIGITS.indexOf(b[i]) : DIGITS.length;
    if (db - da > 1) return prefix + DIGITS[Math.floor((da + db) / 2)];
    prefix += DIGITS[da];
    if (i >= a.length && db - da === 1) return prefix + DIGITS[Math.floor(DIGITS.length / 2)];
  }
}

export function sortByIndex(elements) {
  return [...elements].sort((p, q) => (p.index < q.index ? -1 : p.index > q.index ? 1 : 0));
}

// ---- file format ------------------------------------------------------------

export function serializeScene(elements, appState = {}) {
  return JSON.stringify({
    type: "atelier",
    version: 1,
    source: "atelier-mvp",
    elements: elements.filter((el) => !el.isDeleted),
    appState, // camera, selection, background — never element data
  });
}

export function deserializeScene(json) {
  const data = JSON.parse(json);
  if (data.type !== "atelier") throw new Error("not an atelier scene file");
  return { elements: data.elements ?? [], appState: data.appState ?? {} };
}

function randNonce() {
  return crypto.getRandomValues(new Uint32Array(1))[0];
}
