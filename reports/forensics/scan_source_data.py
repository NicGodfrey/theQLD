#!/usr/bin/env python3
"""High-signal statistical forensics on journal source-data spreadsheets.

Designed to catch templated numbers (HDAC6/LGR4 class):
  exact duplicate vectors, constant offsets, shared fractional parts,
  within-group cloned replicates, high-precision scalar reuse.

Skips bulk omics tables. Allegation generator, not a verdict.
"""
from __future__ import annotations

import hashlib
import json
import math
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

ROOT = Path("/tmp/forensics")
OUT = Path("/workspace/reports/forensics")
EPS = 1e-9


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def frac(x, nd=6):
    return round(abs(x) - math.floor(abs(x) + 1e-12), nd)


def load_grid(path, max_rows=400, max_cols=80):
    wb = openpyxl.load_workbook(path, data_only=True)
    sheets = []
    for name in wb.sheetnames:
        rows = []
        for i, row in enumerate(wb[name].iter_rows(values_only=True)):
            if i >= max_rows:
                break
            rows.append(list(row[:max_cols]))
        sheets.append((name, rows))
    wb.close()
    return sheets


def vertical_runs(rows, min_len=4, max_len=80):
    if not rows:
        return []
    ncols = max((len(r) for r in rows), default=0)
    out = []
    for c in range(ncols):
        buf, start = [], None
        for r, row in enumerate(rows):
            v = row[c] if c < len(row) else None
            if is_num(v):
                if start is None:
                    start = r
                buf.append(float(v))
            else:
                if min_len <= len(buf) <= max_len:
                    out.append({"kind": "col", "c": c, "r0": start, "r1": start + len(buf) - 1, "vals": buf})
                buf, start = [], None
        if min_len <= len(buf) <= max_len:
            out.append({"kind": "col", "c": c, "r0": start, "r1": start + len(buf) - 1, "vals": buf})
    return out


def horizontal_groups(rows, min_len=3, max_len=20):
    """Split a row into numeric groups separated by blanks (typical n=3–6 replicates)."""
    out = []
    for r, row in enumerate(rows):
        buf, start = [], None
        for c, v in enumerate(row):
            if is_num(v):
                if start is None:
                    start = c
                buf.append(float(v))
            else:
                if min_len <= len(buf) <= max_len:
                    out.append({"kind": "rowg", "r": r, "c0": start, "c1": start + len(buf) - 1, "vals": buf})
                buf, start = [], None
        if min_len <= len(buf) <= max_len:
            out.append({"kind": "rowg", "r": r, "c0": start, "c1": start + len(buf) - 1, "vals": buf})
    return out


def label_near(rows, r, c):
    bits = []
    for rr in range(max(0, r - 3), min(len(rows), r + 1)):
        row = rows[rr]
        for cc in range(max(0, c - 3), min(len(row), c + 4)):
            v = row[cc]
            if isinstance(v, str) and v.strip() and v.strip().lower() not in ("none",):
                bits.append(v.strip()[:70])
    seen, out = set(), []
    for b in bits:
        if b not in seen:
            seen.add(b)
            out.append(b)
    return " | ".join(out[:5])


def vec_key(vals, nd=8):
    return tuple(round(v, nd) for v in vals)


def looks_like_index(vals):
    if not vals:
        return True
    if all(abs(v - round(v)) < 1e-9 and 0 <= v <= 400 and abs(v) < 1e6 for v in vals):
        if vals == list(range(int(vals[0]), int(vals[0]) + len(vals))):
            return True
        diffs = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        if diffs and all(abs(d - diffs[0]) < 1e-9 for d in diffs) and diffs[0] in (1, 2, 5, 10, 15, 30, 60):
            return True
    return False


def constant_offset(a, b, tol=1e-8):
    if len(a) != len(b) or len(a) < 5:
        return None
    diffs = [y - x for x, y in zip(a, b)]
    span = max(diffs) - min(diffs)
    if span <= tol * max(1.0, max(abs(d) for d in diffs) or 1):
        d = sum(diffs) / len(diffs)
        if abs(d) > 1e-6:
            return d
    return None


