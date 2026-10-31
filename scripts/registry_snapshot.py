#!/usr/bin/env python3
"""Enumerate and fetch ALL TIFFs outside data/ from nine focus repositories.

Pins a consistent commit per repo, verifies Git blob SHA1 and size, records SHA256.
No filename or 8 MB heuristic can silently remove a prior. Non-prediction grids
are retained for explicit classification by the audit. Fails closed on missing files.

Fetch order (2026-10-31 template fix, reported per protocol item 2): the GitHub REST
API (``gh api``) first; on failure — e.g. exhausted REST rate limits — an exact
git-protocol fallback reads the same pinned blob from a partial mirror clone of the
same repository and re-verifies the identical blob SHA1 and byte size. The git
protocol is not subject to the REST quota, so long sessions no longer strand the
registry in a permanently incomplete state. Both paths verify the same pinned bytes.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading

ROOT = Path(__file__).resolve().parents[1]
SITES = [24, 25, 27, 28, 30, 31, 32, 33, 36]
_GIT_LOCK = threading.Lock()


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', path], timeout=90))


def blob_sha(b):
    return hashlib.sha1(f'blob {len(b)}\0'.encode() + b).hexdigest()


def git_blob(repo: str, ref: str, path: str) -> bytes:
    """Exact blob bytes from a pinned commit via the git protocol (no REST quota)."""
    mirror = ROOT / '.cache' / 'gitmirror' / repo
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0')
    with _GIT_LOCK:
        if not (mirror / '.git').exists():
            mirror.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['git', 'clone', '--quiet', '--filter=blob:none', '--no-checkout',
                            f'https://github.com/buffedlizard55-lab/{repo}.git', str(mirror)],
                           check=True, timeout=900, env=env)
        if subprocess.run(['git', '-C', str(mirror), 'cat-file', '-e', f'{ref}^{{commit}}'],
                          capture_output=True).returncode != 0:
            subprocess.run(['git', '-C', str(mirror), 'fetch', '--quiet', '--filter=blob:none',
                            'origin', ref], check=True, timeout=900, env=env)
        result = subprocess.run(['git', '-C', str(mirror), 'cat-file', 'blob', f'{ref}:{path}'],
                                capture_output=True, check=True, timeout=600, env=env)
    return result.stdout


def fetch(row):
    dest = ROOT / row['local']
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        if not dest.exists() or blob_sha(dest.read_bytes()) != row['blob_sha1']:
            try:
                result = subprocess.run(['gh', 'api',
                    f"repos/{row['owner']}/{row['repo']}/contents/{row['path']}?ref={row['ref']}",
                    '-H', 'Accept: application/vnd.github.raw'], capture_output=True, check=True, timeout=180)
                b = result.stdout
            except Exception as api_error:
                b = git_blob(row['repo'], row['ref'], row['path'])
                api_error_repr = f'{type(api_error).__name__}: {str(api_error)[:180]}'
            else:
                api_error_repr = ''
            if blob_sha(b) != row['blob_sha1'] or len(b) != row['bytes']:
                raise ValueError('Git blob/size mismatch')
            tmp = dest.with_suffix('.partial')
            tmp.write_bytes(b)
            tmp.replace(dest)
            if api_error_repr:
                row['fetch_note'] = 'restored via git-protocol fallback after: ' + api_error_repr
        b = dest.read_bytes()
        return dict(row, sha256=hashlib.sha256(b).hexdigest(), status='verified')
    except Exception as error:
        return dict(row, status='failed', error=str(error)[:300])



def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--refresh', action='store_true', help='explicitly resolve new commits; default restores frozen inventory')
    args = ap.parse_args()
    manifest_path = ROOT / 'registry/focus_inventory.json'
    if manifest_path.exists() and not args.refresh:
        m = json.loads(manifest_path.read_text())
    else:
        m = dict(snapshot_utc=datetime.now(timezone.utc).isoformat(), scope='All TIFF blobs outside data/ in nine public focus repos; not other sites/private submissions.', refs={}, rasters=[])
        for site in SITES:
            repo = f'GEMSDOE{site}'
            ref = api(f'repos/buffedlizard55-lab/{repo}/commits/main')['sha']
            tree = api(f'repos/buffedlizard55-lab/{repo}/git/trees/{ref}?recursive=1')
            if tree.get('truncated'):
                raise ValueError('truncated tree: ' + repo)
            m['refs'][repo] = ref
            for x in tree['tree']:
                p = x['path']
                if x['type'] == 'blob' and p.lower().endswith(('.tif', '.tiff')) and not p.startswith('data/'):
                    m['rasters'].append(dict(owner='buffedlizard55-lab', repo=repo, ref=ref,
                        path=p, blob_sha1=x['sha'], bytes=x['size'], local=f'.cache/registry/{repo}/{p}'))
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(fetch, m['rasters']))
    m['rasters'] = rows
    m['failed'] = sum(x['status'] != 'verified' for x in rows)
    m['complete_within_scope'] = m['failed'] == 0
    manifest_path.write_text(json.dumps(m, indent=2, allow_nan=False) + '\n')
    print(json.dumps(dict(rasters=len(rows), failed=m['failed'], refs=m['refs']), indent=2))
    if m['failed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
