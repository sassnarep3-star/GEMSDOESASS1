#!/usr/bin/env python3
"""H-OFFSET-STEP lane: build a multi-instrument across-strike-step field and score it.

Preregistered in knowledge/hypotheses_20261031_recalldom.md section 6 (written
after E1's negative geometry result, flagged there as post hoc).

Subcommands
    build    build the field and cache it to work/offset_step_field.npy
    e2       score the field on GEMSASS1-HR-v2-segment against the champion
    canary   single-feature leakage canary for the field and its parts

Every emitted number is HOLDOUT-DTI (evaluator version, withheld positives,
95% CI) or DATA-MEASUREMENT. No leaderboard projection is produced here.
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
from src.gems.holdout import (EVALUATOR_VERSION, auc_binary, build_folds,  # noqa: E402
                              score_pooled, score_pooled_farfield)

WORK = ROOT / "work"
DATA = ROOT / "data"
NAN_FILL = 0.0

# band index (1-based) -> group.  See evidence/feature_cache.json for names.
GROUPS = {
    "TOPO": (12, 19),                 # det_elev, det_elev_slope
    "MAG": (1, 2, 3, 9, 14),          # mag_anom, rtp, tmi_hg, tmi_vg, tmi
    "GRAV": (5, 11, 13, 18),          # iso_grav_anom_slope/_vg/_anom/_hg
    "BASE": (15, 17),                 # depth_to_base_surf, cond_surf
    "GEOSEIS": (4, 7, 8, 10, 16),     # geod_2ndinv, shear, dilat, deq, ieq
}
SIGMA = 2.0


def load_base():
    with rasterio.open(DATA / "official/sample_submission.tif") as s:
        footprint = np.isfinite(s.read(1))
    with rasterio.open(DATA / "official/existing_faults.tif") as s:
        catalogue = (s.read(1) == 1) & footprint
    return footprint, catalogue


def band_path(n: int) -> Path:
    return ROOT / ".cache" / "features" / f"band-{n:02d}.npy"


def robust_z(a: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    v = a[footprint]
    v = v[np.isfinite(v)]
    med = np.median(v)
    mad = np.median(np.abs(v - med))
    scale = 1.4826 * mad if mad > 0 else (v.std() if v.size else 1.0)
    if scale <= 0:
        scale = 1.0
    z = (a - med) / scale
    z[~np.isfinite(z)] = NAN_FILL
    return np.clip(z, -5.0, 5.0).astype(np.float32)


def lineament_score(z: np.ndarray, sigma: float = SIGMA):
    """Across-strike step score = coherence x larger eigenvalue of the structure tensor.

    For a linear step, the gradient is concentrated in the across-strike
    direction: the structure tensor is strongly anisotropic (coherence -> 1) and
    its larger eigenvalue measures the step energy.  A smooth surface has low
    energy; an isotropic rough patch has low coherence.
    """
    gx = ndi.sobel(z, axis=1).astype(np.float32)
    gy = ndi.sobel(z, axis=0).astype(np.float32)
    jxx = ndi.gaussian_filter(gx * gx, sigma, mode="nearest")
    jyy = ndi.gaussian_filter(gy * gy, sigma, mode="nearest")
    jxy = ndi.gaussian_filter(gx * gy, sigma, mode="nearest")
    del gx, gy
    tr = jxx + jyy
    det = np.sqrt(np.maximum((jxx - jyy) ** 2 + 4.0 * jxy * jxy, 0.0))
    l1 = 0.5 * (tr + det)
    coh = det / (tr + 1e-6)
    score = (coh * l1).astype(np.float32)
    del jxx, jyy, jxy, tr, det, l1, coh
    return score


def pct_norm(a: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Rank-normalise to [0,1] inside the footprint; 0 outside."""
    v = a[footprint]
    order = np.argsort(v, kind="stable")
    out = np.zeros(a.shape, np.float32)
    r = np.empty(v.size, np.float32)
    r[order] = np.linspace(0.0, 1.0, v.size, dtype=np.float32)
    out[footprint] = r
    return out


