# Helix Memory — live vs. designed, and what must land before a non-dev trusts it

Opus#7 of 10 · 2026-08-21 · read-only pass over `/workspace`, all outputs under
`/tmp/atelier-opus/07-memory-gaps/`

**Compared**

| Side | Files |
| --- | --- |
| Live runtime | `atelier/helix/store.py` (305 lines), plus its callers `atelier/server.py`, `atelier/helix/conductor.py`, `atelier/helix/usage.py`, `atelier/helix/loom.py` |
| Designed | `atelier/research/fable5/04-helix-arch/{schema.sql, store.py, ARCHITECTURE.md}` (+ `openapi.yaml`, `test_store.py`) |

Everything below marked *(measured)* comes from four probe scripts run against
copies of the tree in `/tmp`, output in `evidence/probe-output.txt`, scripts in
`evidence/probe*.py`. No file under `/workspace` was written; probes ran with
`PYTHONDONTWRITEBYTECODE=1` against `tempfile` databases and, for the HTTP
tests, a server on an otherwise-unused port with `ATELIER_RUNTIME` pointed at
`/tmp`.

---

## 1. The verdict first

**Today the live studio is a good demo and an unsafe home for real work.** It is
honest about spend, it never blanks the board, and a single user clicking once
at a time gets clean results *(measured: 8 sequential demo turns → 8×HTTP 200,
16 messages, 8 board nodes; 12 concurrent board reads during a turn → 12×200)*.

Three findings are disqualifying on their own:

1. **Two writes at once corrupt the session.** The whole app shares one
   `sqlite3` connection with `check_same_thread=False` behind a
   `ThreadingHTTPServer`, with no lock and no explicit transactions. Double-click
   Run and *(measured)* **5 of 12 turns fail with HTTP 500** (`bad parameter or
   other API misuse`), **2 user messages are lost entirely**, and one probe run
   got a **404 "missing thread" for a thread that exists** — a read returning the
   wrong answer. Eight simultaneous turns produced 1 success, 6 500s, and
   7 of 16 expected messages.
2. **Nothing is protected and nothing is repairable.** `UPDATE`/`DELETE` on
   `messages` and on `usage_events` both succeed *(measured)*; declared foreign
   keys are not enforced (`PRAGMA foreign_keys=0`), so a message can be inserted
   against a thread that does not exist *(measured)*. At the same time there is
   **no delete path at all**: the string `DELETE` does not appear in the live
   `store.py` and `server.py` has no `do_DELETE` *(measured)*. So history can be
   silently rewritten by anything with the file, and the user cannot remove a bad
   generation or the orphan user-message a failed turn left behind.
3. **Any schema change bricks existing installs, and there is no backup.** The
   schema is `CREATE TABLE IF NOT EXISTS` with `PRAGMA user_version=0`; opening a
   database written by an older build silently keeps the stale shape and the
   first write dies with `OperationalError: table projects has no column named
   brand_kit` *(measured)*. There is no export, no `VACUUM INTO`, no snapshot
   endpoint, and the artifact bytes live in a gitignored `.runtime/` directory
   referenced by **absolute host paths** stored in the database *(measured:
   `path='/tmp/.../artifacts/cd42df…svg'`)*, so moving or copying the studio
   breaks every image.

The good news: the design that fixes almost all of this is already written **and
already passes its own tests** — `python3 test_store.py` in `04-helix-arch`
reports `ALL 10 TESTS PASSED` *(measured)*, and the same 5-thread × 100-append
load that loses rows on the live store gives **500/500 rows, 0 errors, gap-free
`seq`** on the research store *(measured)*. This is a porting-and-migration job,
not a research job. But porting is **not sufficient**: §5 lists five gaps the
research design also does not close.

---

## 2. Enforcement surface, side by side

*(measured — object counts from `sqlite_master` on a freshly created database of each)*

