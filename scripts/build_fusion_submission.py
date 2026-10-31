#!/usr/bin/env python3
"""E4 + packaging: rank-fusion of three independent published lineament fields.

Why this is the deliverable (all of it measured, none of it narrative):

* E1/E2/E3/E3b established that the champion's emission geometry is already at
  the certified optimum and that none of this session's four new fields beat it,
  so the field -- not the emission -- is what has to change.
* support screening (evidence/offset_step_v2/support_screen.json) showed the
  three published lineament fields H19-5, H19-4 and H16-1 are the only locally
  available supports within CI of the champion, and that they are statistically
  indistinguishable from each other on the holdout (0.1048 / 0.1039 / 0.1027).
* Combining independent detectors by the MEAN OF THEIR WITHIN-FOOTPRINT RANKS is
  the standard robust fusion and is the cheapest way to raise the precision
  term ``g`` that the certified algebra identifies as the only live lever.

Emission is the certified optimum: 2.8 px Poisson-disk dots, >= 2 px off the
known catalogue, dot field (no thinning below the optimum, no corridor).

Outputs
  work/<name>.tif            single-band float32, 0 outside the footprint
  docs/downloads/<name>.tif  the downloadable copy
  docs/downloads/<name>.zip  one-TIFF zip, as the portal also accepts
  docs/downloads/<name>.json full audit receipt
"""
from __future__ import annotations

import argparse
import hashlib
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
from vendor.gems57.submission_writer import write_submission  # noqa: E402
from vendor.gems57.validate import validate  # noqa: E402

DATA = ROOT / "data"
IN = DATA / "inputs"
N_SUP = 121_131
N_DOTS = 44_090
SPACING = 2.8
PRUNE = 2.0

MEMBERS = {
    "H19-5": IN / "gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif",
    "H19-4": IN / "gems19-h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan.tif",
    "H16-1": IN / "gems16-h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan.tif",
}


def load_base():
    with rasterio.open(DATA / "official/sample_submission.tif") as s:
        raw = s.read(1)
        profile = s.profile
    footprint = np.isfinite(raw)
    with rasterio.open(DATA / "official/existing_faults.tif") as s:
        catalogue = (s.read(1) == 1) & footprint
    return footprint, catalogue, profile