def build_field(footprint: np.ndarray, cache: Path):
    if cache.exists():
        field = np.load(cache)
        print(f"[build] reused cached field {cache} ({int((field > 0).sum())} nonzero)", flush=True)
        return field
    groups = {}
    for name, bands in GROUPS.items():
        acc = None
        for b in bands:
            p = band_path(b)
            if not p.exists():
                print(f"[build] missing band {b} in group {name}; skipped", flush=True)
                continue
            z = robust_z(np.load(p, mmap_mode="r").astype(np.float32), footprint)
            s = lineament_score(z)
            del z
            acc = s if acc is None else np.maximum(acc, s)
            del s
        groups[name] = pct_norm(acc, footprint)
        print(f"[build] group {name} done", flush=True)
        del acc
    topo = groups["TOPO"]
    geo = np.maximum.reduce([groups[k] for k in ("MAG", "GRAV", "BASE", "GEOSEIS")])
    field = (topo * geo).astype(np.float32)          # product = corroboration
    field[~footprint] = 0.0
    np.save(cache, field)
    np.save(str(cache).replace(".npy", "_topo.npy"), topo)
    np.save(str(cache).replace(".npy", "_geo.npy"), geo)
    for k, v in groups.items():
        np.save(str(cache).replace(".npy", f"_{k}.npy"), v)
    print(f"[build] field written {cache}; topo-only and geo-only parts cached too", flush=True)
    return field


def support_from(field: np.ndarray, footprint: np.ndarray, n_px: int) -> np.ndarray:
    v = np.where(footprint, field, -np.inf)
    flat = np.argpartition(-v.ravel(), n_px - 1)[:n_px]
    out = np.zeros(field.size, bool)
    out[flat] = True
    return out.reshape(field.shape) & footprint


def emit_for_fold(field_or_support, footprint, visible, n_px, spacing, fold_prune):
    if field_or_support.dtype == bool:
        f = field_or_support.astype(np.float32)
        sup = field_or_support
    else:
        sup = None
    allowed = footprint.copy()
    if fold_prune and fold_prune > 0:
        d = ndi.distance_transform_edt(~visible)
        allowed &= d > fold_prune
    if sup is not None:
        allowed &= sup
    return poisson_disk_dots(f if sup is None else f, allowed, n_px, spacing)


def score(label, preds_by_fold, folds, extra=None, n_boot=300):
    pooled = score_pooled(preds_by_fold, folds, n_boot=n_boot)
    far = score_pooled_farfield(preds_by_fold, folds, n_boot=100)
    row = dict(label=label, emitted=int(sum(int(p.sum()) for p in preds_by_fold) / max(1, len(preds_by_fold))),
               evaluator=pooled["evaluator"], holdout_dti=pooled["holdout_dti"], ci95=pooled["ci95"],
               n_withheld_positives=pooled["n_withheld_positives"], tp=pooled["tp"], fp=pooled["fp"],
               fn=pooled["fn"],
               coverage=pooled["tp"] / (pooled["tp"] + pooled["fn"]) if pooled["tp"] + pooled["fn"] else 0.0,
               farfield_gt5px_dti=far["holdout_dti"], farfield_ci95=far["ci95"],
               evidence_class="HOLDOUT-DTI")
    if extra:
        row.update(extra)
    print(f"[e2] {label:<46} n={row['emitted']:>7}  HOLDOUT-DTI {row['holdout_dti']:.4f} "
          f"[{row['ci95'][0]:.4f},{row['ci95'][1]:.4f}]  cov={row['coverage']:.3f}  "
          f"far>5px {row['farfield_gt5px_dti']:.4f}", flush=True)
    return row


