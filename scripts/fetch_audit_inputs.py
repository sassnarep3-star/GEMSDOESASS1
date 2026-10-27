#!/usr/bin/env python3
"""Fetch a small, pinned owner-mirror audit set; never claim organizer authenticity.

This fetches nine historical TIFFs, five later research candidate TIFFs and three
preflight inputs. It is not the complete registry or the feature stack. The public GitHub
CLI may need authentication to avoid rate limits. No credentials are stored.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "focus_sources.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def destination(entry: dict, cache: Path) -> Path:
    # Filenames are local identifiers, not uncontrolled repository paths.
    name = entry.get("id") or entry["site"]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValueError(f"Unsafe local identifier: {name!r}")
    return cache / (name + ".tif")


def validate_unique_destinations(entries: list[dict], cache: Path) -> None:
    """Fail before downloading if two manifest entries could overwrite a cache file."""
    seen: set[Path] = set()
    for entry in entries:
        target = destination(entry, cache)
        if target in seen:
            raise ValueError(f"Duplicate local destination: {target.name}")
        seen.add(target)


def fetch(entry: dict, cache: Path) -> Path:
    repo, ref, path, expected = (entry[k] for k in ("repo", "ref", "path", "sha256"))
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Invalid repository")
    if not re.fullmatch(r"[0-9a-f]{40}", ref) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("Ref and SHA-256 must be immutable hexadecimal pins")
    if path.startswith("/") or ".." in Path(path).parts or "?" in path or "#" in path:
        raise ValueError("Invalid source path")
    cache.mkdir(parents=True, exist_ok=True)
    target = destination(entry, cache)
    if target.is_file() and sha256_file(target) == expected:
        return target
    partial = target.with_suffix(".tif.partial")
    endpoint = f"repos/{repo}/contents/{path}?ref={ref}"
    try:
        with partial.open("wb") as out:
            subprocess.run(
                ["gh", "api", endpoint, "-H", "Accept: application/vnd.github.raw"],
                stdout=out, check=True, timeout=180,
            )
        actual = sha256_file(partial)
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch for {repo}/{path}: {actual} != {expected}")
        os.replace(partial, target)
    finally:
        partial.unlink(missing_ok=True)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=ROOT / ".cache" / "audit-inputs")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    claims = json.loads((ROOT / "registry" / "claimed_candidates.json").read_text())
    try:
        entries = [*manifest["sources"], *manifest["auxiliary"], *claims["entries"]]
        validate_unique_destinations(entries, args.cache)
        for entry in entries:
            target = fetch(entry, args.cache)
            print(f"verified {target.name}: {entry['sha256']}")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Fetch failed; audit remains blocked: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