| | live | designed |
| --- | --- | --- |
| Tables | 6 (`projects`, `threads`, `messages`, `artifacts`, `nodes`, `usage_events`) | 15 (adds `rungs`, `boards`, `board_layers`, `board_nodes`, `brand_kits`, `brand_assets`, `provider_configs`, `loom_runs`, `loom_steps`, `loom_step_io`) |
| Indexes | **0** | 14 (incl. `ux_brand_kits_active` partial unique) |
| Triggers | **0** | 5 (append-only messages ×2, append-only usage ×2, frozen artifacts ×1) |
| Views | 0 | 2 (`v_board_scene`, `v_usage_daily`) |
| `PRAGMA journal_mode` | `delete` | `wal` |
| `PRAGMA foreign_keys` | `0` (FKs declared but dead) | `1` |
| `PRAGMA user_version` | `0` | `1` |
| `busy_timeout` | 5000 ms — inherited from `sqlite3.connect`'s default `timeout=5.0`, not set deliberately | 5000 ms, set explicitly |
| Transactions | implicit; `commit()` after every statement | `BEGIN IMMEDIATE` via a re-entrant `_txn()` under an `RLock` |
| Write concurrency | one shared connection, no lock | one shared connection, all writes serialized through the lock |
| Timestamps | `REAL` seconds | `INTEGER` ms |
| Money | `estimated_usd REAL` | `cost_micros INTEGER` |
| IDs | `uuid4().hex` (unordered) | prefixed ULIDs (`prj_01J…`, time-sortable) |

Column-level: `artifacts` is `(id, project_id, thread_id, kind, path, mime,
prompt, provider, model, created_at)` live versus `(…, storage, uri, sha256,
byte_size, width, height, duration_ms, title, meta_json, parent_id, …)`
designed. `messages` has no `seq`. `projects` has no `slug`, no `archived_at`,
no `updated_at`.

---

## 3. The ten named gaps

### 3.1 Append-only — **absent, and the ledger is defeatable**

*Designed:* messages and `usage_events` are ledgers, enforced by four triggers
that `RAISE(ABORT)` on any `UPDATE` or `DELETE`, so the guarantee survives raw
SQL (`I3`, `I8`). Messages carry a gap-free per-thread `seq` with `UNIQUE
(thread_id, seq)`.

*Live:* no triggers. *(measured)* `UPDATE messages SET content='rewritten
history'` succeeded; `DELETE FROM messages` succeeded; `UPDATE usage_events SET
estimated_usd=0` and `DELETE FROM usage_events` both succeeded. Ordering is by
`created_at REAL` (`ORDER BY created_at ASC`), a wall-clock float with no
tiebreak — no collisions appeared at this scale, but two messages written in the
same millisecond have undefined order and a clock adjustment reorders history.

*Why a non-dev cares:* the spend meter is the only thing standing between them
and a surprise provider bill, and the live budget guard reads that same table
(`usage.spent_since` sums `estimated_usd`). Anything that can delete rows —
including a future "clear history" feature written by a well-meaning
contributor — silently resets the budget guard to zero. And a chat log that can
be edited in place is not evidence of anything.

*Must land:* the four triggers plus `seq`, and `ORDER BY seq` in the read path.

### 3.2 Rungs / provenance — **absent**

*Designed:* a `rungs` table (`message_id`, `artifact_id`, `relation ∈
{prompted, produced, referenced, approved, rejected}`, unique per triple),
`artifacts.parent_id` for derivation (upscale-of, variation-of), and
`loom_step_io` recording what each pipeline step consumed and produced. The
promise in `ARCHITECTURE.md` §1 is "given any pixel on the canvas you can climb
the rungs back to the sentence that caused it".

*Live:* *(measured)* the only link is `artifacts.thread_id` — nullable, pointing
at a *thread*, not a message — plus whatever the conductor happened to stash in
`messages.plan_json`. No `rungs`, no `parent_id`, no `loom_runs`/`loom_steps`, no
`loom_step_io`. There are no variations or upscales in the live product yet, so
nothing needs `parent_id` today; the message link, though, is needed the moment a
thread has two turns.

*Why a non-dev cares:* six weeks into a project the board has forty images and
the only question that matters is "which brief produced this one, and what did I
say about it?" Today the answer is "some turn in this thread". This is also the
mechanism a "regenerate like this one" or "why does this look wrong" feature
would be built on.

