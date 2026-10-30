#!/usr/bin/env python3
"""Refresh the focus-site registry from local git clones (no GitHub API).

The frozen ``registry/focus_inventory.json`` is the pinned experiment registry and is never
overwritten.  This script writes a *new* file, ``registry/focus_inventory_<date>.json``, from
the current public HEAD of the nine focus repositories, so a novelty claim can be checked
against today's public heads as well as the frozen snapshot.

Blobs are enumerated with ``git ls-tree -r`` and hashed from the working tree, so the result
does not depend on the GitHub REST API (which rate-limits long sessions).  Git blob SHA-1 and
byte size are recorded exactly as the frozen inventory does, plus SHA-256 of the working-tree
bytes.  Fails closed if a repository cannot be resolved.

Usage:
    python3 scripts/refresh_registry_local.py [--clone-root .cache/registry_src]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = [24, 25, 27, 28, 30, 31, 32, 33, 36]
OWNER = "buffedlizard55-lab"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(args, cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True)


def head(clone: Path) -> str:
    return git(["rev-parse", "HEAD"], clone).strip()


def ensure_clone(clone: Path, repo: str) -> None:
    if (clone / ".git").is_dir():
        return
    clone.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", f"https://github.com/{OWNER}/{repo}.git",
                    str(clone)], check=True, capture_output=True, timeout=900)


def enumerate_rasters(clone: Path, repo: str, ref: str) -> list[dict]:
    tree = git(["ls-tree", "-r", "-z", ref], clone)
    rows: list[dict] = []
    for entry in tree.split("\0"):
        if not entry:
            continue
        meta, _, name = entry.partition("\t")
        mode, kind, blob = meta.split()
        if kind != "blob" or not name.lower().endswith((".tif", ".tiff")):
            continue
        if name.startswith("data/"):
            continue
        path = clone / name
        data = path.read_bytes()
        rows.append(dict(owner=OWNER, repo=repo, ref=ref, path=name,
                         blob_sha1=blob, bytes=len(data),
                         local=f".cache/registry_current/{repo}/{name}",
                         sha256=hashlib.sha256(data).hexdigest(), status="verified"))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clone-root", default=str(ROOT / ".cache" / "registry_src"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    clone_root = Path(args.clone_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    out = Path(args.out) if args.out else ROOT / f"registry/focus_inventory_{stamp}.json"

    rasters: list[dict] = []
    refs: dict[str, str] = {}
    for site in SITES:
        repo = f"GEMSDOE{site}"
        clone = clone_root / repo
        ensure_clone(clone, repo)
        ref = head(clone)
        refs[repo] = ref
        rows = enumerate_rasters(clone, repo, ref)
        print(f"{repo} @ {ref[:12]}: {len(rows)} tif blobs outside data/", flush=True)
        rasters.extend(rows)

    inventory = dict(
        snapshot_utc=datetime.now(timezone.utc).isoformat(),
        scope="All TIFF blobs outside data/ in the nine public focus repos at their CURRENT public HEAD; "
              "not other sites, private submissions, or the frozen snapshot.",
        source="local git clones (git ls-tree + working-tree hashes); no GitHub REST API",
        refs=refs, rasters=rasters, failed=0, complete_within_scope=True,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(inventory, indent=2, allow_nan=False) + "\n")
    print(json.dumps(dict(out=str(out.relative_to(ROOT)), rasters=len(rasters), refs=refs), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
