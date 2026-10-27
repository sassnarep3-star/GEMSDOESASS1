import json
import math
from pathlib import Path
import sys

import numpy as np
import pytest
import rasterio
from affine import Affine
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_witnesses import binary_spearman, coverage, inspect_raster, overlap, placement_bound  # noqa: E402
from fetch_witnesses import check_entry, fetch  # noqa: E402


def test_lattice_bound_strict_boundary_and_invalid_counts():
    # 3 uncovered cells: at exactly 7/10 it is not a strict >70% duplicate.
    same = placement_bound(20, 17, 10)
    assert same['minimum_overlapping_dots'] == 7
    assert same['guaranteed_duplicate'] is False
    assert same['first_forced_dot_count'] == 11
    assert placement_bound(20, 17, 11)['guaranteed_duplicate'] is True
    assert placement_bound(20, 17, 1)['minimum_overlapping_dots'] == 0
    assert placement_bound(20, 17, 1)['interpretation'].startswith('A non-forced')
    for values in ((0, 0, 1), (20, 21, 1), (20, 17, 0), (20, 17, 21), (20, 17, True)):
        with pytest.raises(ValueError):
            placement_bound(*values)


def test_euclidean_halo_and_empty_ref():
    dots = np.zeros((9, 9), bool)
    dots[4, 4] = True
    halo = coverage(dots)
    assert halo[4, 7] and halo[6, 6]
    assert not halo[7, 7] and not halo[4, 8]
    assert not coverage(np.zeros_like(dots)).any()
    with pytest.raises(ValueError):
        coverage(dots, float('nan'))


def test_overlap_threshold_and_empty_candidate():
    dots = np.ones((1, 10), bool)
    halo = np.zeros((1, 10), bool)
    halo[0, :7] = True
    assert overlap(dots, halo)['duplicate'] is False
    halo[0, 7] = True
    assert overlap(dots, halo)['duplicate'] is True
    assert overlap(np.zeros_like(dots), halo)['fraction'] is None
    assert overlap(np.zeros_like(dots), halo)['duplicate'] is None
    with pytest.raises(ValueError):
        overlap(dots, np.zeros((2, 2), bool))


def test_binary_spearman_matches_tie_aware_reference():
    rng = np.random.default_rng(904)
    a = rng.random((10, 12)) < .20
    b = rng.random((10, 12)) < .25
    fp = rng.random((10, 12)) < .80
    actual = binary_spearman(a, b, fp)
    expected = spearmanr(a[fp], b[fp]).statistic
    assert actual == pytest.approx(expected)
    assert binary_spearman(np.zeros_like(a), b, fp) is None
    with pytest.raises(ValueError):
        binary_spearman(a, b[:, :-1], fp)


def write_tif(path, values, *, transform=None, crs='EPSG:32611', dtype='float32', count=1):
    transform = transform or Affine(100, 0, 0, 0, -100, 400)
    with rasterio.open(path, 'w', driver='GTiff', height=values.shape[0], width=values.shape[1],
                       count=count, dtype=dtype, crs=crs, transform=transform) as ds:
        ds.write(values.astype(dtype), 1)
        if count > 1:
            ds.write(values.astype(dtype), 2)


def test_saved_file_validation_catches_grid_range_nan_and_outside(tmp_path):
    from rasterio.crs import CRS
    fp = np.array([[True, True], [True, False]])
    transform = Affine(100, 0, 0, 0, -100, 400)
    grid = (CRS.from_epsg(32611), transform, (2, 2))
    p = tmp_path / 'candidate.tif'
    write_tif(p, np.array([[0, 1], [0, 0]]))
    report, mask = inspect_raster(p, grid, fp)
    assert report['no_nan_or_inf_inside'] and report['in_footprint_range_0_1']
    assert report['whole_array_range_0_1'] and report['outside_all_zero']
    assert report['positive_pixels'] == 1 and mask.sum() == 1
    for values in (np.array([[0, np.nan], [0, 0]]),
                   np.array([[0, 1.1], [0, 0]]),
                   np.array([[0, -0.1], [0, 0]]),
                   np.array([[0, 0], [0, 1]])):
        write_tif(p, values)
        with pytest.raises(ValueError):
            inspect_raster(p, grid, fp)
    write_tif(p, np.zeros((2, 2)), transform=Affine(100, 0, 1, 0, -100, 400))
    with pytest.raises(ValueError, match='CRS, shape or transform'):
        inspect_raster(p, grid, fp)
    write_tif(p, np.zeros((2, 2)), dtype='uint8')
    with pytest.raises(ValueError, match='malformed'):
        inspect_raster(p, grid, fp)
    write_tif(p, np.zeros((2, 2)), count=2)
    with pytest.raises(ValueError, match='exactly one band'):
        inspect_raster(p, grid, fp)