def cmd_e2(args):
    t0 = time.monotonic()
    footprint, catalogue = load_base()
    folds, n_seg = build_folds(catalogue, footprint)
    print(f"[e2] evaluator {EVALUATOR_VERSION}; {n_seg} segments; "
          f"withheld positives {sum(f.n_test for f in folds)}", flush=True)

    field = build_field(footprint, WORK / "offset_step_field.npy")
    topo = np.load(WORK / "offset_step_field_topo.npy")
    geo = np.load(WORK / "offset_step_field_geo.npy")
    with rasterio.open(DATA / "inputs/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif") as s:
        h19 = s.read(1)
    h19_support = np.isfinite(h19) & (h19 > 0)
    n_support = int(h19_support.sum())
    print(f"[e2] champion (H19-5) support {n_support} px", flush=True)

    rows = []
    for prune in (0, 2):
        # ---- control: champion field, champion geometry, fold-aware prune ----
        preds = [emit_for_fold(h19_support, footprint & h19_support, f.visible, 44_090, 2.8, prune)
                 for f in folds]
        rows.append(score(f"CONTROL champion H19-5 md2.8 prune{prune}", preds, folds,
                          extra=dict(role="control", support_px=n_support, spacing=2.8)))
        del preds

    # ---- H-OFFSET-STEP: same support size, same geometry ----
    for tag, arr in (("product topo*geo", field), ("topo only", topo), ("geo only", geo)):
        sup = support_from(arr, footprint, n_support)
        preds = [emit_for_fold(sup, footprint & sup, f.visible, 44_090, 2.8, 2) for f in folds]
        rows.append(score(f"H-OFFSET-STEP {tag} md2.8 prune2", preds, folds,
                          extra=dict(role="candidate", support_px=int(sup.sum()), spacing=2.8, field=tag)))
        del preds, sup

    # ---- spacing sweep on the winning field, at matched support ----
    sup = support_from(field, footprint, n_support)
    for sp in (2.0, 2.8, 3.5, 4.5):
        preds = [emit_for_fold(sup, footprint & sup, f.visible, 5_000_000, sp, 2) for f in folds]
        rows.append(score(f"H-OFFSET-STEP product md{sp} prune2", preds, folds,
                          extra=dict(role="candidate", support_px=int(sup.sum()), spacing=sp)))
        del preds

    out = dict(evidence_class="HOLDOUT-DTI", evaluator=EVALUATOR_VERSION,
               generated_utc=datetime.now(timezone.utc).isoformat(),
               hypothesis="H-OFFSET-STEP: multi-instrument across-strike step corroboration",
               n_segments=n_seg, n_withheld_positives=sum(f.n_test for f in folds),
               rows=rows, elapsed_seconds=round(time.monotonic() - t0, 1))
    save(args.out, out)
    print(f"[e2] wrote {args.out}")
    return 0


def cmd_canary(args):
    footprint, catalogue = load_base()
    folds, _ = build_folds(catalogue, footprint)
    feats = {}
    field = build_field(footprint, WORK / "offset_step_field.npy")
    feats["offset_step_product"] = field
    for nm in ("topo", "geo", "TOPO", "MAG", "GRAV", "BASE", "GEOSEIS"):
        p = WORK / f"offset_step_field_{nm}.npy"
        if p.exists():
            feats[nm] = np.load(p)
    rows = []
    for nm, f in feats.items():
        aucs = [auc_binary(f, fd.test_truth & fd.active) for fd in folds]
        m = float(np.nanmean(aucs))
        rows.append(dict(feature=nm, mean_auc=m, per_fold=[float(a) for a in aucs],
                         verdict="LEAKAGE" if m > 0.90 else "ok"))
        print(f"[canary] {nm:<24} AUC {m:.4f} {'<-- LEAKAGE' if m > 0.90 else ''}", flush=True)
    save(args.out, dict(evidence_class="LEAKAGE-CANARY", evaluator=EVALUATOR_VERSION,
                        generated_utc=datetime.now(timezone.utc).isoformat(),
                        threshold=0.90, rows=rows))
    return 0


def save(rel, obj):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build"); p.set_defaults(fn=lambda a: (build_field(*load_base(), WORK / "offset_step_field.npy") and 0))
    p2 = sub.add_parser("e2"); p2.add_argument("--out", default="evidence/offset_step/e2_field.json")
    p3 = sub.add_parser("canary"); p3.add_argument("--out", default="evidence/offset_step/canary.json")
    a = ap.parse_args()
    WORK.mkdir(exist_ok=True)
    if a.cmd == "build":
        return 0
    return {"e2": cmd_e2, "canary": cmd_canary}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