*Must land:* `rungs` written by the conductor on every produced artifact (one
line at the existing `add_artifact` call site), and `parent_id` before the first
variation/upscale feature ships.

### 3.3 Content-addressed blobs — **absent, no integrity at all**

*Designed:* `_blob_write` hashes bytes, writes `<sha[:2]>/<sha>` once per digest
via temp-file + `os.replace`, and the row carries `sha256`, `byte_size`, and a
*relative* `uri`; `CHECK (storage <> 'blob' OR sha256 IS NOT NULL)` (`I10`).

*Live:* `loom.write_bytes` writes `<artifact_id><ext>` with a plain
`Path.write_bytes` — no hash, no temp-and-rename, no `fsync`. *(measured)*
identical bytes were stored twice under two names; the row holds an **absolute**
host path; overwriting the file on disk afterwards is undetectable because there
is no `sha256` or `byte_size` to compare. `server.py` then serves whatever that
absolute path points at.

*Why a non-dev cares:* three consequences, in order of how soon they bite.
(a) Copying the studio to a new laptop, or renaming the folder, breaks every
image on every board — the DB still points at the old absolute path. (b) A
half-written file from a crash or a full disk renders as a broken card forever.
(c) Regenerating the same prompt stores the same megabytes again.

*Must land:* `sha256` + `byte_size` + relative `uri` on the row, temp-write +
`fsync` + `os.replace`, and content addressing so the path is derivable from the
hash rather than stored.

### 3.4 Brand kit uniqueness — **absent; one unvalidated JSON blob**

*Designed:* a `brand_kits` table with `palette_json` / `typography_json` /
`voice_json`, `brand_assets` linking curated artifacts with roles
(`logo_primary`, `wordmark`, …), and `I6` — at most one active kit per project —
enforced by `CREATE UNIQUE INDEX ux_brand_kits_active ON brand_kits(project_id)
WHERE is_active = 1`, with activation as an atomic swap inside one transaction.
Brand assets cannot cross projects (`I7`).

*Live:* one `projects.brand_kit TEXT DEFAULT '{}'` column. No second kit, no
activation, no history, no asset references, and no validation. *(measured)*
`update_brand_kit("no-such-project", …)` returns `None` and raises nothing — a
silent no-op the UI reports as success. A non-JSON value in that column persists
happily and then makes `get_project()` raise `JSONDecodeError`, which in
`server.py` is an uncaught exception in `do_GET` — the project page becomes
unloadable, and the board, threads, and brand panel all go with it.

There is also a live shape bug at `server.py:194`: `update_brand_kit(parts[2],
body.get("brand_kit") or body)`. *(measured)* clearing the kit — posting
`{"brand_kit": {}}` — is falsy, so the fallback fires and the **envelope gets
stored as the kit**: `{"brand_kit": {}}`. The conductor then feeds that nested
shape to the model as "Brand kit JSON (must obey)".

*Why a non-dev cares:* the brand kit is the one artifact they will hand-curate,
and it is the thing every generation is conditioned on. It deserves versions
("go back to last month's palette"), an explicit active/inactive state, and
validation — not a free-text box that can be poisoned into a 500.

*Must land:* the `brand_kits`/`brand_assets` tables with the partial unique
index, palette/typography validation at the store boundary, and the `or body`
fallback deleted.

### 3.5 Delete and orphan artifacts — **no delete path anywhere; failures leave residue**

