#!/usr/bin/env python3
"""Restore the hash-pinned bridge from LOCAL git clones (no GitHub API calls).

Why this exists: the shared ``vendor/gems57/prepare_data.py`` fetches every pin
through ``gh api``.  In this sandbox the GH_TOKEN in the environment is rejected
by ``gh auth status`` ("token ... is no longer valid") and the unauthenticated
core quota (5000/h, now shared) was exhausted, so every ``gh api`` call fails
with HTTP 403.  The git protocol (``git clone``/``sparse-checkout``) is NOT
subject to that quota and works, so this script performs the identical work --
same pins, same digests, same assembler, same band cacher, reused from the
vendored template -- taking the bytes from a local checkout instead.

Nothing here relaxes a pin: every file is re-hashed against ``PIN`` and the run
fails closed on any mismatch.  Provenance is unchanged and remains
"hash-verified public bridge; NOT organizer-authenticated".

Usage:
    python scripts/local_restore.py --probe6 /tmp/probe6 [--probe24 /tmp/probe24] [--cache-bands]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vendor.gems57.prepare_data import (  # noqa: E402  reused, not forked
    BRIDGE_COMMIT, BRIDGE_REPO, PARTS, PIN, assemble_features, cache_bands, sha256,
)

# Local clone layout probing: (clone_root, [relative paths to try])
CANDIDATES = {
    "data/official/labels.tif": ["data/labels.tif", "data/bridge/labels.tif", "data/official/labels.tif"],
    "data/official/existing_faults.tif": [
        "data/bridge/existing_faults.tif", "data/existing_faults.tif", "data/bridge/existing_faults.tif"],
    "data/official/sample_submission.tif": [
        "data/sample_submission.tif", "data/bridge/sample_submission.tif",
        "data/bridge/example_submission.tif", "data/official/sample_submission.tif"],
}


def copy_from_clones(target: Path, digest: str, clones: list[Path], rels: list[str], reuse: list[Path]) -> str:
    if target.exists() and sha256(target) == digest:
        return "already-present"
    for extra in reuse:                        # repo's own data/bridge first (verified bytes)
        if extra.exists() and sha256(extra) == digest:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(extra, target)
            return f"copied from {extra}"
    for clone in clones:
        for rel in rels:
            src = clone / rel
            if src.is_file() and src.stat().st_size == target.stat().st_size if target.exists() else True:
                if sha256(src) == digest:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, target)
                    return f"copied from {clone.name}:{rel}"
    raise SystemExit(f"could not locate a local copy matching {digest[:12]} for {target.name}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--probe6", default="/tmp/probe6", help="local clone of 6GEMSDOE at the pinned commit")
    ap.add_argument("--probe24", default="/tmp/probe24", help="local clone of GEMSDOE24 at the pinned commit")
    ap.add_argument("--cache-bands", action="store_true")
    a = ap.parse_args()

    clones = [Path(p) for p in (a.probe6, a.probe24) if Path(p).is_dir()]
    if not clones:
        raise SystemExit("no local clone directories were found; pass --probe6/--probe24")
    reuse = [ROOT / "data/bridge/existing_faults.tif", ROOT / "data/bridge/sample_submission.tif"]

    receipt = dict(evidence_class="DATA-MEASUREMENT",
                   provenance="hash-verified public bridge; NOT organizer-authenticated",
                   transport="local git clone (gh api unavailable: invalid GH_TOKEN + exhausted quota)",
                   source_repo=BRIDGE_REPO, source_commit=BRIDGE_COMMIT, files=[], all_pins_verified=False)

    # 1. the 419 MB stack: assembled by the vendored assembler from .cache/source_parts
    parts = [ROOT / ".cache" / "source_parts" / f"gems-geodawn-numerical-features.tif.part-{i:03d}"
             for i in range(5)]
    have_parts = all(p.is_file() for p in parts)
    target = ROOT / "data/official/training_features.tif"
    if not (target.exists() and sha256(target) == PIN["data/official/training_features.tif"]):
        if not have_parts:
            raise SystemExit("feature-stack parts are missing from .cache/source_parts")
        got = [(p.stat().st_size, sha256(p)) for p in parts]
        want = [(size, digest) for size, digest in PARTS]
        if got != want:
            raise SystemExit("feature-stack part digests do not match the pin")
        receipt["assembly"] = assemble_features(ROOT)
    receipt["files"].append(dict(path="data/official/training_features.tif",
                                 sha256=sha256(target), expected_sha256=PIN["data/official/training_features.tif"],
                                 verified=sha256(target) == PIN["data/official/training_features.tif"],
                                 bytes=target.stat().st_size))

    # 2. small bridge rasters
    for relative, rels in CANDIDATES.items():
        path = ROOT / relative
        origin = copy_from_clones(path, PIN[relative], clones, rels, reuse)
        ok = path.exists() and sha256(path) == PIN[relative]
        receipt["files"].append(dict(path=relative, sha256=sha256(path) if path.exists() else None,
                                     expected_sha256=PIN[relative], verified=ok,
                                     bytes=path.stat().st_size if path.exists() else None, origin=origin))
        print(f"[data] {'OK' if ok else 'MISMATCH'} {relative} ({origin})", flush=True)

    receipt["all_pins_verified"] = bool(all(f["verified"] for f in receipt["files"]))
    (ROOT / "evidence").mkdir(exist_ok=True)
    (ROOT / "evidence/local_restore.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")

    if receipt["all_pins_verified"] and a.cache_bands:
        report = cache_bands(ROOT)
        print(f"[data] cached {report['count']} bands (ignored by Git)", flush=True)
    print("[data] " + ("ALL PINS VERIFIED" if receipt["all_pins_verified"] else "PIN CHECK FAILED"))
    return 0 if receipt["all_pins_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