def shared_frac_rate(a, b, nd=3):
    if len(a) != len(b) or len(a) < 5:
        return 0.0, 0
    hits = sum(1 for x, y in zip(a, b) if abs(frac(x, nd) - frac(y, nd)) < 10 ** (-nd))
    return hits / len(a), hits


def affine(a, b):
    n = len(a)
    if n < 6 or n != len(b):
        return None
    ma, mb = sum(a) / n, sum(b) / n
    var_a = sum((x - ma) ** 2 for x in a)
    if var_a < 1e-12:
        return None
    slope = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / var_a
    intercept = mb - slope * ma
    pred = [slope * x + intercept for x in a]
    ss_res = sum((y - p) ** 2 for y, p in zip(b, pred))
    ss_tot = sum((y - mb) ** 2 for y in b)
    r2 = 1 - ss_res / ss_tot if ss_tot > 1e-12 else 1
    return slope, intercept, r2


def within_group_clones(groups):
    hits = []
    for g in groups:
        vals = g["vals"]
        if looks_like_index(vals):
            continue
        # high-precision duplicates inside a small replicate group
        rnd = [round(v, 6) for v in vals]
        cnt = Counter(rnd)
        for val, n in cnt.items():
            if n >= 2 and abs(val) > 1e-6:
                # integer-ish 0/1/100 common; require some decimal uniqueness
                if abs(val - round(val)) < 1e-9 and abs(val) in (0, 1, 100, 1000):
                    continue
                hits.append((g, val, n))
    return hits


def loc(run):
    if run["kind"] == "col":
        return f"{run['sheet']} col{run['c']} r{run['r0']}-{run['r1']}"
    return f"{run['sheet']} r{run['r']} c{run['c0']}-{run['c1']}"


