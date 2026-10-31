#!/usr/bin/env python3
"""Write an ADDITIVE refreshed registry manifest for the nine focus repos.

Reuses the frozen tool's helpers (api, fetch, SITES) from scripts/registry_snapshot.py, which is
deliberately NOT modified: its hash is pinned in evidence/release_checks.json by an earlier review.

Differences from `registry_snapshot.py --refresh`:
  * writes to a NEW manifest path (--out); refuses to overwrite any existing file
  * caches blobs under a NEW directory (--cache-dir), so frozen cache files are never replaced
    (a blob at the same repo path can change between snapshots)

Every blob is verified by Git blob SHA1 and size before its SHA256 is recorded (fail-closed).
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from registry_snapshot import SITES, api, fetch  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True, help='new manifest path, relative to repo root')
    ap.add_argument('--cache-dir', required=True, help='new blob cache directory, relative to repo root')
    args = ap.parse_args()
    manifest_path = ROOT / args.out
    if manifest_path.exists():
        raise SystemExit(f'refusing to overwrite existing manifest: {args.out}')
    cache_dir = args.cache_dir.rstrip('/')

    m = dict(snapshot_utc=datetime.now(timezone.utc).isoformat(),
             scope='All TIFF blobs outside data/ in nine public focus repos; not other sites/private submissions.',
             refs={}, rasters=[])
    for site in SITES:
        repo = f'GEMSDOE{site}'
        ref = api(f'repos/buffedlizard55-lab/{repo}/commits/main')['sha']
        tree = api(f'repos/buffedlizard55-lab/{repo}/git/trees/{ref}?recursive=1')
        if tree.get('truncated'):
            raise SystemExit('truncated tree: ' + repo)
        m['refs'][repo] = ref
        for x in tree['tree']:
            p = x['path']
            if x['type'] == 'blob' and p.lower().endswith(('.tif', '.tiff')) and not p.startswith('data/'):
                m['rasters'].append(dict(owner='buffedlizard55-lab', repo=repo, ref=ref, path=p,
                                         blob_sha1=x['sha'], bytes=x['size'],
                                         local=f'{cache_dir}/{repo}/{p}'))
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(fetch, m['rasters']))
    m['rasters'] = rows
    m['failed'] = sum(x['status'] != 'verified' for x in rows)
    m['complete_within_scope'] = m['failed'] == 0
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(m, indent=2, allow_nan=False) + '\n')
    print(json.dumps(dict(out=args.out, rasters=len(rows), failed=m['failed'], refs=m['refs']), indent=2))
    if m['failed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
