import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gems_audit.forensics import _positive_binary, binary_spearman, disk, duplicate_stop, forced_overlap


def test_disk_is_euclidean_and_includes_boundary():
    d = disk(3)
    assert d.shape == (7, 7)
    assert d[0, 3] and d[6, 3]  # exactly 3 px
    assert not d[0, 0]
    assert d[1, 1]  # sqrt(8)
    assert int(d.sum()) == 29
    with pytest.raises(ValueError):
        disk(-1)


def test_bound_strict_boundary_and_unproven_is_not_pass():
    at_boundary = forced_overlap(100, 97, 10)
    assert at_boundary["minimum_overlapping_dots"] == 7
    assert at_boundary["minimum_overlap_fraction"] == 0.7
    assert not at_boundary["proven_duplicate_stop"]
    assert at_boundary["first_count_forced_above_limit"] == 11
    assert forced_overlap(100, 97, 11)["proven_duplicate_stop"]
    assert not forced_overlap(100, 0, 50)["proven_duplicate_stop"]
    for bad in [(0, 0, 1), (10, 11, 1), (10, 9, 0), (10, 9, 11), (10, 9, True)]:
        with pytest.raises(ValueError):
            forced_overlap(*bad)


def test_exact_binary_spearman_with_ties_and_constant():
    foot = np.ones((3, 3), bool)
    a = np.zeros((3, 3), bool)
    a[1, 1] = True
    assert binary_spearman(a, a, foot) == pytest.approx(1)
    assert binary_spearman(a, ~a, foot) == pytest.approx(-1)
    assert binary_spearman(a, np.zeros_like(a), foot) is None
    foot[1, 1] = False
    assert binary_spearman(a, ~a, foot) is None


def test_duplicate_stop_uses_strict_positive_rank_threshold_and_fails_closed():
    assert not duplicate_stop(0.7, 0.9)
    assert not duplicate_stop(0.0, -1.0)
    assert duplicate_stop(0.700001, 0.1)
    assert duplicate_stop(0.1, 0.900001)
    assert duplicate_stop(0.0, None)
    assert duplicate_stop(0.0, float('nan'))
    assert duplicate_stop(float('nan'), 0.2)


def test_inf_outside_is_not_called_masked_or_nan(tmp_path):
    path = tmp_path / 'reference.tif'
    foot = np.array([[False, True], [True, True]])
    values = np.array([[np.inf, 0], [0, 1]], dtype='float32')
    with rasterio.open(path, 'w', driver='GTiff', height=2, width=2, count=1,
                       dtype='float32', crs='EPSG:32611', transform=from_origin(0, 200, 100, 100)) as ds:
        ds.write(values, 1)
    with rasterio.open(path) as ds:
        mask, info = _positive_binary(ds, foot)
    assert mask.sum() == 1
    assert not info['outside_masked_or_nan']
