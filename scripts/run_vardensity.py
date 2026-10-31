#!/usr/bin/env python3
"""E3b — variable-density emission under the certified marginal rule.

The champion thins its field to a *uniform* 2.8 px Poisson-disk set.  The
certified algebra (scripts/certify_metric.py) says the optimal emission is not a
uniform lattice but the acceptance set

    dT > alpha * DTI * (dT + dFP)

which, for a posterior ``p``, is a *variable-density* set: dense where the
posterior is high (a dot on a true fault costs FP = 0, so densifying there is
almost free) and sparse where it is low.  This is the one emission question E1
could not answer (its dense variants were invalid — see AMEND-E1-01).

Posteriors compared, all on the SAME support (the champion's H19-5 field) so the
only difference is the emission:

  P-uniform     p constant on the support, sum(p) = K_est          (emission-only test)
  P-geo         p on the support proportional to the smoothed multi-instrument
                across-strike step field, sum(p) = K_est           (new field test)

``allocate_by_marginal_bar`` from the pinned template does the allocation.
"""
from __future__ import annotations

import argparse
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
from vendor.gems57.emit import allocate_by_marginal_bar  # noqa: E402

WORK = ROOT / "work"
DATA = ROOT / "data"
K_EST = 14_086       # hidden-truth pixels, calibrated in knowledge/hypotheses_20261031_recalldom.md s.5


def load_base():
    with rasterio.open(DATA / "official/sample_submission.tif") as s:
        footprint = np.isfinite(s.read(1))
    with rasterio.open(DATA / "official/existing_faults.tif") as s:
        catalogue = (s.read(1) == 1) & footprint
    return footprint, catalogue


def score(label, preds, folds, extra=None):
    pooled = score_pooled(preds, folds, n_boot=300)
    far = score_pooled_farfield(preds, folds, n_boot=100)
    row = dict(label=label, emitted=int(np.mean([int(p.sum()) for p in preds])),
               evaluator=pooled["evaluator"], holdout_dti=pooled["holdout_dti"], ci95=pooled["ci95"],
               n_withheld_positives=pooled["n_withheld_positives"], tp=pooled["tp"], fp=pooled["fp"],
               fn=pooled["fn"],
               coverage=pooled["tp"] / (pooled["tp"] + pooled["fn"]) if pooled["tp"] + pooled["fn"] else 0.0,
               farfield_gt5px_dti=far["holdout_dti"], evidence_class="HOLDOUT-DTI")
    if extra:
        row.update(extra)
    print(f"[e3b] {label:<46} n={row['emitted']:>7} HOLDOUT-DTI {row['holdout_dti']:.4f} "
          f"[{row['ci95'][0]:.4f},{row['ci95'][1]:.4f}] cov={row['coverage']:.3f} "
          f"far>5px {row['farfield_gt5px_dti']:.4f}", flush=True)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="evidence/offset_step_v2/e3b_vardensity.json")
    ap.add_argument("--k-truth", type=float, default=K_EST)
    a = ap.parse_args()
    t0 = time.monotonic()
    footprint, catalogue = load_base()
    folds, _ = build_folds(catalogue, footprint)

    with rasterio.open(DATA / "inputs/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif") as s:
        h19 = s.read(1)
    sup = np.isfinite(h19) & (h19 > 0) & footprint
    dcat = ndi.distance_transform_edt(~catalogue)

    p_uniform = np.where(sup, 1.0, 0.0).astype(np.float32)
    p_uniform *= a.k_truth / p_uniform.sum()

    geo = np.load(WORK / "osv2_geo.npy")            # rank-normalised smoothed geophysical step, [0,1]
    w = np.where(sup, 0.15 + 0.85 * geo, 0.0).astype(np.float32)
    p_geo = w * (a.k_truth / w.sum())

    rows = []
    for tag, p in (("P-uniform", p_uniform), ("P-geo", p_geo)):
        # fold-aware visible-catalogue prune: the live prune is against the whole
        # catalogue, the holdout analogue prunes only the fold's VISIBLE faults
        for prune in (2,):
            for fold_aware in (True,):
                for cap in (20_000, 40_000, 80_000, 200_000):
                    preds = []
                    for f in folds:
                        vis = f.visible if fold_aware else catalogue
                        allowed = footprint & sup & (ndi.distance_transform_edt(~vis) > prune)
                        al = allocate_by_marginal_bar(p, allowed, a.k_truth, max_dots=cap,
                                                      candidate_cap=600_000, floor=0.0)
                        preds.append(al.emitted)
                    rows.append(score(f"{tag} marginal-bar cap{cap} prune{prune}", preds, folds,
                                      dict(role="candidate", posterior=tag, k_truth=a.k_truth,
                                           max_dots=cap)))
                    del preds

    # control, same support and same fold-aware prune
    preds = [poisson_disk_dots(sup.astype(np.float32),
                               footprint & sup & (ndi.distance_transform_edt(~f.visible) > 2),
                               44_090, 2.8) for f in folds]
    rows.append(score("CONTROL champion H19-5 md2.8 prune2", preds, folds,
                      dict(role="control", support_px=int(sup.sum()), spacing=2.8)))

    out = dict(evidence_class="HOLDOUT-DTI",
               generated_utc=datetime.now(timezone.utc).isoformat(),
               hypothesis="variable-density emission under the certified marginal rule",
               k_truth_used=a.k_truth,
               rows=rows, elapsed_seconds=round(time.monotonic() - t0, 1))
    p = ROOT / a.out
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(f"[e3b] wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
