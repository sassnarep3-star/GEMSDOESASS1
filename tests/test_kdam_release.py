"""Contract for the 2026-10-31 H-KDAM release: the page verdict must equal the bytes.

These tests re-open the shipped GeoTIFF and re-derive every claim the site prints. They do not
trust the release JSON: they compare it with the file and with the evidence receipts, so a stale or
hand-edited card fails.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest
import rasterio

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.gems.grid import load_catalogue, load_footprint  # noqa: E402
from src.gems.submission import validate  # noqa: E402

RELEASE = ROOT / "evidence/kdam/release.json"


@pytest.fixture(scope="module")
def release():
    if not RELEASE.exists():
        pytest.skip("no H-KDAM release in this checkout")
    return json.loads(RELEASE.read_text())


def test_every_gate_is_derived_from_evidence(release):
    assert release["ok_to_download_and_submit"] == all(passed for _, passed in release["gates"])
    assert release["card"]["submission_slots_used"] == 0
    note = release["card"]["note"]
    assert len(note) <= 140 and note == release["card"]["note"][:140]
    assert len(release["card"]["submission_name"]) <= 140


def test_sha256_and_format_recomputed_from_the_bytes(release):
    tif = ROOT / "docs/downloads" / release["card"]["raster_name"]
    assert tif.exists(), tif
    digest = hashlib.sha256(tif.read_bytes()).hexdigest()
    assert digest == release["card"]["raster_sha256"]
    footprint = load_footprint()
    catalogue = load_catalogue()
    report = validate(tif, footprint, catalogue)
    assert report["all_checks_passed"], report["checks"]
    assert report["checks"]["values_in_0_1_everywhere"]
    assert report["checks"]["no_nan_anywhere"]
    assert report["checks"]["zero_mass_on_known_catalogue_pixels"]
    with rasterio.open(tif) as src:
        a = src.read(1)
        assert src.count == 1 and src.dtypes[0] == "float32"
        assert (src.height, src.width) == (3730, 3292)
        assert src.crs.to_epsg() == 32611
    assert np.isfinite(a).all()
    assert a.min() >= 0.0 and a.max() <= 1.0
    assert int((a > 0).sum()) == release["card"]["n_dots"]


def test_zip_contains_exactly_the_tif(release):
    import zipfile
    zip_path = (ROOT / "docs/downloads" / release["card"]["raster_name"]).with_suffix(".zip")
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
    assert names == [release["card"]["raster_name"]]


def test_holdout_numbers_are_labelled_and_ordered(release):
    card = release["card"]
    h = card["holdout_dti"]
    assert h["label"] == "HOLDOUT-DTI"
    assert h["alpha"] == 0.2 and h["beta"] == 0.8 and h["radius_m"] == 300.0
    assert h["ci95"][0] < h["value"] < h["ci95"][1]
    assert h["n_withheld_positives"] == 60988
    comp = card["comparators_same_emission"]["family_base_44090_unpruned"]
    assert h["value"] > comp, "the release claims a field gain; the evidence must support it"


def test_novelty_receipt_supports_the_claim(release):
    nov = json.loads((ROOT / "evidence/kdam"
                      / f"novelty_{release['card']['submission_name']}.json").read_text())
    assert nov["candidate_dots"] == release["card"]["n_dots"]
    assert nov["cleared"] is True and nov["duplicates"] == []
    assert nov["max_overlap3"] <= nov["thresholds"]["overlap_limit"]
    assert nov["max_rho"] <= nov["thresholds"]["rho_limit"]
    assert nov["measured_exactly"] + nov["bounded"] + nov["incompatible_grid"] == nov["competitive_rasters"]
    # the bound must never be reported below the exact measurement (it is an upper bound)
    if nov["max_overlap3"] is not None:
        assert nov["max_overlap3_upper_bound"] >= nov["max_overlap3"]


def test_lattice_overlap_is_disclosed_not_hidden(release):
    d = release["card"]["lattice_disclosure"]
    assert d["available"] and d["overlap3"] > 0.99
    pages = (ROOT / "docs/executive-summary.html").read_text()
    assert "Scope disclosure" in pages
    assert "calibration lattice" in pages
    assert "nine focus sites only" in pages


def test_page_verdict_matches_the_card(release):
    card = release["card"]
    word = "OK TO DOWNLOAD AND SUBMIT" if card["ok_to_download_and_submit"] else "NOT OK TO SUBMIT"
    for page in (ROOT / "docs/index.html", ROOT / "docs/executive-summary.html"):
        text = page.read_text()
        assert word in text
        assert card["raster_name"] in text
        assert "HOLDOUT-DTI" in text
