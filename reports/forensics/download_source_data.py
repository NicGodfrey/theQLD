#!/usr/bin/env python3
"""Download Nature source-data files for forensic mining."""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 research-integrity forensic"}
ROOT = Path("/tmp/forensics")


def fetch(url: str, dest: Path | None = None) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    if dest:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        print(f"  {dest}  {len(data)}")
    return data


def html(url: str) -> str:
    return fetch(url).decode("utf-8", "replace")


def media_xlsx_zip(page: str):
    items = []
    for m in re.finditer(
        r'data-track-label="([^"]+)" href="(https://media\.springernature\.com[^"]+)"',
        page,
    ):
        lab, href = m.group(1), m.group(2)
        if any(href.lower().endswith(ext) for ext in (".xlsx", ".xls", ".zip")):
            items.append((lab.lower(), href))
    return items


def download_labeled(paper_id: str, url: str, want_substr=None, skip_substr=None):
    print(f"==== {paper_id} {url}")
    page = html(url)
    items = media_xlsx_zip(page)
    print(f"  found {len(items)} xlsx/zip")
    out = ROOT / paper_id
    out.mkdir(parents=True, exist_ok=True)
    kept = []
    for lab, href in items:
        fname = href.split("/")[-1]
        if want_substr and not any(s in lab or s in fname.lower() for s in want_substr):
            continue
        if skip_substr and any(s in lab or s in fname.lower() for s in skip_substr):
            continue
        dest = out / fname
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"  SKIP {fname}")
        else:
            fetch(href, dest)
        kept.append((lab, dest))
    (out / "index.txt").write_text(
        "\n".join(f"{lab}\t{p.name}" for lab, p in kept) + "\n"
    )
    return kept


def main():
    ROOT.mkdir(parents=True, exist_ok=True)

    download_labeled(
        "lei",
        "https://www.nature.com/articles/s43587-024-00694-0",
        want_substr=["source data", "moesm11", "moesm12", "moesm13", "moesm4", "moesm3"],
    )
    download_labeled(
        "luo",
        "https://www.nature.com/articles/s41467-023-38842-6",
        want_substr=["xlsx", "source"],
    )
    download_labeled(
        "wangqg",
        "https://www.nature.com/articles/s41467-021-25561-z",
        want_substr=["xlsx", "source"],
    )
    download_labeled(
        "hdac6",
        "https://www.nature.com/articles/s41586-024-08248-5",
        want_substr=["source data"],
        skip_substr=["supplementary table", "pdf"],
    )
    download_labeled(
        "lgr4",
        "https://www.nature.com/articles/s43018-023-00715-8",
        want_substr=["source data"],
        skip_substr=["supplementary table", "pdf"],
    )
    download_labeled(
        "su",
        "https://www.nature.com/articles/s41565-025-02082-0",
        want_substr=["source data", "supplementary data", "xlsx"],
    )
    download_labeled(
        "kuang_ncb",
        "https://www.nature.com/articles/s41556-026-01876-1",
        want_substr=["source data"],
        skip_substr=["pdf"],
    )

    # Qiu Chd3: resolve search
    try:
        q = html("https://www.nature.com/search?q=In%20vivo%20base%20editing%20of%20Chd3")
        dois = sorted(set(re.findall(r"10\.1038/s41586-[^\"\s<]+", q)))
        hrefs = sorted(set(re.findall(r"/articles/s41586-[^\"\s]+", q)))
        print("QIU dois", dois)
        print("QIU hrefs", hrefs[:20])
        (ROOT / "qiu_search.txt").write_text(q[:5000])
        for h in hrefs[:5]:
            url = "https://www.nature.com" + h.split("?")[0]
            print(" try", url)
            try:
                page = html(url)
                title = re.search(r"<title>([^<]+)", page)
                print("  title", title.group(1)[:160] if title else "")
                if "Chd3" in page or "chd3" in page.lower():
                    (ROOT / "qiu.html").write_text(page)
                    items = media_xlsx_zip(page)
                    print("  media", len(items))
                    for lab, href in items:
                        print("   ", lab, href.split("/")[-1])
                        if href.lower().endswith((".xlsx", ".xls", ".zip")):
                            fetch(href, ROOT / "qiu" / href.split("/")[-1])
            except Exception as e:
                print("  fail", e)
    except Exception as e:
        print("QIU search fail", e)

    print("DONE")


if __name__ == "__main__":
    main()
