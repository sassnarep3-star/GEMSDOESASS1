#!/usr/bin/env python3
"""Git-clone fallback restore of the frozen 414-raster registry (no GitHub API quota).

Same pins as scripts/registry_snapshot.py (registry/focus_inventory.json): one pinned commit
per repo, sparse checkout of docs/downloads/, Git-blob-SHA1 verification per file, and the
sha256 pins already stored in the inventory. Fails closed on any mismatch.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "registry" / "focus_inventory.json"


def blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ensure_repo(repo: str, ref: str, items: list[dict]) -> Path:
    dest = ROOT / ".cache" / "git-registry" / repo
    dest.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        subprocess.run(["git", "init", "-q", str(dest)], check=True)
        subprocess.run(["git", "-C", str(dest), "remote", "add", "origin",
                        f"https://github.com/buffedlizard55-lab/{repo}.git"], check=True)
    # sparse patterns: every directory that contains an inventory file, from the inventory itself
    dirs = sorted({"/" + str(Path(r["path"]).parent).replace(os.sep, "/") + "/*" for r in items})
    head = subprocess.run(["git", "-C", str(dest), "rev-parse", "HEAD"],
                          capture_output=True, text=True)
    cur = head.stdout.strip() if head.returncode == 0 else ""
    if cur != ref:
        subprocess.run(["git", "-C", str(dest), "sparse-checkout", "init", "--no-cone"], check=True)
        subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", "--no-cone", *dirs],
                       check=True)
        subprocess.run(["git", "-C", str(dest), "fetch", "-q", "--depth", "1", "origin", ref],
                       check=True, timeout=1800)
        subprocess.run(["git", "-C", str(dest), "checkout", "-q", "FETCH_HEAD"], check=True)
    else:
        subprocess.run(["git", "-C", str(dest), "sparse-checkout", "add", "--no-cone", *dirs],
                       check=True)
    return dest


def main() -> None:
    inv = json.loads(INV.read_text())
    rows = inv["rasters"]
    by_repo: dict[str, list[dict]] = {}
    for r in rows:
        by_repo.setdefault(r["repo"], []).append(r)
    failed = 0
    for repo, items in by_repo.items():
        ref = items[0]["ref"]
        print(f"{repo}: {len(items)} rasters @ {ref[:10]}", flush=True)
        repo_dir = ensure_repo(repo, ref, items)

        def check(item: dict) -> dict:
            p = repo_dir / item["path"]
            if not p.exists():
                return dict(item, status="missing-in-sparse-checkout")
            b = p.read_bytes()
            if blob_sha1(b) != item["blob_sha1"] or len(b) != item["bytes"]:
                return dict(item, status="git-blob-mismatch")
            if sha256(b) != item.get("sha256", sha256(b)):
                return dict(item, status="sha256-mismatch")
            local = ROOT / item["local"]
            local.parent.mkdir(parents=True, exist_ok=True)
            if not local.exists():
                local.write_bytes(b)
            return dict(item, status="verified")

        with ThreadPoolExecutor(max_workers=4) as pool:
            out = list(pool.map(check, items))
        bad = [r for r in out if r["status"] != "verified"]
        failed += len(bad)
        print(f"  verified {len(out) - len(bad)}/{len(out)}", flush=True)
        for r in bad[:5]:
            print("  FAIL", r["path"], r["status"], flush=True)
    if failed:
        raise SystemExit(f"{failed} registry files failed verification")
    print("REGISTRY RESTORED", flush=True)


if __name__ == "__main__":
    sys.exit(main())
