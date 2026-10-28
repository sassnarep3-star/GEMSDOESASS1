"""H-PBSC session receipts — no re-run of the experiment."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
CARD = json.loads((ROOT / "evidence/pbsc/run_card.json").read_text())
TIF = ROOT / "docs/downloads" / CARD["submission_name"]
TMPL = ROOT / "data/bridge/sample_submission.tif"
CAT = ROOT / "data/bridge/existing_faults.tif"


def test_verdict_is_negative_and_not_ok_to_submit():
    assert CARD["verdict"] == "negative"
    assert CARD["ok_to_submit"] is False
    assert CARD["approved_for_submission"] is False
    assert CARD["holdout_dti"]["label"] == "HOLDOUT-DTI"
    assert CARD["holdout_dti"]["value"] < CARD["holdout_dti"]["bar_0p2600_family_base"]["holdout_dti"]
    assert CARD["note_length"] <= 140
    assert len(CARD["submission_note"]) <= 140
    assert CARD["organizer_confirmed"] is None


def test_uniqueness_under_protocol_thresholds():
    u = CARD["correlation_overlap_vs_registry"]
    assert u["max_spearman"] <= 0.90
    assert u["max_frac_dots_within_3px"] <= 0.70
    assert u["is_duplicate"] is False
    extra = u["extra_sibling_and_prior_swgb"]
    assert extra["is_duplicate"] is False
    assert extra["max_frac_dots_within_3px"] <= 0.70


def test_tif_matches_template_and_range():
    assert TIF.is_file()
    assert CARD["raster_sha256"]
    with rasterio.open(TIF) as s:
        a = s.read(1)
        assert s.count == 1
        assert s.dtypes[0] == "float32"
        assert str(s.crs) == "EPSG:32611"
        assert (s.height, s.width) == (3730, 3292)
        assert tuple(s.transform)[:6] == (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
        assert np.isfinite(a).all()
        assert float(a.min()) >= 0.0 and float(a.max()) <= 1.0
        assert CARD["validator_output"]["values_in_0_1_everywhere"] is True
        assert CARD["validator_output"]["no_nan_anywhere"] is True
        assert int((a > 0).sum()) == 37654
    if TMPL.is_file():
        with rasterio.open(TIF) as s, rasterio.open(TMPL) as t:
            a = s.read(1)
            foot = np.isfinite(t.read(1))
            assert float(a[~foot].max()) <= 0.0
    if CAT.is_file():
        with rasterio.open(CAT) as c, rasterio.open(TIF) as s:
            cat = c.read(1) == 1
            a = s.read(1)
        assert int((a[cat] > 0).sum()) == 0


def test_canary_not_flagged():
    can = json.loads((ROOT / "evidence/pbsc/leakage_canary.json").read_text())
    assert can["flagged_over_0p90"] == {}
    assert max(can["auc"].values()) <= 0.90


def test_homepage_makes_submit_decision_obvious():
    home = (ROOT / "index.html").read_text()
    assert "DO NOT SUBMIT" in home
    assert CARD["submission_name"] in home
    assert "OK TO DOWNLOAD AND SUBMIT" in home
    swgb = json.loads((ROOT / "evidence/swgb/run_card.json").read_text())
    assert swgb["submission_name"] in home
    assert "Predicted values must be in range [0, 1]" in home
