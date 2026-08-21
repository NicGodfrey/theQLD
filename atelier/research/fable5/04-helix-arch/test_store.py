"""
test_store.py — invariant and behaviour tests for Memory (store.py).

Standard library only. Run: python3 test_store.py
Each test gets a fresh on-disk store in a temp dir (WAL, triggers, blobs all
exercised the same way a real install would).
"""

from __future__ import annotations

import os
import sqlite3
import tempfile
import traceback

from store import (
    InvalidTransition,
    MemoryStore,
    NotFound,
    SecretLeakError,
    ValidationError,
)

TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


def expect_raises(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    except Exception as e:  # noqa: BLE001
        raise AssertionError(
            f"expected {exc_type.__name__}, got {type(e).__name__}: {e}"
        ) from e
    raise AssertionError(f"expected {exc_type.__name__}, nothing raised")


# ---------------------------------------------------------------------------


@test
def projects_crud_and_slugs(mem: MemoryStore):
    a = mem.create_project("Nova Coffee rebrand")
    b = mem.create_project("Nova Coffee rebrand")  # same name -> new slug
    assert a["slug"] == "nova-coffee-rebrand"
    assert b["slug"] == "nova-coffee-rebrand-2"
    assert mem.get_project_by_slug(a["slug"])["id"] == a["id"]

    mem.update_project(a["id"], description="Identity refresh",
                       meta={"client": "Nova"})
    got = mem.get_project(a["id"])
    assert got["description"] == "Identity refresh"
    assert got["meta"] == {"client": "Nova"}

    mem.archive_project(b["id"])
    active = [p["id"] for p in mem.list_projects()]
    assert b["id"] not in active and a["id"] in active
    everything = [p["id"] for p in mem.list_projects(include_archived=True)]
    assert b["id"] in everything

    expect_raises(NotFound, mem.get_project, "prj_NOPE")


@test
def messages_are_ordered_and_append_only(mem: MemoryStore):
    prj = mem.create_project("P")
    thr = mem.create_thread(prj["id"], title="T")
    m0 = mem.append_message(thr["id"], "user", "hello")
    m1 = mem.append_message(thr["id"], "conductor", "hi", payload={"k": 1})
    assert (m0["seq"], m1["seq"]) == (0, 1)

    msgs = mem.list_messages(thr["id"])
    assert [m["seq"] for m in msgs] == [0, 1]
    assert msgs[1]["payload"] == {"k": 1}
    assert mem.list_messages(thr["id"], after_seq=0)[0]["id"] == m1["id"]

    # I3: triggers block any rewrite of history, even raw SQL.
    expect_raises(
        sqlite3.DatabaseError, mem._db.execute,
        "UPDATE messages SET content = 'rewritten' WHERE id = ?", (m0["id"],)
    )
    expect_raises(
        sqlite3.DatabaseError, mem._db.execute,
        "DELETE FROM messages WHERE id = ?", (m0["id"],)
    )


@test
def artifacts_content_addressed_and_frozen(mem: MemoryStore):
    prj = mem.create_project("P")
    data = b"identical bytes"
    a1 = mem.put_artifact(prj["id"], data, "image", "image/png", title="one")
    a2 = mem.put_artifact(prj["id"], data, "image", "image/png", title="two")

    # I10: identities differ, bytes stored once (same sha/uri).
    assert a1["id"] != a2["id"]
    assert a1["sha256"] == a2["sha256"] and a1["uri"] == a2["uri"]
    assert mem.open_artifact(a1["id"]) == data

    # Annotations are the only legal mutation (I4).
    mem.annotate_artifact(a1["id"], title="renamed", meta={"pick": True})
    assert mem.get_artifact(a1["id"])["title"] == "renamed"
    expect_raises(
        sqlite3.DatabaseError, mem._db.execute,
        "UPDATE artifacts SET uri = 'evil' WHERE id = ?", (a1["id"],)
    )

    # Lineage: child -> parent chains, both directions.
    child = mem.put_artifact(prj["id"], b"v2", "image", "image/png",
                             parent_id=a1["id"])
    grand = mem.put_artifact(prj["id"], b"v3", "image", "image/png",
                             parent_id=child["id"])
    lin = mem.artifact_lineage(grand["id"])
    assert [a["id"] for a in lin["ancestors"]] == [child["id"], a1["id"]]
    lin_top = mem.artifact_lineage(a1["id"])
    assert {a["id"] for a in lin_top["descendants"]} == {child["id"], grand["id"]}

    # Lineage cannot cross projects.
    other = mem.create_project("Q")
    expect_raises(ValidationError, mem.put_artifact, other["id"], b"x",
                  "image", "image/png", parent_id=a1["id"])

    # External artifacts: no secret-bearing URLs.
    ext = mem.register_external_artifact(
        prj["id"], "https://cdn.example.com/tex.png", "image", "image/png")
    assert ext["storage"] == "external"
    expect_raises(SecretLeakError, mem.register_external_artifact, prj["id"],
                  "https://user:hunter2@example.com/x.png", "image", "image/png")


@test
def rungs_bind_the_strands(mem: MemoryStore):
    prj = mem.create_project("P")
    thr = mem.create_thread(prj["id"])
    msg = mem.append_message(thr["id"], "conductor", "made a thing")
    art = mem.put_artifact(prj["id"], b"thing", "image", "image/png")

    r1 = mem.link_message_artifact(msg["id"], art["id"], "produced")
    r2 = mem.link_message_artifact(msg["id"], art["id"], "produced")  # idempotent
    assert r1["id"] == r2["id"]
    mem.link_message_artifact(msg["id"], art["id"], "approved")

    rungs = mem.artifact_rungs(art["id"])
    assert {r["relation"] for r in rungs} == {"produced", "approved"}
    assert all(r["thread_id"] == thr["id"] for r in rungs)


@test
def board_layers_nodes_and_scene(mem: MemoryStore):
    prj = mem.create_project("P")
    art = mem.put_artifact(prj["id"], b"img", "image", "image/png")
    brd = mem.create_board(prj["id"], "Moodboard")
    bg = mem.create_layer(brd["id"], "Background")
    fg = mem.create_layer(brd["id"], "Foreground")
    assert (bg["z_index"], fg["z_index"]) == (0, 1)

    n1 = mem.add_node(brd["id"], bg["id"], "artifact", artifact_id=art["id"],
                      x=10, y=20, w=256, h=256)
    n2 = mem.add_node(brd["id"], fg["id"], "sticky",
                      props={"text": "pick this one"})
    assert n2["props"]["text"] == "pick this one"

    # I5: artifact nodes must carry an artifact (CHECK constraint).
    expect_raises(sqlite3.IntegrityError, mem._db.execute,
                  "INSERT INTO board_nodes (id, board_id, layer_id, kind, x, y,"
                  " w, h, created_at, updated_at)"
                  " VALUES ('nod_X', ?, ?, 'artifact', 0,0,1,1,0,0)",
                  (brd["id"], bg["id"]))

    # I7: no projecting artifacts from another project.
    other = mem.create_project("Q")
    foreign = mem.put_artifact(other["id"], b"other", "image", "image/png")
    expect_raises(ValidationError, mem.add_node, brd["id"], bg["id"],
                  "artifact", artifact_id=foreign["id"])

    # Move/resize, then paint order: layer z first, node z second.
    mem.update_node(n1["id"], x=500, y=600, w=128, h=128, opacity=0.5)
    scene = mem.board_scene(brd["id"])
    assert [s["node_id"] for s in scene] == [n1["id"], n2["id"]]
    assert scene[0]["x"] == 500 and scene[0]["opacity"] == 0.5

    expect_raises(ValidationError, mem.update_node, n1["id"], color="red")

    mem.set_viewport(brd["id"], {"x": -100, "y": 40, "zoom": 0.75})
    assert mem.get_board(brd["id"])["viewport"]["zoom"] == 0.75

    # Deleting the projection never touches the matter strand.
    mem.delete_node(n1["id"])
    mem.delete_layer(fg["id"])  # cascades n2
    assert mem.board_scene(brd["id"]) == []
    assert mem.get_artifact(art["id"])["id"] == art["id"]


@test
def one_active_brand_kit_per_project(mem: MemoryStore):
    prj = mem.create_project("P")
    k1 = mem.create_brand_kit(prj["id"], "Kit 1",
                              palette=[{"hex": "#112233"}], activate=True)
    k2 = mem.create_brand_kit(prj["id"], "Kit 2")
    assert mem.get_active_brand_kit(prj["id"])["id"] == k1["id"]

    mem.activate_brand_kit(k2["id"])  # atomically swaps the active kit
    assert mem.get_active_brand_kit(prj["id"])["id"] == k2["id"]
    assert mem.get_brand_kit(k1["id"])["is_active"] == 0

    # I6: even raw SQL cannot create two active kits (partial unique index).
    expect_raises(sqlite3.IntegrityError, mem._db.execute,
                  "UPDATE brand_kits SET is_active = 1 WHERE id = ?", (k1["id"],))

    art = mem.put_artifact(prj["id"], b"logo", "vector", "image/svg+xml")
    kit = mem.add_brand_asset(k2["id"], art["id"], "logo_primary")
    assert kit["assets"][0]["role"] == "logo_primary"

    other = mem.create_project("Q")
    foreign = mem.put_artifact(other["id"], b"x", "image", "image/png")
    expect_raises(ValidationError, mem.add_brand_asset, k2["id"], foreign["id"])


@test
def provider_configs_reject_raw_secrets(mem: MemoryStore):
    pc = mem.upsert_provider_config(
        "openai", "OpenAI (personal)", key_ref="openai.personal",
        base_url="https://api.openai.com/v1",
        capabilities=["text.generate", "image.generate"],
        defaults={"image_model": "gpt-image-1"},
    )
    assert pc["enabled"] == 1 and pc["key_ref"] == "openai.personal"

    # Upsert by label keeps the id.
    pc2 = mem.upsert_provider_config("openai", "OpenAI (personal)",
                                     key_ref="openai.personal", enabled=False)
    assert pc2["id"] == pc["id"] and pc2["enabled"] == 0

    # I1: raw secrets are refused in every position.
    expect_raises(SecretLeakError, mem.upsert_provider_config, "openai", "leaky1",
                  key_ref="openai.x",
                  defaults={"api_key": "sk-abcdefghijklmnop1234"})
    expect_raises(SecretLeakError, mem.upsert_provider_config, "openai", "leaky2",
                  key_ref="openai.x",
                  defaults={"note": "use sk-abcdefghijklmnopqrst please"})
    expect_raises(ValidationError, mem.upsert_provider_config, "openai", "leaky3",
                  key_ref="sk-abcdefghijklmnopqrst")
    expect_raises(SecretLeakError, mem.upsert_provider_config, "aws", "leaky4",
                  key_ref="aws.main", base_url="https://AKIAIOSFODNN7EXAMPLE@x.com")

    got = mem.list_provider_configs(spoke="openai")
    assert len(got) == 1


@test
def usage_ledger_is_append_only(mem: MemoryStore):
    prj = mem.create_project("P")
    mem.record_usage("openai", "image.generate", project_id=prj["id"],
                     model="gpt-image-1", unit_type="pixels",
                     output_units=1_048_576, cost_micros=40_000, latency_ms=9000)
    mem.record_usage("anthropic", "text.generate", project_id=prj["id"],
                     model="claude", unit_type="tokens", input_units=900,
                     output_units=400, cost_micros=1_200, latency_ms=1500)
    mem.record_usage("openai", "image.generate", project_id=prj["id"],
                     unit_type="pixels", output_units=262_144,
                     cost_micros=10_000, status="error", error="content policy")

    summary = {(s["spoke"], s["operation"]): s
               for s in mem.usage_summary(project_id=prj["id"])}
    assert summary[("openai", "image.generate")]["events"] == 2
    assert summary[("openai", "image.generate")]["cost_micros"] == 50_000
    assert summary[("anthropic", "text.generate")]["input_units"] == 900
    assert len(mem.usage_daily()) == 2  # two (spoke, operation) pairs today

    ev = mem.list_usage_events(project_id=prj["id"])[0]
    # I8: the meter never lies.
    expect_raises(sqlite3.DatabaseError, mem._db.execute,
                  "UPDATE usage_events SET cost_micros = 0 WHERE id = ?",
                  (ev["id"],))
    expect_raises(sqlite3.DatabaseError, mem._db.execute,
                  "DELETE FROM usage_events WHERE id = ?", (ev["id"],))


@test
def loom_runs_follow_the_status_graph(mem: MemoryStore):
    prj = mem.create_project("P")
    thr = mem.create_thread(prj["id"])
    src = mem.put_artifact(prj["id"], b"src", "image", "image/png")

    run = mem.create_run(
        prj["id"],
        [{"name": "gen", "spoke_op": "image.generate",
          "params": {"prompt": "poster"}},
         {"name": "upscale", "spoke_op": "image.upscale"}],
        thread_id=thr["id"], name="poster-v1",
        plan={"edges": [[0, 1]]},
    )
    assert [s["idx"] for s in run["steps"]] == [0, 1]

    # I9: no skipping ahead.
    expect_raises(InvalidTransition, mem.finish_run, run["id"], "succeeded")
    mem.start_run(run["id"])
    expect_raises(InvalidTransition, mem.start_run, run["id"])

    s0, s1 = run["steps"][0], run["steps"][1]
    mem.start_step(s0["id"])
    out = mem.put_artifact(prj["id"], b"gen-out", "image", "image/png")
    mem.finish_step(s0["id"], output_artifact_ids=[out["id"]])

    mem.start_step(s1["id"])
    mem.add_step_inputs(s1["id"], [out["id"], src["id"]])
    up = mem.put_artifact(prj["id"], b"upscaled", "image", "image/png",
                          parent_id=out["id"])
    mem.finish_step(s1["id"], output_artifact_ids=[up["id"]])
    done = mem.finish_run(run["id"])

    assert done["status"] == "succeeded"
    assert done["steps"][0]["outputs"] == [out["id"]]
    assert set(done["steps"][1]["inputs"]) == {out["id"], src["id"]}
    expect_raises(InvalidTransition, mem.finish_run, run["id"], "failed")

    expect_raises(ValidationError, mem.create_run, prj["id"], [])


@test
def snapshot_covers_every_aggregate(mem: MemoryStore):
    prj = mem.create_project("P")
    thr = mem.create_thread(prj["id"])
    msg = mem.append_message(thr["id"], "user", "go")
    art = mem.put_artifact(prj["id"], b"a", "image", "image/png")
    mem.link_message_artifact(msg["id"], art["id"], "prompted")
    brd = mem.create_board(prj["id"])
    lyr = mem.create_layer(brd["id"])
    mem.add_node(brd["id"], lyr["id"], "artifact", artifact_id=art["id"])
    mem.create_brand_kit(prj["id"], "K", activate=True)
    mem.create_run(prj["id"], [{"name": "s", "spoke_op": "image.generate"}])
    mem.record_usage("openai", "image.generate", project_id=prj["id"])

    snap = mem.project_snapshot(prj["id"])
    assert snap["format"] == "helix-snapshot/1"
    assert snap["project"]["id"] == prj["id"]
    assert len(snap["threads"]) == 1 and len(snap["threads"][0]["messages"]) == 1
    assert len(snap["artifacts"]) == 1
    assert len(snap["boards"]) == 1 and len(snap["boards"][0]["nodes"]) == 1
    assert len(snap["brand_kits"]) == 1
    assert len(snap["runs"]) == 1
    assert snap["usage_summary"][0]["events"] == 1


# ---------------------------------------------------------------------------


def main() -> int:
    failures = 0
    for fn in TESTS:
        with tempfile.TemporaryDirectory(prefix="helix-test-") as tmp:
            mem = MemoryStore(os.path.join(tmp, "test.db"))
            try:
                fn(mem)
                print(f"  ok    {fn.__name__}")
            except Exception:  # noqa: BLE001
                failures += 1
                print(f"  FAIL  {fn.__name__}")
                traceback.print_exc()
            finally:
                mem.close()
    print()
    if failures:
        print(f"{failures}/{len(TESTS)} tests FAILED")
        return 1
    print(f"ALL {len(TESTS)} TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
