#!/usr/bin/env python3
"""Restore pinned shared template and its owner-mirrored core/external data.

Uses the shared restore script unchanged; does not rebuild the cached feature
stack, authenticate the mirrors as organizer data, train a model, or make a
submission. Large data live in .cache/ and are deliberately not committed.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache"
REF = "1398109a23f04a2ace71c1bd2f527cfba87860b5"
ARCHIVE_SHA256 = "911dcb80f88d236b8c44350bee82f1418315afb578b83a64ad218498a68ae44a"
TOOL_HASHES = {
    "scripts/evaluate_holdout.py": "d786273021c86b62af2504060309554218ca1442ed84d717f13334dddeea892c",
    "scripts/submission_writer.py": "cf7eb9948cfe5032e1db2362ddd5a075c2c744bb33ebbcfb2ba2b5ebd1b1de9b",
    # These are used when running the restored shared-data utility. Never execute
    # a cached copy of it (or its manifest/imports) without checking the pins.
    "scripts/restore_data.py": "46d97fd30dea0b7ae62e0286f837059ad08828e7f74d49498693dc7dce50670f",
    "registry/data_manifest.json": "79539e073c91bb4a45babb42af187a622a451d38b35f15d5850aed005e14a278",
    "src/gems32/__init__.py": "e4a584f79eab8c0db81b5704b1525536fef2dcee5bac28da1455a39868983504",
    "src/gems32/paths.py": "ceb7c79097958beff1f618e608491c3528341b14ee8b2e9cdcfafe1406230b69",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_archive(archive: Path, destination: Path) -> None:
    """Extract only regular files under the single archive root; reject links."""
    expected_root = f"GEMSDOE32-{REF}"
    with tarfile.open(archive, "r:gz") as tar:
        for item in tar:
            name = PurePosixPath(item.name)
            if name.is_absolute() or ".." in name.parts or not name.parts or name.parts[0] != expected_root:
                raise ValueError(f"Unsafe archive path: {item.name}")
            relative = Path(*name.parts[1:])
            if not relative.parts:
                continue
            target = destination / relative
            if item.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif item.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                src = tar.extractfile(item)
                if src is None:
                    raise ValueError(f"Cannot read archive member: {item.name}")
                with src, target.open("wb") as output:
                    shutil.copyfileobj(src, output)
            else:
                raise ValueError(f"Refusing non-regular archive member: {item.name}")


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    archive = CACHE / f"template-{REF}.tar.gz"
    template = CACHE / "template" / REF
    try:
        if not archive.is_file() or digest(archive) != ARCHIVE_SHA256:
            partial = archive.with_suffix(".partial")
            try:
                req = urllib.request.Request(
                    f"https://codeload.github.com/buffedlizard55-lab/GEMSDOE32/tar.gz/{REF}",
                    headers={"User-Agent": "gems-ass1-reproducible-audit"},
                )
                with urllib.request.urlopen(req, timeout=120) as response, partial.open("wb") as out:
                    shutil.copyfileobj(response, out)
                if digest(partial) != ARCHIVE_SHA256:
                    raise ValueError("Template archive hash mismatch")
                os.replace(partial, archive)
            finally:
                partial.unlink(missing_ok=True)
        if not template.exists():
            template.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=template.parent, prefix="extract-") as temp:
                work = Path(temp) / "template"
                work.mkdir()
                extract_archive(archive, work)
                os.replace(work, template)
        for rel, expected in TOOL_HASHES.items():
            if digest(template / rel) != expected:
                raise ValueError(f"Cached shared tool changed: {rel}")
        if shutil.which("gh") is None:
            raise ValueError("GitHub CLI is required; the shared utility's alternate network endpoint is not used")
        target = CACHE / "gems_data"
        for group in ("core", "external"):
            subprocess.run([sys.executable, str(template / "scripts" / "restore_data.py"),
                            "--group", group, "--target-dir", str(target)], check=True)
        print(f"Pinned shared tools: {template}")
        print(f"Owner-mirror inputs: {target}; hashes match template manifest, not organizer-authenticated.")
        print("STOP: prepared feature cache and an assigned lane are still required; no model was run.")
        return 0
    except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as exc:
        print(f"Restore failed; release remains blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
