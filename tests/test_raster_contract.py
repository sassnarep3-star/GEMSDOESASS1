from pathlib import Path
import json
import subprocess
import sys

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gems_audit.raster_contract import inspect_raster, sha256_file


@pytest.fixture
def grid(tmp_path):
    footprint = np.zeros((5, 6), bool)
    footprint[1:4, 1:5] = True
    template = np.where(footprint, 0, np.nan).astype("float32")
    profile = {"driver": "GTiff", "height": 5, "width": 6, "count": 1, "dtype": "float32",
               "crs": "EPSG:32611", "transform": from_origin(243350, 4508550, 100, 100)}
    path = tmp_path / "template.tif"
    with rasterio.open(path, "w", **profile, nodata=np.nan) as ds:
        ds.write(template, 1)
    return tmp_path, path, footprint, profile


def write_candidate(grid, *, data=None, mask=True, internal=True, **overrides):
    tmp_path, _, footprint, profile = grid
    path = tmp_path / "candidate.tif"
    profile = {**profile, **overrides}
    if data is None:
        data = np.zeros((profile["height"], profile["width"]), dtype=profile["dtype"])
        if data.shape == footprint.shape:
            data[2, 2] = 0.75
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=internal):
        with rasterio.open(path, "w", **profile) as ds:
            for band in range(1, profile["count"] + 1):
                ds.write(data, band)
            if mask and data.shape == footprint.shape:
                ds.write_mask(footprint.astype("uint8") * 255)
    return path


def inspect_synthetic(candidate, template):
    return inspect_raster(candidate, template, expected_shape=(5, 6),
                          expected_transform=from_origin(243350, 4508550, 100, 100))


def test_self_contained_masked_outside_and_raw_finite(grid):
    candidate = write_candidate(grid)
    receipt = inspect_synthetic(candidate, grid[1])
    assert receipt["local_format_pass"]
    assert all(receipt["checks"].values())
    assert receipt["sha256"] == sha256_file(candidate)
    assert not receipt["organizer_acceptance_confirmed"]
    assert not Path(str(candidate) + ".msk").exists()


@pytest.mark.parametrize("bad", [-0.01, 1.01, float("nan"), float("inf"), -3.4e38])
def test_inside_rejected_without_clipping(grid, bad):
    arr = np.zeros((5, 6), dtype="float32")
    arr[2, 2] = bad
    candidate = write_candidate(grid, data=arr)
    result = inspect_synthetic(candidate, grid[1])
    assert not result["local_format_pass"]
    assert not result["checks"]["values_in_0_1_inside_footprint"]


def test_outside_null_and_raw_range_are_separate_checks(grid):
    candidate = write_candidate(grid, mask=False)
    result = inspect_synthetic(candidate, grid[1])
    assert result["checks"]["all_raw_values_in_0_1"]
    assert not result["checks"]["outside_is_null_mask_or_nan"]
    assert not result["local_format_pass"]

    arr = np.zeros((5, 6), dtype="float32")
    arr[0, 0] = np.nan
    candidate = write_candidate(grid, data=arr)
    result = inspect_synthetic(candidate, grid[1])
    assert result["checks"]["outside_is_null_mask_or_nan"]
    assert not result["checks"]["all_raw_values_in_0_1"]
    assert not result["local_format_pass"]


def test_cli_writes_negative_receipt_on_missing_input(tmp_path):
    script = Path(__file__).resolve().parents[1] / 'scripts' / 'validate_tif.py'
    out = tmp_path / 'report.json'
    proc = subprocess.run([sys.executable, str(script), str(tmp_path / 'missing.tif'),
                           str(tmp_path / 'missing-template.tif'), '--out', str(out)],
                          capture_output=True, text=True)
    assert proc.returncode == 1
    assert json.loads(proc.stdout) == json.loads(out.read_text())
    assert json.loads(out.read_text())['local_format_pass'] is False


def test_external_mask_sidecar_is_not_single_file(grid):
    candidate = write_candidate(grid, internal=False)
    assert Path(str(candidate) + ".msk").exists()
    result = inspect_synthetic(candidate, grid[1])
    assert result["checks"]["outside_is_null_mask_or_nan"]
    assert not result["checks"]["self_contained"]
    assert not result["local_format_pass"]


@pytest.mark.parametrize("overrides,failed", [
    ({"count": 2}, "single_band"),
    ({"dtype": "float64"}, "float32"),
    ({"crs": "EPSG:4326"}, "crs_matches_template"),
    ({"transform": from_origin(243351, 4508550, 100, 100)}, "transform_matches_template"),
    ({"height": 4}, "shape_matches_template"),
])
def test_wrong_contract_fails(grid, overrides, failed):
    candidate = write_candidate(grid, **overrides)
    result = inspect_synthetic(candidate, grid[1])
    assert not result["checks"][failed]
    assert not result["local_format_pass"]


def test_arbitrary_template_is_not_silently_accepted_as_official_grid(grid):
    candidate = write_candidate(grid)
    result = inspect_raster(candidate, grid[1])
    assert not result["checks"]["template_expected_shape"]
    assert not result["local_format_pass"]


def test_wrong_template_dtype_fails_even_if_candidate_matches(grid):
    _, _, footprint, profile = grid
    template = grid[0] / "wrong-template.tif"
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
        with rasterio.open(template, "w", **{**profile, "dtype": "uint8"}) as ds:
            ds.write(np.zeros(footprint.shape, dtype="uint8"), 1)
            ds.write_mask(footprint.astype("uint8") * 255)
    result = inspect_synthetic(write_candidate(grid), template)
    assert not result["checks"]["template_float32"]
    assert not result["local_format_pass"]
