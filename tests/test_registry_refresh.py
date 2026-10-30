"""Guards for the additive registry refresh (2026-10-30).

The frozen manifest is evidence: its bytes are pinned here so an accidental rewrite fails CI.
The refresh tool must never overwrite an existing manifest. The refreshed-audit receipt must stay
internally consistent with the literal rules (cleared requires complete comparison and no duplicate).
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FROZEN_SHA256 = '0e52bd80bc93ab9610c35d5f47818da4f86dfdd340689ad6b7522c25bfe74e09'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_frozen_registry_manifest_bytes_are_pinned():
    assert sha256(ROOT / 'registry/focus_inventory.json') == FROZEN_SHA256


def test_refresh_refuses_to_overwrite_existing_manifest():
    # The refusal happens before any network call, so this runs offline.
    result = subprocess.run(
        [sys.executable, 'scripts/registry_refresh.py', '--out', 'registry/focus_inventory.json',
         '--cache-dir', '.cache/unused-by-refusal-test'],
        cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode != 0
    assert 'refusing to overwrite' in (result.stderr + result.stdout)
    assert sha256(ROOT / 'registry/focus_inventory.json') == FROZEN_SHA256


def test_refreshed_manifest_is_complete_and_additive():
    path = ROOT / 'registry/focus_inventory_20261030_api.json'
    if not path.exists():
        pytest.skip('refreshed manifest not present in this checkout')
    refreshed = json.loads(path.read_text())
    frozen = json.loads((ROOT / 'registry/focus_inventory.json').read_text())
    assert refreshed['complete_within_scope'] is True and refreshed['failed'] == 0
    assert len(refreshed['rasters']) == 489
    assert set(refreshed['refs']) == set(frozen['refs'])
    # additive: every frozen (repo, blob) is still present in the refreshed snapshot
    frozen_keys = {(r['repo'], r['blob_sha1']) for r in frozen['rasters']}
    refreshed_keys = {(r['repo'], r['blob_sha1']) for r in refreshed['rasters']}
    assert frozen_keys <= refreshed_keys


def test_refreshed_audit_receipt_is_fail_closed():
    path = ROOT / 'evidence/registry_refresh_20261030.json'
    if not path.exists():
        pytest.skip('refreshed audit receipt not present in this checkout')
    receipt = json.loads(path.read_text(), parse_constant=lambda c: pytest.fail(f'non-strict JSON constant {c}'))
    assert receipt['verdict'] == 'no candidate cleared'
    control = receipt['positive_control']
    assert control['self_match_directed_overlap_within_3px'] >= 0.999
    assert control['self_match_spearman'] >= 0.999
    for label, row in receipt['candidates'].items():
        # Literal rule: a duplicate can never be cleared, and clearance needs complete comparison.
        assert row['duplicate'] is True, label
        assert row['cleared'] is False, label
        assert row['max_directed_overlap_within_3px'] > 0.70, label


def test_unassessable_registry_file_blocks_clearance(tmp_path):
    """Synthetic check of the fail-closed rule: one registry file that is non-finite inside the
    footprint makes the audit non-comparison-complete, so even a dissimilar candidate is not cleared."""
    import hashlib
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin
    sys.path.insert(0, str(ROOT))
    from scripts.novelty import audit

    shape = (30, 30)
    transform = from_origin(0, 3000, 100, 100)
    footprint = np.ones(shape, dtype=bool)

    def write(name, values):
        path = tmp_path / name
        with rasterio.open(path, 'w', driver='GTiff', height=shape[0], width=shape[1], count=1,
                           dtype='float32', crs='EPSG:32611', transform=transform) as out:
            out.write(values.astype('float32'), 1)
        return path

    rng = np.random.default_rng(7)
    candidate = (rng.random(shape) > 0.9).astype('float32')
    bad = np.zeros(shape, dtype='float32'); bad[0, 0] = np.nan
    bad_path = write('bad.tif', bad)
    rows = []
    for name, path in [('bad.tif', bad_path)]:
        rows.append(dict(repo='SYN', ref='x', path=name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         local=str(path), bytes=path.stat().st_size, blob_sha1='0'))
    inventory = dict(complete_within_scope=True, failed=0, scope='synthetic', rasters=rows)
    reference = write('reference.tif', np.zeros(shape))
    receipt = audit(candidate, footprint, inventory, tmp_path, reference, stage='dots', stop_on_duplicate=False)
    assert receipt['unassessable'] == 1
    assert receipt['comparisons_complete'] is False
    assert receipt['cleared'] is False
