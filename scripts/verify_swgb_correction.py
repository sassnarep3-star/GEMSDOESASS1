#!/usr/bin/env python3
"""Offline release gate for the later SWGB negative correction; preserves frozen BGAC checks."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda path: json.loads((ROOT / path).read_text())
release = read('evidence/swgb/release_decision.json')
correction = read('evidence/swgb_lattice_audit.json')
artifact = ROOT / 'swgb/downloads' / release['submission_name']
original = read('evidence/swgb/run_card.json')
assert hashlib.sha256(artifact.read_bytes()).hexdigest() == release['raster_sha256'] == correction['candidate_sha256'] == original['raster_sha256']
assert correction['lattice_sha256'] == 'b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2'
assert (correction['within_3_pixels'], correction['candidate_dots']) == (44033, 44090)
assert correction['directed_overlap'] == 44033 / 44090 > .70
assert correction['duplicate'] and release['verdict'] == 'negative' and not release['approved_for_submission']
assert read('swgb/downloads/' + release['submission_name'].replace('.tif', '.checks.json'))['all_checks_passed']
# Page gates. The four SWGB pages stay strictly revoked: the approval phrase must never
# appear there. The root entry point may present the generated 2026-10-30 release verdict
# (a different, run-card-approved artifact), but only naming that exact raster — SWGB and
# every other historical file remain "not approved" and "do not submit" on every page.
pointer = read('evidence/current_release.json') if (ROOT / 'evidence/current_release.json').exists() else {}
card_path = pointer.get('run_card', 'evidence/thermal/run_card.json')
card = read(card_path) if (ROOT / card_path).exists() else {}
approved_name = card.get('raster_name') if card.get('ok_to_download_and_submit') else None
for page in ('index.html', 'swgb/index.html', 'swgb/how-to-submit.html', 'swgb/run-card.html', 'swgb/hypotheses.html'):
    text = (ROOT / page).read_text()
    assert 'not approved' in text.lower(), page
    if page == 'index.html':
        if 'OK TO DOWNLOAD AND SUBMIT' in text:
            assert approved_name and approved_name in text, 'root approval phrase must name the run-card-approved raster'
    else:
        assert 'OK TO DOWNLOAD AND SUBMIT' not in text, page
assert 'BLOCKED: SWGB duplicate' in (ROOT / 'scripts/build_submission.py').read_text()
print('SWGB correction: negative release, artifact hash intact, website blocks submission')
