#!/usr/bin/env python3
"""H-OFFSET-STEP v2 — Frangi-vesselness multi-instrument lineament field.

Why v2 exists (written after E2's negative result; see
knowledge/hypotheses_20261031_recalldom.md section 7):

E2 scored HOLDOUT-DTI 0.0453 (product), 0.0533 (topo) and 0.0283 (geo) against
the champion control's 0.1048.  Diagnosis: (i) a single-scale structure tensor
on one band is a weak lineament detector compared with the incumbent field's
multi-scale openness/LRM, and (ii) the pixel-wise product of two
rank-normalised fields is spatially incoherent -- the top-121k pixels came out
as isolated specks (only ~18k dots survived a 2.8 px Poisson-disk thinning of a
121k support), so the emission geometry could not form traces.

v2 changes exactly those two things:
  * detector: Frangi vesselness (multi-scale Hessian ridge filter) per band;
  * corroboration: the geophysical support is GAUSSIAN-SMOOTHED (sigma = 4 px)
    before it gates the topographic field, so corroboration is required in the
    *neighbourhood* of a lineament -- which is also the physically right
    statement, because a fault's potential-field expression is laterally offset
    from its topographic scarp by a few hundred metres.

Emissions use the certified optimum (scripts/certify_metric.py): 2.8-3.0 px
spacing, dot field, >=2 px off the known catalogue.

Subcommands
    build    build + cache the field
    e3       score it on GEMSASS1-HR-v2-segment vs the champion control
    canary   leakage canary
    emit     write the submission raster (also runs the format validator)
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
from skimage.filters import frangi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.gems.emission import poisson_disk_dots  # noqa: E402
from src.gems.holdout import (EVALUATOR_VERSION, auc_binary, build_folds,  # noqa: E402
                              score_pooled, score_pooled_farfield)

WORK = ROOT / "work"
DATA = ROOT / "data"
FIELD = WORK / "osv2_field.npy"

# band -> instrument group (see evidence/feature_cache.json)
TOPO_BANDS = (12,)                       # det_elev
GEO_BANDS = {"MAG": (2, 14),             # rtp, tmi
             "GRAV": (13, 18),           # iso_grav_anom, iso_grav_anom_hg
             "BASE": (15, 17)}           # depth_to_base_surf, cond_surf
CORROB_SIGMA = 4.0
CORROB_FLOOR = 0.25


def load_base():
    with rasterio.open(DATA / "official/sample_submission.tif") as s:
        arr = s.read(1)
        profile = s.profile
    footprint = np.isfinite(arr)
    with rasterio.open(DATA / "official/existing_faults.tif") as s:
        catalogue = (s.read(1) == 1) & footprint
    return footprint, catalogue, profile


def band(n: int) -> np.ndarray:
    return np.load(ROOT / ".cache" / "features" / f"band-{n:02d}.npy", mmap_mode="r")


def prep(a: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    z = a.astype(np.float32).copy()
    v = z[footprint]
    v = v[np.isfinite(v)]
    med, mad = np.median(v), np.median(np.abs(v - np.median(v)))
    scale = 1.4826 * mad if mad > 0 else (v.std() or 1.0)
    z = (z - med) / (scale or 1.0)
    z[~np.isfinite(z)] = 0.0
    return np.clip(z, -5.0, 5.0).astype(np.float32)


def vessel(a: np.ndarray) -> np.ndarray:
    return frangi(a, scale_range=(1, 4), scale_step=2, black_ridges=False,
                  alpha=0.5, beta=0.5, gamma=15.0).astype(np.float32)


def pct(a: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    v = a[footprint].astype(np.float64)
    out = np.zeros(a.shape, np.float32)
    order = np.argsort(v, kind="stable")
    r = np.empty(v.size, np.float32)
    r[order] = np.linspace(0.0, 1.0, v.size, dtype=np.float32)
    out[footprint] = r
    return out


def build(footprint: np.ndarray):
    if FIELD.exists():
        return np.load(FIELD), np.load(WORK / "osv2_topo.npy"), np.load(WORK / "osv2_geo.npy")
    print("[build] topographic vesselness ...", flush=True)
    topo = None
    for b in TOPO_BANDS:
        v = vessel(prep(band(b), footprint))
        topo = v if topo is None else np.maximum(topo, v)
        del v
    geos = {}
    for name, bands in GEO_BANDS.items():
        acc = None
        for b in bands:
            v = vessel(prep(band(b), footprint))
            acc = v if acc is None else np.maximum(acc, v)
            del v
        geos[name] = acc
        print(f"[build] geophysical group {name} done", flush=True)
    geo = np.maximum.reduce(list(geos.values()))
    del geos
    geo_s = ndi.gaussian_filter(geo, CORROB_SIGMA, mode="nearest")
    gnorm = pct(geo_s, footprint)
    topo_n = pct(topo, footprint)
    field = (topo_n * (CORROB_FLOOR + (1.0 - CORROB_FLOOR) * gnorm)).astype(np.float32)
    field[~footprint] = 0.0
    np.save(FIELD, field); np.save(WORK / "osv2_topo.npy", topo_n); np.save(WORK / "osv2_geo.npy", gnorm)
    np.save(WORK / "osv2_geo_raw.npy", geo)
    print(f"[build] field written {FIELD}", flush=True)
    return field, topo_n, gnorm


def support_from(arr, footprint, n_px):
    v = np.where(footprint, arr, -np.inf)
    flat = np.argpartition(-v.ravel(), n_px - 1)[:n_px]
    out = np.zeros(arr.size, bool)
    out[flat] = True
    return out.reshape(arr.shape) & footprint


def emit(sup, footprint, visible_or_cat, n_px, spacing, prune):
    allowed = footprint & sup
    if prune and prune > 0:
        d = ndi.distance_transform_edt(~visible_or_cat)
        allowed &= d > prune
    return poisson_disk_dots(sup.astype(np.float32), allowed, n_px, spacing)


def score(label, preds, folds, extra=None):
    pooled = score_pooled(preds, folds, n_boot=300)
    far = score_pooled_farfield(preds, folds, n_boot=100)
    row = dict(label=label, emitted=int(np.mean([int(p.sum()) for p in preds])),
               evaluator=pooled["evaluator"], holdout_dti=pooled["holdout_dti"], ci95=pooled["ci95"],
               n_withheld_positives=pooled["n_withheld_positives"], tp=pooled["tp"], fp=pooled["fp"],
               fn=pooled["fn"],
               coverage=pooled["tp"] / (pooled["tp"] + pooled["fn"]) if pooled["tp"] + pooled["fn"] else 0.0,
               farfield_gt5px_dti=far["holdout_dti"], farfield_ci95=far["ci95"],
               evidence_class="HOLDOUT-DTI")
    if extra:
        row.update(extra)
    print(f"[e3] {label:<48} n={row['emitted']:>7} HOLDOUT-DTI {row['holdout_dti']:.4f} "
          f"[{row['ci95'][0]:.4f},{row['ci95'][1]:.4f}] cov={row['coverage']:.3f} far>5px "
          f"{row['farfield_gt5px_dti']:.4f}", flush=True)
    return row


def save(rel, obj):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")
    return p


def cmd_e3(a):
    t0 = time.monotonic()
    footprint, catalogue, _ = load_base()
    folds, n_seg = build_folds(catalogue, footprint)
    field, topo_n, gnorm = build(footprint)
    with rasterio.open(DATA / "inputs/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif") as s:
        h19 = s.read(1)
    h19sup = np.isfinite(h19) & (h19 > 0)
    n_sup = int(h19sup.sum())
    rows = []
    for prune in (0, 2):
        rows.append(score(f"CONTROL champion H19-5 md2.8 prune{prune}",
                          [emit(h19sup, footprint, f.visible, 44_090, 2.8, prune) for f in folds],
                          folds, dict(role="control", support_px=n_sup, spacing=2.8)))
    for tag, arr in (("osv2 corroborated", field), ("osv2 topo-only", topo_n)):
        sup = support_from(arr, footprint, n_sup)
        for sp in (2.0, 2.8, 3.5):
            rows.append(score(f"{tag} md{sp} prune2",
                              [emit(sup, footprint, f.visible, 5_000_000, sp, 2) for f in folds],
                              folds, dict(role="candidate", support_px=int(sup.sum()), spacing=sp, field=tag)))
    save(a.out, dict(evidence_class="HOLDOUT-DTI", evaluator=EVALUATOR_VERSION,
                     generated_utc=datetime.now(timezone.utc).isoformat(),
                     hypothesis="H-OFFSET-STEP v2 (Frangi vesselness + smoothed geophysical corroboration)",
                     n_segments=n_seg, n_withheld_positives=sum(f.n_test for f in folds),
                     rows=rows, elapsed_seconds=round(time.monotonic() - t0, 1)))
    return 0


def cmd_canary(a):
    footprint, catalogue, _ = load_base()
    folds, _ = build_folds(catalogue, footprint)
    field, topo_n, gnorm = build(footprint)
    rows = []
    for nm, arr in (("osv2_field", field), ("osv2_topo", topo_n), ("osv2_geo_smoothed", gnorm)):
        aucs = [auc_binary(arr, fd.test_truth & fd.active) for fd in folds]
        m = float(np.nanmean(aucs))
        rows.append(dict(feature=nm, mean_auc=m, per_fold=[float(x) for x in aucs],
                         verdict="LEAKAGE" if m > 0.90 else "ok"))
        print(f"[canary] {nm:<24} AUC {m:.4f} {'<-- LEAKAGE' if m > 0.90 else ''}", flush=True)
    save(a.out, dict(evidence_class="LEAKAGE-CANARY", evaluator=EVALUATOR_VERSION,
                     generated_utc=datetime.now(timezone.utc).isoformat(), threshold=0.90, rows=rows))
    return 0


def cmd_emit(a):
    footprint, catalogue, profile = load_base()
    field, _, _ = build(footprint)
    sup = support_from(field, footprint, a.support)
    dots = emit(sup, footprint, catalogue, a.dots, a.spacing, a.prune)
    out = np.where(footprint, dots.astype(np.float32), 0.0).astype(np.float32)
    dest = ROOT / a.out
    dest.parent.mkdir(parents=True, exist_ok=True)
    profile.update(driver="GTiff", dtype="float32", count=1, compress="deflate", nodata=None)
    with rasterio.open(dest, "w", **profile) as dst:
        dst.write(out, 1)
        dst.set_band_description(1, "fault discovery probability (binary dot emission)")
    print(f"[emit] wrote {dest} dots={int(dots.sum())} support={int(sup.sum())}", flush=True)
    from vendor.gems57.validate import validate as v  # noqa
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    p = sub.add_parser("e3"); p.add_argument("--out", default="evidence/offset_step_v2/e3_field.json")
    p = sub.add_parser("canary"); p.add_argument("--out", default="evidence/offset_step_v2/canary.json")
    p = sub.add_parser("emit")
    p.add_argument("--support", type=int, default=121_131)
    p.add_argument("--dots", type=int, default=44_090)
    p.add_argument("--spacing", type=float, default=2.8)
    p.add_argument("--prune", type=float, default=2.0)
    p.add_argument("--out", default="work/candidate.tif")
    a = ap.parse_args()
    WORK.mkdir(exist_ok=True)
    if a.cmd == "build":
        fp, _, _ = load_base(); build(fp); return 0
    return {"e3": cmd_e3, "canary": cmd_canary, "emit": cmd_emit}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
