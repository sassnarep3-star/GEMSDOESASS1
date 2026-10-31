"""Regression tests for the revoked SWGB release and literal overlap audit."""
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_swgb_lattice import compare


def write_tif(path, values, transform=None):
    with rasterio.open(path, 'w', driver='GTiff', height=values.shape[0], width=values.shape[1],
                       count=1, dtype='float32', crs='EPSG:32611',
                       transform=transform or from_origin(100, 100, 1, 1)) as out:
        out.write(values.astype('float32'), 1)


def test_overlap_includes_exactly_three_pixels_and_rejects_above_threshold(tmp_path):
    a = np.zeros((12, 12)); b = np.zeros_like(a)
    a[3, 6] = 1; a[10, 10] = 1; b[3, 3] = 1
    candidate, prior = tmp_path / 'a.tif', tmp_path / 'b.tif'
    write_tif(candidate, a); write_tif(prior, b)
    result = compare(candidate, prior)
    assert result['within_3_pixels'] == 1 and result['directed_overlap'] == 0.5
    assert not result['duplicate']
    a[10, 10] = 0; write_tif(candidate, a)
    assert compare(candidate, prior)['duplicate']


def test_invalid_grid_and_values_fail_closed(tmp_path):
    a = np.zeros((5, 5)); a[1, 1] = 1
    candidate, prior = tmp_path / 'a.tif', tmp_path / 'b.tif'
    write_tif(candidate, a); write_tif(prior, a, from_origin(0, 0, 1, 1))
    with pytest.raises(ValueError, match='grid mismatch'):
        compare(candidate, prior)
    write_tif(prior, a); a[0, 0] = np.nan; write_tif(candidate, a)
    with pytest.raises(ValueError, match='invalid values'):
        compare(candidate, prior)


@pytest.mark.parametrize('script', ['build_submission.py'])
def test_legacy_release_tools_stop_before_side_effects(script):
    card = ROOT / 'evidence/run_card.json'
    old = card.read_bytes()
    result = subprocess.run([sys.executable, str(ROOT / 'scripts' / script)], capture_output=True, text=True)
    assert result.returncode != 0 and 'BLOCKED' in result.stderr
    assert card.read_bytes() == old


def test_current_pages_revoke_promotion():
    assert 'DO NOT SUBMIT' in (ROOT / 'index.html').read_text()
    for page in (ROOT / 'swgb').glob('*.html'):
        assert 'Do not submit' in page.read_text()
        assert 'downloads/' not in page.read_text()
    result = json.loads((ROOT / 'evidence/swgb_lattice_audit.json').read_text())
    assert result['duplicate'] and result['within_3_pixels'] / result['candidate_dots'] > .70


def test_generated_pages_and_download_index_do_not_revive_swgb_approval():
    """A revoked candidate must never be called a selector-cleared submission."""
    pages = [ROOT / 'docs/index.html', ROOT / 'docs/executive-summary.html', ROOT / 'docs/how-to-submit.html']
    pages += sorted((ROOT / 'docs/sites').glob('GEMSDOE*.html'))
    for page in pages:
        text = page.read_text()
        assert 'No SWGB, H-PBSC or BGAC-1 file is approved for submission.' in text
        assert 'selector-cleared file' not in text
        assert 'red / green banners' not in text
    download_index = (ROOT / 'docs/downloads/README.md').read_text()
    assert 'OK TO SUBMIT' not in download_index
    # SWGB/PBSC must stay revoked in the download index.
    assert 'withdrawn' in download_index and 'ok_to_submit = false' in download_index
    # Any approval in the download index must match the thermal run card exactly.
    card = json.loads((ROOT / 'evidence/thermal/run_card.json').read_text())
    if card['ok_to_download_and_submit']:
        assert 'OK TO DOWNLOAD AND SUBMIT' in download_index
        assert card['raster_name'] in download_index
    else:
        assert 'OK TO DOWNLOAD AND SUBMIT' not in download_index


def test_generated_verdict_matches_run_card_gates():
    """The verdict shown on every generated page must equal the machine gate table.

    2026-10-31: both releases are checked — the standing H-TVGB release (OK) and, when
    present, the H-REGAVOID release (negative under AMEND-2). Every verdict phrase must
    appear on the rendered pages."""
    pairs = []
    thermal_release = json.loads((ROOT / 'evidence/thermal/release.json').read_text())
    pairs.append((thermal_release['card'], thermal_release))
    reg_path = ROOT / 'evidence/regavoid/release.json'
    if reg_path.exists():
        reg_release = json.loads(reg_path.read_text())
        pairs.append((reg_release['card'], reg_release))
    pages_text = {p: p.read_text()
                  for p in (ROOT / 'docs/index.html', ROOT / 'docs/executive-summary.html')}
    for card, release in pairs:
        assert card['ok_to_download_and_submit'] == all(p for _, p in release['gates'])
        verdict_word = ('OK TO DOWNLOAD AND SUBMIT' if card['ok_to_download_and_submit']
                        else 'NOT OK TO SUBMIT')
        for page, text in pages_text.items():
            assert verdict_word in text, f'{verdict_word} missing from {page}'
            assert 'HOLDOUT-DTI' in text  # every new number stays labelled
        assert card['submission_slots_used'] == 0
        assert len(card['note']) <= 140 and len(card['submission_name']) <= 140
    card, release = pairs[0]
    assert card['submission_slots_used'] == 0
    assert len(card['note']) <= 140 and len(card['submission_name']) <= 140
    # validator invariants the portal enforces
    v = release['validator']
    assert v['all_checks_passed']
    assert v['checks']['values_in_0_1_everywhere'] and v['checks']['no_nan_anywhere']
    assert v['checks']['crs_matches_template'] and v['checks']['shape_matches_template']
    assert v['checks']['transform_matches_template']
