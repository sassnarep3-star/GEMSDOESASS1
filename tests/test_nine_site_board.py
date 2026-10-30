"""Tests for the nine-site board, the literal lattice-gate bound and the format validator.

Synthetic-array tests always run. Evidence-consistency tests read the committed JSON only,
so they run in CI without restoring the 345 MB registry.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

from scipy.spatial import cKDTree  # noqa: E402
from vendor.gems57.uniqueness import dot_overlap  # noqa: E402
import nine_site_board as board  # noqa: E402
import validate_format as vf  # noqa: E402


def test_kdtree_rule_equals_shared_dot_overlap():
    rng = np.random.default_rng(0)
    a = rng.random((60, 70)) < 0.03
    b = rng.random((60, 70)) < 0.05
    shared = dot_overlap(a, b)
    kd = board.forward_overlap(np.argwhere(a), cKDTree(np.argwhere(b)))
    assert kd == pytest.approx(shared, abs=1e-12)


def test_halo_boundary_is_inclusive_at_three_pixels():
    reg = np.zeros((20, 20), bool)
    reg[10, 10] = True
    cand = np.zeros((20, 20), bool)
    cand[10, 13] = True  # exactly 3 px away: inside the literal 3 px halo
    cand[10, 14] = True  # 4 px away: outside
    assert board.forward_overlap(np.argwhere(cand), cKDTree(np.argwhere(reg))) == pytest.approx(0.5)


def test_literal_rule_bound_is_uncovered_over_thirty_percent():
    assert board.max_dots_satisfying_rule(6649) == 22163
    assert board.max_dots_satisfying_rule(0) == 0


def test_validator_rejects_out_of_range_and_wrong_dtype(tmp_path):
    with rasterio.open(ROOT / 'data/bridge/sample_submission.tif') as s:
        profile = s.profile.copy()
        footprint = np.isfinite(s.read(1))
    good = np.where(footprint, 0.5, 0.0).astype(np.float32)
    bad_value = good.copy()
    bad_value[np.argwhere(footprint)[0][0], np.argwhere(footprint)[0][1]] = 1.5
    bad_dtype = good.astype(np.float64)
    profile.update(dtype='float32', nodata=None, compress='lzw')
    p_good, p_bad, p_dtype = tmp_path / 'g.tif', tmp_path / 'v.tif', tmp_path / 'd.tif'
    for path, arr, prof in [(p_good, good, profile), (p_bad, bad_value, profile),
                            (p_dtype, bad_dtype, dict(profile, dtype='float64'))]:
        with rasterio.open(path, 'w', **prof) as dst:
            dst.write(arr, 1)
    with rasterio.open(ROOT / 'data/bridge/sample_submission.tif') as s:
        grid = (s.shape, s.crs, s.transform)
    assert vf.check(p_good, footprint, grid)['pass_format_check'] is True
    assert vf.check(p_bad, footprint, grid)['pass_format_check'] is False
    assert vf.check(p_dtype, footprint, grid)['pass_format_check'] is False


def test_board_evidence_is_internally_consistent():
    path = ROOT / 'evidence/nine_site_board.json'
    if not path.exists():
        pytest.skip('board evidence not generated')
    d = json.loads(path.read_text(), parse_constant=lambda v: pytest.fail('non-standard JSON ' + v))
    assert len(d['nine_site_best']) == 9
    assert d['nine_site_pairs_total'] == 72
    # every nine-site pair is over the literal limit: none is clear of any other
    assert d['nine_site_pairs_over_limit'] == 72
    bound = d['lattice_gate_bound']
    assert bound['max_dots_satisfying_literal_70pct_rule'] == int(bound['uncovered_footprint_cells'] / 0.30)
    assert all(not v['feasible_under_literal_rule'] for v in bound['per_site_feasibility'].values())
    assert d['lattice']['null_random_same_count_overlap']['mean'] > 0.99
    for site, v in d['nine_site_best'].items():
        assert v['values_in_01'] is True
        assert v['nan_inside_footprint'] == 0
        assert v['dots_outside_footprint'] == 0
        assert v['dots_on_catalogue'] == 0
        assert v['score_label'].startswith('OWNER-REPORT')


def test_format_evidence_all_nine_pass_official_text():
    path = ROOT / 'evidence/format_validation_nine_best.json'
    if not path.exists():
        pytest.skip('format evidence not generated')
    r = json.loads(path.read_text())
    best = [x for x in r['results'] if x['file'].startswith('.cache/')]
    assert len(best) == 9 and all(x['pass_format_check'] for x in best)