def test_fetch_rejects_bad_pins_and_hash_mismatch(tmp_path, monkeypatch):
    import hashlib
    good = {'id':'x', 'repo':'owner/repo', 'ref':'a'*40, 'path':'docs/a.tif',
            'local_name':'x.tif', 'sha256':hashlib.sha256(b'hello').hexdigest()}
    for bad in ({**good, 'ref':'main'}, {**good, 'local_name':'../out'},
                {**good, 'path':'../file'}, {**good, 'sha256':'oops'}):
        with pytest.raises(ValueError):
            check_entry(bad)
    def fake_run(_command, *, stdout, check, timeout):
        stdout.write(b'wrong data')
    monkeypatch.setattr('fetch_witnesses.subprocess.run', fake_run)
    with pytest.raises(ValueError, match='SHA-256 mismatch'):
        fetch(good, tmp_path)
    assert list(tmp_path.iterdir()) == []
    (tmp_path / 'x.tif').write_bytes(b'hello')
    assert fetch(good, tmp_path) == 'cached and verified'
    (tmp_path / 'x.tif').write_bytes(b'changed')
    with pytest.raises(ValueError, match='Existing file fails'):
        fetch(good, tmp_path)


def test_committed_evidence_is_negative_and_complete():
    root = Path(__file__).resolve().parents[1]
    x = json.loads((root / 'evidence/witness-audit.json').read_text())
    assert x['submission_ready'] is False and x['experiment_count'] == 0
    assert x['historical_nine_pairwise']['all_72_fail_overlap']
    assert len(x['historical_nine_pairwise']['comparisons']) == 72
    assert x['kpl36']['overlap_with_lattice']['duplicate']
    assert x['literal_budget_bound']['guaranteed_duplicate']
    assert x['sample']['ones_equal_label_mirror']
    assert x['lattice']['registered_id'] == 'reg-052'
    assert x['lattice']['footprint_sha256'] == '15bc7e7d4e21d284c42e4183bb7c63d087f67635818bd7b963d58f6beed44817'
    assert x['registry_snapshot']['entry_count'] == 198
    assert x['forensics']['25_and_30_identical_in_footprint']
    assert x['forensics']['32_vs_25_minus_visible_catalogue_2px_xor_pixels'] == 0
    assert math.isclose(x['historical_nine_pairwise']['minimum_directional_fraction'], 0.8671895382207149)


def test_registered_witness_is_bound_to_bytes_and_footprint():
    import hashlib
    from audit_witnesses import validate_registered_witness
    pixels = np.array([[0, 1], [1, 0]], dtype='float32')
    fp = np.array([[True, True], [False, True]])
    content = hashlib.sha256(np.asarray(pixels[fp], dtype='<f4').tobytes()).hexdigest()
    entry = {'id': 'reg-052', 'file_sha256': 'a'*64, 'footprint_sha256': content}
    registry = {'n_entries': 1, 'entries': [entry]}
    found, observed = validate_registered_witness(registry, 'a'*64, pixels, fp)
    assert found == entry and observed == content
    with pytest.raises(ValueError, match='identity'):
        validate_registered_witness(registry, 'b'*64, pixels, fp)
    with pytest.raises(ValueError, match='footprint checksum'):
        validate_registered_witness(registry, 'a'*64, pixels, ~fp)
    with pytest.raises(ValueError, match='Malformed'):
        validate_registered_witness({'n_entries': 2, 'entries': [entry]}, 'a'*64, pixels, fp)
    with pytest.raises(ValueError, match='identity'):
        validate_registered_witness({'n_entries': 2, 'entries': [entry, entry]}, 'a'*64, pixels, fp)


def test_full_readback_reproduces_committed_evidence_when_witnesses_are_available():
    from audit_witnesses import run
    root = Path(__file__).resolve().parents[1]
    directory = root / '.local-data/audit'
    if not (directory / 'registry_snapshot.json').is_file():
        pytest.skip('Optional: run scripts/fetch_witnesses.py for full integration test')
    expected = json.loads((root / 'evidence/witness-audit.json').read_text())
    actual = run(directory)
    expected.pop('generated_utc')
    actual.pop('generated_utc')
    assert actual == expected