def rank_field(a: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    v = np.where(np.isfinite(a), a, 0.0).astype(np.float64)
    out = np.zeros(v.shape, np.float32)
    vals = v[footprint]
    order = np.argsort(vals, kind="stable")
    r = np.empty(vals.size, np.float32)
    r[order] = np.linspace(0.0, 1.0, vals.size, dtype=np.float32)
    out[footprint] = r
    return out


def support_from(arr, footprint, n):
    v = np.where(footprint, arr, -np.inf)
    flat = np.argpartition(-v.ravel(), n - 1)[:n]
    out = np.zeros(arr.size, bool)
    out[flat] = True
    return out.reshape(arr.shape) & footprint


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--members", nargs="+", default=list(MEMBERS))
    ap.add_argument("--support", type=int, default=N_SUP)
    ap.add_argument("--dots", type=int, default=N_DOTS)
    ap.add_argument("--spacing", type=float, default=SPACING)
    ap.add_argument("--prune", type=float, default=PRUNE)
    ap.add_argument("--name", default=None)
    ap.add_argument("--no-holdout", action="store_true")
    a = ap.parse_args()
    t0 = time.monotonic()

    footprint, catalogue, profile = load_base()
    ranks = []
    for m in a.members:
        with rasterio.open(MEMBERS[m]) as s:
            ranks.append(rank_field(s.read(1), footprint))
    fused = np.mean(ranks, axis=0).astype(np.float32)
    fused[~footprint] = 0.0
    support = support_from(fused, footprint, a.support)
    print(f"[fusion] members={a.members} support={int(support.sum())} px", flush=True)

    # ---- holdout: fold-aware visible-catalogue prune, same geometry as control
    holdout_rows = []
    if not a.no_holdout:
        folds, _ = build_folds(catalogue, footprint)
        for tag, sup in (("FUSION", support),):
            preds = [poisson_disk_dots(sup.astype(np.float32),
                                       footprint & sup & (ndi.distance_transform_edt(~f.visible) > a.prune),
                                       a.dots, a.spacing) for f in folds]
            pooled = score_pooled(preds, folds, n_boot=300)
            far = score_pooled_farfield(preds, folds, n_boot=100)
            holdout_rows.append(dict(label=tag, emitted=int(np.mean([int(p.sum()) for p in preds])),
                                     evaluator=pooled["evaluator"], holdout_dti=pooled["holdout_dti"],
                                     ci95=pooled["ci95"], n_withheld_positives=pooled["n_withheld_positives"],
                                     tp=pooled["tp"], fp=pooled["fp"], fn=pooled["fn"],
                                     coverage=pooled["tp"] / (pooled["tp"] + pooled["fn"]),
                                     farfield_gt5px_dti=far["holdout_dti"], evidence_class="HOLDOUT-DTI"))
            print(f"[fusion] {tag} HOLDOUT-DTI {pooled['holdout_dti']:.4f} "
                  f"[{pooled['ci95'][0]:.4f},{pooled['ci95'][1]:.4f}] cov={holdout_rows[-1]['coverage']:.3f}",
                  flush=True)
            del preds

    # ---- live emission: prune against the FULL catalogue
    dcat = ndi.distance_transform_edt(~catalogue)
    allowed = footprint & support & (dcat > a.prune)
    dots = poisson_disk_dots(support.astype(np.float32), allowed, a.dots, a.spacing)
    pred = np.where(footprint, dots.astype(np.float32), 0.0).astype(np.float32)
    print(f"[fusion] live emission: {int(dots.sum())} dots; "
          f"min catalogue distance {float(dcat[dots].min()):.2f} px", flush=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short = hashlib.sha256(np.packbits(dots).tobytes()).hexdigest()[:12]
    name = a.name or f"gemsass1-fusion3-rankmean-{int(dots.sum())}dots-{stamp}-{short}-zeros"
    note = (f"GEMSASS1: rank-mean fusion of H19-5/H19-4/H16-1, {a.spacing}px dots, "
            f">{a.prune}px off catalogue")[:140]
    dest_dir = ROOT / "docs/downloads"
    dest_dir.mkdir(parents=True, exist_ok=True)
    tif = dest_dir / f"{name}.tif"
    write_submission(tif, pred, DATA / "official/sample_submission.tif", footprint,
                     note=note, name=name, catalogue=catalogue,
                     metadata=dict(hypothesis="H-FUSION3-RANKMEAN", mechanism=note,
                                   members=a.members, support_px=int(support.sum()),
                                   spacing_px=a.spacing, catalogue_prune_px=a.prune))
    receipt = validate(tif, footprint=footprint, catalogue=catalogue)

    with rasterio.open(tif) as s:
        arr = s.read(1)
    aud = dict(evidence_class="CANDIDATE-AUDIT",
               generated_utc=datetime.now(timezone.utc).isoformat(),
               name=name, note=note, file=str(tif.relative_to(ROOT)),
               sha256=sha256(tif), bytes=tif.stat().st_size,
               dots=int(dots.sum()), support_px=int(support.sum()),
               spacing_px=a.spacing, catalogue_prune_px=a.prune,
               members=a.members,
               grid=dict(crs="EPSG:32611", shape=list(arr.shape),
                         transform=list(tuple(rasterio.open(tif).transform)[:6])),
               values=dict(min=float(arr.min()), max=float(arr.max()),
                           finite_inside_footprint=bool(np.isfinite(arr[footprint]).all()),
                           nonfinite_outside=int((~np.isfinite(arr[~footprint])).sum()),
                           in_0_1=bool(arr.min() >= 0 and arr.max() <= 1)),
               dots_on_catalogue=int((dots & catalogue).sum()),
               min_catalogue_distance_px=float(dcat[dots].min()),
               validator=receipt, holdout=holdout_rows,
               elapsed_seconds=round(time.monotonic() - t0, 1))
    (dest_dir / f"{name}.json").write_text(json.dumps(aud, indent=2, allow_nan=False) + "\n")
    print(f"[fusion] wrote {tif} sha256={aud['sha256'][:16]} dots={aud['dots']}", flush=True)
    print(f"[fusion] validator: {json.dumps({k: v for k, v in receipt.items() if isinstance(v, (bool, str, int, float))})[:600]}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
