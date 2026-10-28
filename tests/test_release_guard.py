"""Regression guards against resurfacing a superseded submission approval."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_frozen_witness_veto():
    audit = json.loads((ROOT / 'evidence/swgb_witness_audit.json').read_text())
    assert audit['duplicate'] and audit['directed_overlap_within_3px'] > 0.70
    assert audit['verdict'] == 'negative' and not audit['approved_for_submission']
    assert (ROOT / 'docs/evidence/swgb_witness_audit.json').read_bytes() == (ROOT / 'evidence/swgb_witness_audit.json').read_bytes()


def test_public_entry_points_do_not_recommend_submission():
    for page in ['index.html', 'swgb/index.html', 'swgb/how-to-submit.html', 'swgb/run-card.html', 'swgb/hypotheses.html']:
        text = (ROOT / page).read_text().lower()
        assert 'do not submit' in text
        assert 'ok to download and submit' not in text
        assert 'href="downloads/' not in text


def test_legacy_builders_fail_closed():
    for script in ['scripts/build_submission.py', 'scripts/swgb_build_site.py']:
        result = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, capture_output=True, text=True)
        assert result.returncode != 0
        assert 'blocked:' in result.stderr.lower()
