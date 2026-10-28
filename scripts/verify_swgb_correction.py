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
for page in ('index.html', 'swgb/index.html', 'swgb/how-to-submit.html', 'swgb/run-card.html', 'swgb/hypotheses.html'):
    text = (ROOT / page).read_text()
    assert 'not approved' in text.lower(), page
    assert 'OK TO DOWNLOAD AND SUBMIT' not in text, page
assert 'BLOCKED: SWGB duplicate' in (ROOT / 'scripts/build_submission.py').read_text()
print('SWGB correction: negative release, artifact hash intact, website blocks submission')