def scan_file(path, paper):
    findings = []
    sheets = load_grid(path)
    all_cols, all_groups = [], []
    precise_vals = defaultdict(list)  # value -> locations

    for sname, rows in sheets:
        # skip giant omics
        nrows = len(rows)
        ncols = max((len(r) for r in rows), default=0)
        omics = nrows > 250 and ncols > 20
        cols = vertical_runs(rows, min_len=5, max_len=60)
        groups = horizontal_groups(rows, min_len=3, max_len=12)
        for run in cols + groups:
            run["sheet"] = sname
            run["file"] = Path(path).name
            run["paper"] = paper
            rr = run.get("r0", run.get("r", 0))
            cc = run.get("c", run.get("c0", 0))
            run["label"] = label_near(rows, rr, cc)
        if not omics:
            all_cols.extend(cols)
            all_groups.extend(groups)

        for g in groups:
            for v in g["vals"]:
                if abs(v) > 1e-6 and abs(v - round(v, 2)) > 1e-9:  # >2 decimals
                    precise_vals[round(v, 8)].append((sname, g))

        for g, val, n in within_group_clones(groups):
            findings.append(
                {
                    "type": "within_group_duplicate",
                    "paper": paper,
                    "file": Path(path).name,
                    "sheet": sname,
                    "loc": loc(g),
                    "label": g["label"],
                    "value": val,
                    "times": n,
                    "group": g["vals"],
                    "n": len(g["vals"]),
                }
            )

    # pairwise columns of equal length
    seen = set()
    for i, a in enumerate(all_cols):
        if looks_like_index(a["vals"]):
            continue
        for b in all_cols[i + 1 :]:
            if len(a["vals"]) != len(b["vals"]):
                continue
            if a["sheet"] == b["sheet"] and a["c"] == b["c"]:
                continue
            if looks_like_index(b["vals"]):
                continue
            n = len(a["vals"])
            key = (id(a), id(b))
            if key in seen:
                continue
            seen.add(key)
            va, vb = a["vals"], b["vals"]
            rec = {
                "paper": paper,
                "file": Path(path).name,
                "loc_a": loc(a),
                "loc_b": loc(b),
                "label_a": a["label"],
                "label_b": b["label"],
                "n": n,
                "vals_a": [round(x, 6) for x in va[:12]],
                "vals_b": [round(x, 6) for x in vb[:12]],
            }
            if vec_key(va) == vec_key(vb):
                rec["type"] = "exact_duplicate_vector"
                findings.append(rec)
                continue
            if tuple(sorted(vec_key(va))) == tuple(sorted(vec_key(vb))) and len(set(vec_key(va))) >= 5:
                rec["type"] = "permutation_duplicate_vector"
                findings.append(rec)
                continue
            off = constant_offset(va, vb)
            if off is not None:
                rec["type"] = "constant_offset"
                rec["offset"] = round(off, 8)
                findings.append(rec)
                continue
            rate, hits = shared_frac_rate(va, vb, nd=3)
            if rate >= 0.75 and hits >= 6:
                rec["type"] = "shared_fractional_parts"
                rec["rate"] = round(rate, 3)
                rec["hits"] = hits
                findings.append(rec)
                continue
            fit = affine(va, vb)
            if fit and fit[2] >= 0.9995 and n >= 8:
                slope, intercept, r2 = fit
                if abs(slope - 1) < 0.001 and abs(intercept) < 1e-6:
                    continue
                # skip simple 2x / 0.5x without intercept (could be unit conversion)
                if abs(intercept) < 1e-4 and any(abs(slope - s) < 0.002 for s in (2, 0.5, 10, 0.1, 100, 0.01)):
                    continue
                rec["type"] = "affine_copy"
                rec["slope"] = round(slope, 6)
                rec["intercept"] = round(intercept, 6)
                rec["r2"] = round(r2, 8)
                findings.append(rec)

    # same-length row groups on nearby rows (qPCR / WB densitometry templates)
    by_sheet = defaultdict(list)
    for g in all_groups:
        by_sheet[g["sheet"]].append(g)
    for sheet, gs in by_sheet.items():
        for i, a in enumerate(gs):
            for b in gs[i + 1 :]:
                if len(a["vals"]) != len(b["vals"]) or len(a["vals"]) < 4:
                    continue
                if abs(a["r"] - b["r"]) > 12:
                    continue
                if a["c0"] == b["c0"] and a["r"] == b["r"]:
                    continue
                va, vb = a["vals"], b["vals"]
                if vec_key(va) == vec_key(vb) and not looks_like_index(va):
                    findings.append(
                        {
                            "type": "exact_duplicate_rowgroup",
                            "paper": paper,
                            "file": Path(path).name,
                            "loc_a": loc(a),
                            "loc_b": loc(b),
                            "label_a": a["label"],
                            "label_b": b["label"],
                            "n": len(va),
                            "vals_a": va,
                            "vals_b": vb,
                        }
                    )
                else:
                    rate, hits = shared_frac_rate(va, vb, nd=3)
                    if rate >= 0.8 and hits >= 4:
                        findings.append(
                            {
                                "type": "shared_fractional_parts_row",
                                "paper": paper,
                                "file": Path(path).name,
                                "loc_a": loc(a),
                                "loc_b": loc(b),
                                "label_a": a["label"],
                                "label_b": b["label"],
                                "n": len(va),
                                "rate": round(rate, 3),
                                "vals_a": va,
                                "vals_b": vb,
                            }
                        )

    # high-precision scalar reused in distant groups
    for val, locs in precise_vals.items():
        if len(locs) < 2:
            continue
        # different rows
        rows_used = {(sheet, grp["r"], tuple(grp["vals"])) for sheet, grp in locs}
        if len(rows_used) >= 2 and abs(val) > 0.05:
            # only flag if 5+ decimals of uniqueness
            s = f"{val:.10f}".rstrip("0")
            if "." in s and len(s.split(".")[1]) >= 4:
                findings.append(
                    {
                        "type": "precise_scalar_reuse",
                        "paper": paper,
                        "file": Path(path).name,
                        "value": val,
                        "n_places": len(locs),
                        "examples": [
                            {"sheet": sheet, "row": grp["r"], "group": grp["vals"], "label": grp["label"]}
                            for sheet, grp in locs[:4]
                        ],
                    }
                )
    return findings


