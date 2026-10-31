#!/usr/bin/env python3
"""Pin the 2026-10-31 post-review implementation hashes into evidence/release_checks.json.

The frozen review (2026-10-27) pinned implementation files; verify_release.py allows a change
only when the new bytes are recorded in an explicit dated post-review map. This session fixed
shared tools (registry_snapshot.py, restore_externals.py — git-protocol fallback for the REST
quota; make_release.py — registry path bug) and made the site/verifiers active-release aware
(build_site.py, verify_release.py, check_release_entrypoints.py). Each file's new sha256 is
pinned here with the reason string, preserving the original fail-closed intent.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REASONS = {
    'scripts/registry_snapshot.py': '2026-10-31: git-protocol fallback for REST-quota failures; same pinned-blob verification (protocol item 2 fix).',
    'scripts/restore_externals.py': '2026-10-31: git-protocol fallback for REST-quota failures; same sha256/size verification (protocol item 2 fix).',
    'scripts/build_site.py': '2026-10-31: active-release selection (evidence/tiprelay then thermal), lane-dynamic text, tiprelay evidence mirror.',
    'scripts/verify_release.py': '2026-10-31: additive tiprelay release checks, tiprelay evidence mirror check, merged dated post-review maps.',
    'scripts/check_release_entrypoints.py': '2026-10-31: approved raster read from the active lane release (tiprelay first).',
    'scripts/make_release.py': '2026-10-31: registry exact-duplicate scan path fix (ROOT/rec[local]); --evidence-dir; loud failure on missing registry files.',
}


def main():
    path = ROOT / 'evidence/release_checks.json'
    data = json.loads(path.read_text())
    post = data.setdefault('post_review_2026-10-31_implementation_sha256', {})
    reasons = data.setdefault('post_review_2026-10-31_change_reasons', {})
    for relative, reason in REASONS.items():
        digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        post[relative] = digest
        reasons[relative] = reason
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    print('pinned', len(post), 'files under post_review_2026-10-31')


if __name__ == '__main__':
    main()
