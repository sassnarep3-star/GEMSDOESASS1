#!/usr/bin/env python3
"""Restore the pinned 2026-10-30 registry (489 TIFFs, nine focus repos) with git sparse checkout.

Why not the REST contents API: `gh api .../contents/...` consumed the core rate limit
(5,000/h) mid-run on 2026-10-31. Git over HTTPS has a separate quota, so this uses
`git clone --depth 1 --filter=blob:none --sparse` per repository, checks out only the
prediction directories, and verifies every file against the SHA-256 recorded in
registry/focus_inventory_20261030.json. A mismatch is reported, never silently accepted.

Files are placed at the `.local` path recorded in the inventory (git-ignored .cache/).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / 'registry/focus_inventory_20261030.json'
# every pinned path is checked out explicitly: the inventory contains files in docs/research/,
# archive/ and inputs/calibration/ that a directory wildcard list would silently skip.
def sparse_patterns(rows) -> list[str]:
    return ['/' + r['path'] for r in rows]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def clone_and_collect(repo: str, rows: list[dict], dest_tmp: Path) -> None:
    url = f'https://github.com/buffedlizard55-lab/{repo}.git'
    subprocess.run(['git', 'clone', '-q', '--depth', '1', '--filter=blob:none', '--sparse', url, str(dest_tmp)],
                   check=True, timeout=1800)
    subprocess.run(['git', 'sparse-checkout', 'set', '--no-cone', *sparse_patterns(rows)], cwd=dest_tmp,
                   check=True, timeout=1800, input=None)
    # sparse-checkout materialises lazily; touching the working tree forces the blobs to download
    subprocess.run(['git', 'checkout', '--', '.'], cwd=dest_tmp, check=True, timeout=1800)


def main() -> int:
    inv = json.loads(INVENTORY.read_text())
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for row in inv['rasters']:
        by_repo[row['repo']].append(row)
    tmp_root = Path(tempfile.mkdtemp(prefix='registry_git_'))
    verified, failed = 0, []
    try:
        for repo, rows in sorted(by_repo.items()):
            target = tmp_root / repo
            try:
                clone_and_collect(repo, rows, target)
            except subprocess.SubprocessError as error:
                failed.extend(dict(repo=repo, path=r['path'], error=f'clone failed: {error}'[:300]) for r in rows)
                continue
            for row in rows:
                src = target / row['path']
                dest = ROOT / row['local']
                if not src.exists():
                    failed.append(dict(repo=repo, path=row['path'], error='missing after sparse checkout'))
                    continue
                b = src.read_bytes()
                if sha256(b) != row['sha256'] or len(b) != row['bytes']:
                    failed.append(dict(repo=repo, path=row['path'],
                                       error=f'content differs from pinned ref (sha256 {sha256(b)[:12]}, '
                                             f'bytes {len(b)} vs {row["bytes"]})'))
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dest)
                verified += 1
            print(f'{repo}: {sum(1 for r in rows if (ROOT / r["local"]).exists())}/{len(rows)} present', flush=True)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
    out = dict(inventory=str(INVENTORY.relative_to(ROOT)), snapshot_utc=inv['snapshot_utc'], scope=inv['scope'],
               rasters=len(inv['rasters']), verified=verified, failed=len(failed), failures=failed,
               method='git sparse checkout (blobless clone) + SHA-256 verification against the pinned inventory')
    (ROOT / 'evidence/registry_restore_20261031.json').write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k != 'failures'}, indent=2))
    if failed:
        print(json.dumps(failed[:10], indent=2))
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