def scan_paper(paper, paths):
    findings = []
    for p in paths:
        try:
            findings.extend(scan_file(p, paper))
        except Exception as e:
            findings.append({"type": "read_error", "paper": paper, "file": str(p), "error": str(e)})
    return findings


def lei_fig1_vs_ed6():
    """Direct comparison of analogous quantification blocks."""
    fig1 = next(ROOT.joinpath("lei").rglob("Fig1.xlsx"))
    ed6 = next(ROOT.joinpath("lei").rglob("*Fig. 6 *.xlsx"))
    wb1 = openpyxl.load_workbook(fig1, data_only=True)
    wb6 = openpyxl.load_workbook(ed6, data_only=True)
    r1 = [list(r) for r in wb1.active.iter_rows(values_only=True)]
    r6 = [list(r) for r in wb6.active.iter_rows(values_only=True)]
    wb1.close()
    wb6.close()

    def nums_in(rows):
        out = []
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                if is_num(v) and abs(float(v)) > 1e-9:
                    out.append((r, c, float(v)))
        return out

    n1, n6 = nums_in(r1), nums_in(r6)
    set1 = {round(v, 6) for _, _, v in n1}
    set6 = {round(v, 6) for _, _, v in n6}
    shared = sorted(set1 & set6)
    # keep non-trivial
    shared = [v for v in shared if abs(v - round(v)) > 1e-6 or abs(v) not in (0, 1, 100)]
    return {
        "n_fig1": len(n1),
        "n_ed6": len(n6),
        "n_shared_rounded6": len(shared),
        "shared_sample": shared[:40],
    }


