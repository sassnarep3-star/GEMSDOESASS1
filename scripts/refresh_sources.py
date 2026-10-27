#!/usr/bin/env python3
"""Refresh *GitHub repository metadata only*, never DrivenData or score claims."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
HEADS = ROOT / "registry" / "observed_heads.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_head(repo: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("invalid repo")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "gems-ass1-source-status"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/commits/main", headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read(2_000_001)
    if len(body) > 2_000_000:
        raise ValueError("oversized response")
    sha = json.loads(body)["sha"]
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("invalid commit SHA")
    return sha


def build_feed(baseline: dict, fetch=read_head) -> dict:
    def one(item: tuple[str, dict]) -> dict:
        site, spec = item
        when = now()
        row = {"site": site, "repo": spec["repo"], "baseline_ref": spec["ref"],
               "observed_utc": when, "current_ref": None, "status": "unavailable",
               "repo_url": f"https://github.com/{spec['repo']}"}
        try:
            current = fetch(spec["repo"])
            if not isinstance(current, str) or not re.fullmatch(r"[0-9a-f]{40}", current):
                raise ValueError("invalid commit SHA")
            row.update({"current_ref": current,
                        "status": "unchanged" if current == spec["ref"] else "changed"})
        except (OSError, ValueError, KeyError, json.JSONDecodeError, urllib.error.URLError) as exc:
            # Do not preserve an old successful value as though it were current.
            row["error"] = type(exc).__name__
        return row

    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(one, baseline["refs"].items()))
    return {
        "generated_utc": now(),
        "baseline_observed_utc": baseline["checked_utc"],
        "scope": "GitHub main-branch metadata only; not a score, slot quota, or complete raster registry.",
        "status": "complete" if all(row["status"] != "unavailable" for row in rows) else "partial",
        "sites": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "docs" / "data" / "feed.json")
    parser.add_argument("--require-complete", action="store_true", help="Exit nonzero if any head is unavailable")
    args = parser.parse_args()
    baseline = json.loads(HEADS.read_text())
    feed = build_feed(baseline)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temp = args.out.with_suffix(".json.partial")
    temp.write_text(json.dumps(feed, indent=2) + "\n")
    os.replace(temp, args.out)
    changed = sum(row["status"] == "changed" for row in feed["sites"])
    unavailable = sum(row["status"] == "unavailable" for row in feed["sites"])
    print(f"GitHub metadata feed: {feed['status']} ({len(feed['sites'])} sites, {changed} changed, {unavailable} unavailable); no DrivenData access.")
    return 1 if args.require_complete and feed["status"] != "complete" else 0


if __name__ == "__main__":
    raise SystemExit(main())
