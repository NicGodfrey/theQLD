#!/usr/bin/env python3
"""Fetch stars/license/fork-status for candidate repos via GitHub GraphQL (batched)."""
import json
import subprocess
import sys

CAND = "/tmp/atelier-fable/02-top100/candidates.txt"
OUT = "/tmp/atelier-fable/02-top100/repo_data.json"

repos = [l.strip() for l in open(CAND) if l.strip()]
results = {}

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

for batch_idx, batch in enumerate(chunk(repos, 40)):
    parts = []
    for i, full in enumerate(batch):
        owner, name = full.split("/")
        parts.append(
            f'r{i}: repository(owner: "{owner}", name: "{name}") '
            '{ nameWithOwner stargazerCount isFork isArchived pushedAt '
            'licenseInfo { spdxId name } description }'
        )
    query = "query { " + " ".join(parts) + " }"
    proc = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0 and not proc.stdout:
        print(f"batch {batch_idx} failed: {proc.stderr[:500]}", file=sys.stderr)
        continue
    data = json.loads(proc.stdout).get("data") or {}
    for i, full in enumerate(batch):
        node = data.get(f"r{i}")
        if node is None:
            print(f"NOT FOUND: {full}", file=sys.stderr)
            continue
        lic = node.get("licenseInfo") or {}
        results[full] = {
            "repo": node["nameWithOwner"],
            "stars": node["stargazerCount"],
            "license": lic.get("spdxId") or lic.get("name") or "NONE",
            "is_fork": node["isFork"],
            "archived": node["isArchived"],
            "pushed_at": node["pushedAt"],
            "description": (node.get("description") or "")[:200],
        }

json.dump(results, open(OUT, "w"), indent=1)
print(f"fetched {len(results)}/{len(repos)}")
