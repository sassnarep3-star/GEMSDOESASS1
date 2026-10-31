#!/usr/bin/env python3
"""Measure how far the nine focus owner repos have moved since the frozen registry.

Compares three things per repo:
  1. frozen pin   -> registry/focus_inventory.json (immutable snapshot, 2026-10-27)
  2. refreshed    -> registry/focus_inventory_<tag>.json (additive snapshot; optional)
  3. live head    -> GitHub API `commits/main` at run time (needs gh auth or public API access)

Output: evidence/owner_head_drift_<tag>.json. Read-only against GitHub; writes only the evidence file.
A non-empty "new_blobs_since_frozen" means the frozen uniqueness registry is stale for that repo.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = [24, 25, 27, 28, 30, 31, 32, 33, 36]


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', path], timeout=90))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tag', default='20261030')
    ap.add_argument('--refreshed', default=None, help='optional refreshed manifest (relative to repo root)')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    frozen = json.loads((ROOT / 'registry/focus_inventory.json').read_text())
    refreshed = json.loads((ROOT / args.refreshed).read_text()) if args.refreshed else None
    frozen_blobs = {}
    for r in frozen['rasters']:
        frozen_blobs.setdefault(r['repo'], set()).add(r['blob_sha1'])

    repos = {}
    for site in SITES:
        repo = f'GEMSDOE{site}'
        head = api(f'repos/buffedlizard55-lab/{repo}/commits/main')
        tree = api(f'repos/buffedlizard55-lab/{repo}/git/trees/{head["sha"]}?recursive=1')
        if tree.get('truncated'):
            raise SystemExit(f'truncated tree: {repo}')
        head_tifs = [x for x in tree['tree'] if x['type'] == 'blob'
                     and x['path'].lower().endswith(('.tif', '.tiff')) and not x['path'].startswith('data/')]
        new_blobs = [x['path'] for x in head_tifs if x['sha'] not in frozen_blobs.get(repo, set())]
        entry = dict(
            frozen_pin=frozen['refs'][repo],
            live_head=head['sha'],
            live_head_committed_utc=head['commit']['committer']['date'],
            moved_since_frozen_pin=head['sha'] != frozen['refs'][repo],
            tif_blobs_at_live_head=len(head_tifs),
            tif_blobs_in_frozen_registry=len(frozen_blobs.get(repo, set())),
            new_blobs_since_frozen=len(new_blobs),
            new_blob_paths=sorted(new_blobs),
        )
        if refreshed is not None:
            entry['refreshed_pin'] = refreshed['refs'][repo]
            entry['refreshed_matches_live_head'] = refreshed['refs'][repo] == head['sha']
        repos[repo] = entry
        print(repo, 'moved' if entry['moved_since_frozen_pin'] else 'same', 'new_blobs', len(new_blobs), flush=True)

    out = dict(
        schema='owner-head-drift-v1',
        tag=args.tag,
        checked_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),
        frozen_manifest=dict(path='registry/focus_inventory.json', snapshot_utc=frozen['snapshot_utc']),
        refreshed_manifest=args.refreshed,
        repos=repos,
        totals=dict(
            repos_moved=sum(v['moved_since_frozen_pin'] for v in repos.values()),
            new_blobs_since_frozen=sum(v['new_blobs_since_frozen'] for v in repos.values()),
            tif_blobs_at_live_heads=sum(v['tif_blobs_at_live_head'] for v in repos.values()),
        ),
        note='Blob-level comparison uses git blob SHA1 from the GitHub trees API. Byte-identical files under new names count as new paths but are not new bytes.',
    )
    out_path = ROOT / (args.out or f'evidence/owner_head_drift_{args.tag}.json')
    if out_path.exists():
        raise SystemExit(f'refusing to overwrite {out_path.relative_to(ROOT)}')
    out_path.write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
    print('totals', out['totals'])
    print('wrote', out_path.relative_to(ROOT))


if __name__ == '__main__':
    sys.exit(main())
