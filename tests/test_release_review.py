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