*Designed:* `I11` — projects, threads, messages, and usage events are never
hard-deleted (projects archive via `archived_at`); board nodes, layers, and brand
assets *are* deletable because they are projections and curation, not history.
`openapi.yaml` exposes exactly three deletes: `deleteNode`, `deleteLayer` ("the
artifact behind it is untouched"), and `deleteKey`.

*Live:* *(measured)* no `DELETE` statement in `store.py`, no `do_DELETE` in
`server.py`, no archive flag. A user cannot remove a node, an artifact, a thread,
or a project. `nodes.artifact_id` has no foreign key and `PRAGMA foreign_keys=0`
anyway, so a dangling reference is insertable *(measured: a node inserted with a
non-existent project and artifact was accepted)*.

*Live residue is already observable.* `conductor.run` performs **four separate
commits** per image — the artifact row, then the file, then `UPDATE artifacts SET
path`, then the node — with no transaction spanning them. *(measured)* a crash or
error between them leaves an artifact row with `path=''` and no board node:
unreachable, invisible, and unremovable. And in the double-click test, the 5
turns that 500ed still left their user messages behind *(measured: 10 user
messages vs. 7 assistant replies)* — the chat now shows five questions the studio
never answered, permanently.

*Why a non-dev cares:* "delete this ugly one" is table stakes, and a log full of
unanswered questions from failed clicks reads as a broken app. This gap is the
one most likely to be *misfixed*: the obvious implementation (`DELETE FROM
artifacts`) is exactly what `I4`/`I11` exist to prevent. Deleting a node must
leave the artifact; retiring an artifact should be a tombstone plus blob
reclamation, not a row deletion.

*Must land:* node/layer delete (projection only), project archive, one
transaction per conductor turn so a failure leaves nothing, and a documented
answer for "retire an artifact" that is not `DELETE`.

### 3.6 Migrations — **absent on both sides; the live one bricks on upgrade**

*Designed:* `PRAGMA user_version = 1` at the top of `schema.sql`, with a comment
that every statement is idempotent.

*Live:* `PRAGMA user_version` stays `0` and the schema is `CREATE TABLE IF NOT
EXISTS`, which is the dangerous half of a migration story: it makes a stale
database *look* fine. *(measured)* opening a database whose `projects` table
predates the `brand_kit` column left the stale columns in place — the `IF NOT
EXISTS` skipped the new shape — and the first write raised `OperationalError:
table projects has no column named brand_kit`. Through the HTTP surface that is a
500 on project creation with no explanation and no path forward.

Note the designed side sets `user_version` but *(measured)* never reads it — the
research `store.py` contains no migration runner either. Being on version 1 with
no upgrade path is only better than version 0 because the number is there to
compare against later.

*Why a non-dev cares:* they will update the app. The failure mode must be "your
library was upgraded" or, at worst, "this library is newer than this app,
please update" — never a 500 with a SQL error in it.

*Must land:* read `user_version` on open; refuse to run against a newer version;
run ordered migration steps inside one transaction for older ones; snapshot the
file before migrating (see §3.7). This is the one item where the research design
gives no head start.

### 3.7 Backup — **absent on both sides**

*Designed:* `project_snapshot()` produces a `helix-snapshot/1` JSON covering
project, threads with messages, artifacts, boards with layers and nodes, brand
kits, runs, and a usage summary — exposed as `GET
/projects/{id}/snapshot`. `ARCHITECTURE.md` §8 says deleting the database file
and blob root "*is* total erasure", which is also the whole disaster-recovery
plan.

*Live:* nothing — no export, no snapshot, no `.backup()`, no `VACUUM INTO`
*(measured)*. The database is `.runtime/helix.sqlite` and the artifacts are
`.runtime/artifacts/`, both inside a `.gitignore`d directory, referenced by
absolute path.

*Gap on the designed side too:* the snapshot is **export-only and metadata-only**
— `openapi.yaml` has no import, restore, or checkpoint operation *(measured: no
`import`/`restore`/`backup` string in the file)*, and the JSON carries artifact
*rows*, not bytes. Round-tripping a project onto a new machine is not possible
from any documented surface.

*(measured)* `VACUUM INTO` on the research store produced a 335 KB consistent
snapshot in under 10 ms, so the cheap version of this is genuinely cheap.

*Why a non-dev cares:* this is the single scariest gap for someone doing paid
client work in a local-first app. There is no cloud copy by design, so if the
file is the only copy, the file is the whole risk.

*Must land:* a one-click "Back up this studio" that writes `VACUUM INTO` plus a
blob-root copy (trivial and safe once blobs are content-addressed) into a
user-chosen folder; an automatic pre-migration snapshot; a restore path that is
tested, not implied.

### 3.8 WAL — **absent live; a reader can lock out the writer for 5 s and then fail**

*Designed:* `PRAGMA journal_mode = WAL` + `synchronous = NORMAL` + explicit
`busy_timeout = 5000`, with `IMMEDIATE` transactions (`ARCHITECTURE.md` §8).

*Live:* `journal_mode=delete`, `synchronous=FULL` (SQLite default), timeout only
by accident of `sqlite3.connect`'s default *(measured)*. Under a rollback journal
a reader takes a SHARED lock that blocks the writer entirely: *(measured)* a
write attempted while one read cursor was open failed with `database is locked`
after **5.01 s**. The identical test with `journal_mode=WAL` succeeded in
**0.000 s**.

*Why a non-dev cares:* this is the mechanism behind a class of bugs that look
like flakiness — a turn that hangs for five seconds and then errors because a
second browser tab, an export, or a backup script was reading. `synchronous=FULL`
also makes the current commit-per-statement pattern slower than it needs to be,
which matters because a turn does a dozen of them.

*Must land:* WAL + `NORMAL` + explicit busy timeout, set at connection open,
before anyone runs two tabs.

### 3.9 Concurrent writes — **the most acute defect; data is being lost today**

*Designed:* "Thread-safe for use from one process: all writes are serialized
through an `RLock` and run in `IMMEDIATE` transactions." One re-entrant `_txn()`
wraps each logical operation, so a turn is atomic.

*Live:* one connection, `check_same_thread=False`, no lock, `isolation_level`
default, `commit()` sprinkled through every method — behind a
`ThreadingHTTPServer` that gives every request its own thread.

*(measured, live store, direct)* 5 threads × 100 `add_message` on the shared
connection: **427 of 500 rows written, 175 errors**, all
`InterfaceError: bad parameter or other API misuse`. Errors both accompanied
successful inserts and hid lost ones.

*(measured, live server over HTTP)*

| scenario | result |
| --- | --- |
| 8 sequential demo turns | 8×200; 16 messages, 8 nodes — correct |
| 12 concurrent board reads during one turn | 12×200 — fine |
| 8 simultaneous turns on one thread | 1×200, **6×500**, 1×404 `missing thread` *(for a thread that exists)*; **7 of 16** messages persisted, 1 of 8 artifacts |
| 6 trials of 2 simultaneous turns (the double-click) | **5 of 12 turns 500**; **2 user messages lost outright**; failed turns left their user message with no reply |

*(measured, research store, same load)* 5 threads × 100 `append_message`:
**500/500 rows, 0 errors, 500 distinct gap-free `seq` values, 0.06 s**.

*Why a non-dev cares:* they cannot know that clicking Run twice is unsafe, and
the live UI does nothing to stop them — `app.js` neither disables the Run button
during a turn nor serializes requests. A real provider turn takes ten seconds;
the double-click is not an edge case, it is the default behaviour of an impatient
human. The observable symptom is an error toast plus a chat log missing the
message they just typed.

*Must land:* the lock + `_txn()` pattern (a direct lift), one transaction per
turn, and — independently, because the client should not rely on the server being
correct — a disabled Run button while a turn is in flight.

### 3.10 Secret scanner — **absent live; partial in the design**

*Designed:* `I1`/`I2` — `_assert_no_secrets()` refuses anything key-shaped with
`SecretLeakError`, checking eleven value patterns (OpenAI, Anthropic, AWS,
GitHub, Slack, Google, HuggingFace, Replicate, PEM, JWT, URL userinfo) and
seventeen suspicious field names, recursively through nested JSON; the database
stores only Keyring handles matching `^[a-z][a-z0-9_.:-]{2,63}$`, shape-checked
by a `CHECK` constraint. `08-security-quota/POLICY.md` adds a second layer:
`scrub_secrets()` replacing matches with `[REDACTED]` in logs and API bodies, a
canary-key CI grep, and a `redaction_backstop_hits` counter that is a release
blocker when nonzero.

*Live:* no scanning of any kind in `store.py`. *(measured)* an OpenAI-shaped key
pasted into a prompt landed in **3 row classes — `messages.content`,
`artifacts.prompt`, and `projects.brand_kit` — with no scan, no refusal, and no
redaction**, and it stays there forever because there is no delete path (§3.5).
Related: `keyring.json` is plaintext at mode 0600 (the design calls for the OS
keychain or an age/argon2 keyfile), and `Keyring.public_status()` returns
`secret[:3] + "…" + secret[-4:]` over HTTP, where `POLICY.md` §2 says "at most
the last 4 characters".

*Gap on the designed side too:* `_assert_no_secrets` is called from exactly two
places *(measured)* — `register_external_artifact` (the URI) and
`upsert_provider_config`. `append_message` payloads, artifact `meta_json`, and
brand-kit JSON are **not** scanned. The single most likely way a real key enters
the database is a user pasting it into chat to ask "is this key right?", and
neither implementation catches that.

*Why a non-dev cares:* a key in the message table is a key in every backup and
every exported snapshot, and it is exactly the person who does not know what
`sk-` means who will paste one into the chat box.

*Must land:* scan on the write path for messages, prompts, meta, and brand kits —
refusing with a message the user understands ("that looks like an API key; put it
in Settings instead") — plus scrubbing on the read/log path, plus the keyring
moved off plaintext.

---

## 4. Two live-code details that belong in the same fix

Not in the assigned list, but they are in the write path and they will bite the
same user.

* **`server.py:175` writes SQL from the conductor.** `conductor.py` reaches
  through the store — `self.memory.conn.execute("UPDATE artifacts SET path=?…")`
  and `UPDATE threads SET topic=?…` — so the module boundary that
  `ARCHITECTURE.md` relies on ("Memory is the only module that touches disk") is
  already broken. Every invariant added to the store can be bypassed by the
  module most likely to bypass it.
* **The transport has no auth and can be told to listen publicly.** `I12` calls
  for loopback-only plus a per-install bearer token. Live binds
  `os.environ.get("ATELIER_HOST", "127.0.0.1")` — a good default with an env var
  that removes it — and has no token, so on a shared network `ATELIER_HOST=0.0.0.0`
  hands anyone the studio, its BYOK spend, and the key hints from `/api/keys`.

---

## 5. Porting the research design is necessary but not sufficient

`04-helix-arch` closes §3.1–3.5, 3.8, 3.9 outright and half of 3.10. It leaves
five things open, and these are the ones nobody has designed yet:

1. **No migration runner.** `user_version` is set and never read (§3.6).
2. **No restore.** Snapshot is export-only and carries no bytes (§3.7).
3. **No blob garbage collection.** Nothing ever unlinks a blob *(measured: no
   `unlink`/`shutil` in the research store)*. `ARCHITECTURE.md` §8 accepts
   "a crash can strand an orphan blob"; over a year of generations that is the
   studio quietly eating the disk, with no `fsck` to find them.
4. **No `fsync` before `os.replace`, and no verify-on-read.** The rename is
   atomic; the *contents* are not guaranteed durable without an `fsync` of the
   file and its directory, and `open_artifact` reads bytes without ever checking
   them against the `sha256` it has sitting in the row.
5. **Secret scanning misses chat** (§3.10).

---

## 6. What must land before a non-dev user trusts the studio with real work

Ordered by "what breaks first for a real user", with the acceptance test each
one needs. P0 items are pre-condition for a *first* real project; P1 for keeping
one for a month; P2 before recommending it to someone else.

**P0 — correctness under a human's hands**

| # | Item | Acceptance test |
| --- | --- | --- |
| 1 | Serialize writes: `RLock` + `BEGIN IMMEDIATE` `_txn()` (lift from research `store.py`), and one transaction per conductor turn | 5 threads × 100 appends → 500/500 rows, 0 errors; 6 trials of 2 simultaneous turns → 12×200 and 12 complete turns |
| 2 | WAL + `synchronous=NORMAL` + explicit `busy_timeout`, `foreign_keys=ON` | write during an open read cursor completes in < 100 ms; insert with a bogus `thread_id` is rejected |
| 3 | Disable Run while a turn is in flight (client-side, independent of #1) | double-click issues one request |
| 4 | Atomic artifact write: temp + `fsync` + `os.replace`, row after bytes, `sha256` + `byte_size` + relative `uri` | kill the process at each of the four former commit points → no artifact row without a readable file, no board node without an artifact |
| 5 | Secret scan on the write path for messages, prompts, meta, brand kits, with a plain-language refusal | pasting a canary key into a prompt is refused and appears in zero rows |
| 6 | Migration runner: read `user_version`, refuse newer, upgrade older in one transaction, snapshot first | a v0 database opens, migrates, and serves requests; a v99 database produces a clear message, not a 500 |
| 7 | Backup: `VACUUM INTO` + blob copy to a user-chosen folder, plus automatic pre-migration snapshot | restore into an empty directory reproduces every board, thread, and image |

**P1 — the guarantees the product's own story rests on**

| # | Item | Acceptance test |
| --- | --- | --- |
| 8 | Append-only triggers on `messages` and `usage_events`; `seq` per thread; read path ordered by `seq` | raw `UPDATE`/`DELETE` on either table aborts; the research suite's `I3`/`I8` tests pass against the live schema |
| 9 | `rungs` written on every produced artifact | for any artifact, "which message produced this" returns exactly one row |
| 10 | Delete that respects the model: node/layer delete, project archive, artifact retire-as-tombstone; no `DELETE FROM artifacts` | deleting a node leaves the artifact and its rungs intact; a retired artifact disappears from the board and its blob is reclaimable |
| 11 | `brand_kits` + `brand_assets` with the partial unique index; validation; kill the `or body` fallback | two kits, one active; saving an empty kit stores `{}`, not `{"brand_kit":{}}`; a malformed kit is refused at write, never at read |
| 12 | Move `conductor.py`'s raw SQL behind store methods | no `memory.conn.execute` outside `store.py` |

**P2 — durability and hygiene at rest**

| # | Item | Acceptance test |
| --- | --- | --- |
| 13 | Content addressing + blob GC + `fsck` (`sha256` verify on read or on demand) | regenerating identical bytes adds no file; a tampered blob is reported, not served |
| 14 | Keyring off plaintext (OS keychain or encrypted keyfile); redaction on responses and logs; hint ≤ last 4 chars | canary key absent from every log line and API body |
| 15 | Loopback + per-install bearer token; `ATELIER_HOST` override requires an explicit opt-in flag | unauthenticated request to any `/api/*` is refused |
| 16 | `artifacts.parent_id` before the first variation/upscale feature | lineage query returns the derivation chain |

**The one-sentence gate.** A non-dev can be handed this studio when: clicking Run
twice cannot lose a message, the app can back itself up and restore from that
backup, an app update cannot brick an existing library, and a pasted API key is
refused rather than filed forever in a chat log that has no delete button.

---

## Appendix — evidence

* `evidence/probe.py` — pragmas, FK enforcement, mutable history, provenance
  columns, blob duplication and tamper, brand-kit no-op and poisoning, secret
  persistence, delete-path absence, stale-schema upgrade
* `evidence/probe2.py` — rollback-journal vs. WAL reader/writer lockout,
  research-store concurrency and `VACUUM INTO`, mid-turn crash residue,
  8 simultaneous turns over HTTP
* `evidence/probe3.py` — sequential baseline and read-during-write baseline
* `evidence/probe4.py` — the double-click case and the residue it leaves
* `evidence/probe-output.txt` — concatenated output of all four

One caution about the numbers: this VM was running several sibling agents'
Atelier servers on nearby ports. An early `probe2` run reached another agent's
server on 8791; every HTTP figure quoted above comes from re-runs on ports
8846–8848 with `ATELIER_RUNTIME` under `/tmp`, verified against the runtime
database each probe created. `evidence/probe-output.txt` is from those runs.
