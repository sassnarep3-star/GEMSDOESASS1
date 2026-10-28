"""Regression tests for the withdrawn SWGB release decision."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_witness_receipt_is_negative_and_identifies_the_actual_bytes():
    receipt = json.loads((ROOT / 'evidence/swgb_witness_review.json').read_text())
    candidate = ROOT / receipt['local_format_validation']['file']
    assert hashlib.sha256(candidate.read_bytes()).hexdigest() == receipt['input_sha256']['candidate']
    assert receipt['local_format_validation']['all_checks_passed']
    assert receipt['directed_overlap_within_3px'] > receipt['overlap_limit']
    assert receipt['duplicate'] and not receipt['approved_for_submission']
    assert receipt['verdict'] == 'negative'
    assert 'not a complete registry scan' in receipt['scope']


def test_historical_builder_stops_before_writing():
    candidate_dir = ROOT / 'swgb/downloads'
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in candidate_dir.iterdir() if p.is_file()}
    p = subprocess.run([sys.executable, 'scripts/build_submission.py'], cwd=ROOT, capture_output=True, text=True)
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in candidate_dir.iterdir() if p.is_file()}
    assert p.returncode != 0 and 'BLOCKED' in p.stderr
    assert before == after


def test_active_swgb_pages_fail_closed():
    result = subprocess.run([sys.executable, 'scripts/swgb_build_site.py'], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0 and 'BLOCKED' in result.stderr
    for name in ('index.html', 'how-to-submit.html', 'run-card.html', 'hypotheses.html'):
        html = (ROOT / 'swgb' / name).read_text()
        assert 'Do not submit' in html and 'not approved' in html.lower()
        assert 'href="downloads/' not in html and 'OK TO DOWNLOAD AND SUBMIT' not in html
    root = (ROOT / 'index.html').read_text()
    assert 'not approved' in root.lower() and 'DO NOT SUBMIT' in root