def image_hashes():
    """Byte-identical and aHash near-duplicates among Lei blot/jpg files."""
    from PIL import Image
    import io

    imgs = []
    lei = ROOT / "lei"
    for zpath in lei.glob("*.zip"):
        with zipfile.ZipFile(zpath) as z:
            for info in z.infolist():
                name = info.filename.lower()
                if not name.endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
                    continue
                data = z.read(info)
                md5 = hashlib.md5(data).hexdigest()
                imgs.append({"zip": zpath.name, "name": info.filename, "md5": md5, "n": len(data), "data": data})

    by_md5 = defaultdict(list)
    for im in imgs:
        by_md5[im["md5"]].append(im)
    identical = [v for v in by_md5.values() if len(v) > 1]

    def ahash(data, size=16):
        try:
            im = Image.open(io.BytesIO(data)).convert("L").resize((size, size))
        except Exception:
            return None
        pixels = list(im.getdata())
        avg = sum(pixels) / len(pixels)
        bits = "".join("1" if p >= avg else "0" for p in pixels)
        return bits

    hashes = []
    for im in imgs:
        h = ahash(im["data"])
        if h:
            hashes.append((h, im))

    near = []
    # only compare across different zip/folders, sample if huge
    # 16*16=256 bits; hamming <= 8 is very similar
    from itertools import combinations

    # group by zip to avoid comparing same gel crops too aggressively? still useful
    # Limit pairwise: hash into buckets
    buckets = defaultdict(list)
    for h, im in hashes:
        buckets[h[:16]].append((h, im))
    for bucket in buckets.values():
        for (h1, a), (h2, b) in combinations(bucket, 2):
            ham = sum(x != y for x, y in zip(h1, h2))
            if ham <= 10 and a["md5"] != b["md5"]:
                if Path(a["name"]).name != Path(b["name"]).name or a["zip"] != b["zip"]:
                    near.append(
                        {
                            "hamming": ham,
                            "a": f"{a['zip']}::{a['name']}",
                            "b": f"{b['zip']}::{b['name']}",
                        }
                    )
    return {
        "n_images": len(imgs),
        "n_identical_md5_groups": len(identical),
        "identical": [
            [{"zip": x["zip"], "name": x["name"], "bytes": x["n"]} for x in g]
            for g in identical[:40]
        ],
        "n_near": len(near),
        "near": sorted(near, key=lambda x: x["hamming"])[:40],
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = {
        "hdac6_POSITIVE": list((ROOT / "hdac6").glob("*.xlsx")),
        "lgr4_POSITIVE": list((ROOT / "lgr4").glob("*.xlsx")),
        "lei_xiangya": list((ROOT / "lei").rglob("*.xlsx")),
        "luo_xiangya": list((ROOT / "luo").glob("*.xlsx")),
        "wangqg_tongji": list((ROOT / "wangqg").glob("*.xlsx")),
        "su_shu": [p for p in (ROOT / "su").glob("*.xlsx") if p.stat().st_size < 2_000_000],
        "qiu_sjtu": [
            p
            for p in (ROOT / "qiu").glob("*.xlsx")
            if "MOESM3" not in p.name  # skip bulk sequencing table
        ],
        "kuang_ncb": [
            p
            for p in (ROOT / "kuang_ncb").glob("*.xlsx")
            if p.stat().st_size < 500_000  # skip bulk matrices
        ],
    }
    all_out = {}
    for paper, paths in jobs.items():
        print(f"\n======== {paper} n={len(paths)} ========", flush=True)
        findings = scan_paper(paper, paths)
        counts = Counter(f.get("type") for f in findings)
        all_out[paper] = {"n_files": len(paths), "counts": dict(counts), "findings": findings}
        print("counts", dict(counts))
        for t in [
            "exact_duplicate_vector",
            "constant_offset",
            "shared_fractional_parts",
            "shared_fractional_parts_row",
            "affine_copy",
            "within_group_duplicate",
            "exact_duplicate_rowgroup",
            "precise_scalar_reuse",
            "permutation_duplicate_vector",
        ]:
            xs = [f for f in findings if f.get("type") == t]
            print(f"  {t}: {len(xs)}")
            for f in xs[:6]:
                print(
                    "   ",
                    f.get("file"),
                    f.get("loc") or f.get("loc_a"),
                    "||",
                    f.get("loc_b"),
                    "val",
                    f.get("value"),
                    "off",
                    f.get("offset"),
                    "rate",
                    f.get("rate"),
                    "a",
                    f.get("slope"),
                )
                if f.get("vals_a"):
                    print("      A", f["vals_a"][:8])
                    print("      B", (f.get("vals_b") or [])[:8])
                if f.get("group"):
                    print("      G", f["group"])
                la = (f.get("label") or f.get("label_a") or "")[:120]
                if la:
                    print("      L", la)

    print("\n===== Lei Fig1 vs ED6 =====", flush=True)
    cmp = lei_fig1_vs_ed6()
    all_out["lei_fig1_vs_ed6"] = cmp
    print(cmp)

    print("\n===== Image hashes =====", flush=True)
    try:
        img = image_hashes()
        # drop raw
        all_out["lei_images"] = {k: img[k] for k in img}
        print("n_images", img["n_images"], "identical_groups", img["n_identical_md5_groups"], "near", img["n_near"])
        for g in img["identical"][:15]:
            print(" IDENT", g)
        for n in img["near"][:15]:
            print(" NEAR", n)
    except Exception as e:
        print("image fail", e)
        all_out["lei_images"] = {"error": str(e)}

    (OUT / "scan_results.json").write_text(json.dumps(all_out, indent=2, default=str))
    print("WROTE", OUT / "scan_results.json")


if __name__ == "__main__":
    main()
