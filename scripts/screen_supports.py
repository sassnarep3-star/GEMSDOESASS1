#!/usr/bin/env python3
"""Screen every locally available independent support field on the shared holdout.

Purpose: choose the support for the deliverable raster on measured evidence, not
on narrative.  Every candidate is emitted with the SAME certified geometry
(2.8 px Poisson-disk dots, fold-aware 2 px visible-catalogue prune, 44,090 dot
cap) so that only the support differs.  The champion's H19-5 support is the
control.  All numbers are HOLDOUT-DTI with a 50x50-px block-bootstrap 95% CI.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.gems.emission import poisson_disk_dots  # noqa: E402
from src.gems.holdout import build_folds, score_pooled, score_pooled_farfield  # noqa: E402

DATA = ROOT / "data"
N_SUP = 121_131          # the champion's support size; every candidate is matched to it
N_DOTS = 44_090
SPACING = 2.8
PRUNE = 2


def load_base():
    with rasterio.open(DATA / "official/sample_submission.tif") as s:
        footprint = np.isfinite(s.read(1))
    with rasterio.open(DATA / "official/existing_faults.tif") as s:
        catalogue = (s.read(1) == 1) & footprint
    return footprint, catalogue


def top_k(arr, footprint, n):
    v = np.where(footprint, arr, -np.inf)
    flat = np.argpartition(-v.ravel(), n - 1)[:n]
    out = np.zeros(arr.size, bool)
    out[flat] = True
    return out.reshape(arr.shape) & footprint


def candidates(footprint):
    out = {}
    with rasterio.open(DATA / "inputs/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif") as s:
        h = s.read(1)
    out["H19-5 (champion control)"] = np.isfinite(h) & (h > 0) & footprint          # already a mask
    for name, path in (("H19-4", DATA / "inputs/gems19-h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan.tif"),
                       ("H16-1", DATA / "inputs/gems16-h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan.tif")):
        with rasterio.open(path) as s:
            a = s.read(1)
        v = np.where(np.isfinite(a), a, 0.0)
        out[name] = top_k(v, footprint, N_SUP)
    with rasterio.open(DATA / "external/lidar_scarp_features_u8.tif") as s:
        arr = s.read()
        names = list(s.descriptions)
    for i, nm in enumerate(names):
        out[f"lidar_scarp:{nm}"] = top_k(arr[i].astype(np.float32), footprint, N_SUP)
    out["lidar_scarp:MAX"] = top_k(arr.astype(np.float32).max(axis=0), footprint, N_SUP)
    with rasterio.open(DATA / "external/derived_sgmc_faults_100m_u8.tif") as s:
        sgmc = s.read(1)
    out["sgmc_offcatalogue (raw mask)"] = (sgmc > 0) & footprint
    return out


def main() -> int:
    t0 = time.monotonic()
    footprint, catalogue = load_base()
    folds, _ = build_folds(catalogue, footprint)
    rows = []
    for label, sup in candidates(footprint).items():
        n_sup = int(sup.sum())
        preds = [poisson_disk_dots(sup.astype(np.float32),
                                   footprint & sup & (ndi.distance_transform_edt(~f.visible) > PRUNE),
                                   N_DOTS, SPACING) for f in folds]
        pooled = score_pooled(preds, folds, n_boot=300)
        far = score_pooled_farfield(preds, folds, n_boot=100)
        row = dict(label=label, support_px=n_sup, emitted=int(np.mean([int(p.sum()) for p in preds])),
                   evaluator=pooled["evaluator"], holdout_dti=pooled["holdout_dti"], ci95=pooled["ci95"],
                   n_withheld_positives=pooled["n_withheld_positives"], tp=pooled["tp"], fp=pooled["fp"],
                   fn=pooled["fn"],
                   coverage=pooled["tp"] / (pooled["tp"] + pooled["fn"]) if pooled["tp"] + pooled["fn"] else 0.0,
                   farfield_gt5px_dti=far["holdout_dti"], evidence_class="HOLDOUT-DTI")
        rows.append(row)
        print(f"[screen] {label:<38} sup={n_sup:>7} n={row['emitted']:>6} HOLDOUT-DTI "
              f"{row['holdout_dti']:.4f} [{row['ci95'][0]:.4f},{row['ci95'][1]:.4f}] "
              f"cov={row['coverage']:.3f} far>5px {row['farfield_gt5px_dti']:.4f}", flush=True)
        del preds
    rows.sort(key=lambda r: -r["holdout_dti"])
    out = dict(evidence_class="HOLDOUT-DTI", generated_utc=datetime.now(timezone.utc).isoformat(),
               purpose="support screening at fixed certified emission geometry",
               geometry=dict(spacing_px=SPACING, dots_cap=N_DOTS, catalogue_prune_px=PRUNE,
                             support_matched_to_px=N_SUP),
               rows=rows, elapsed_seconds=round(time.monotonic() - t0, 1))
    p = ROOT / "evidence/offset_step_v2/support_screen.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(f"[screen] wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
