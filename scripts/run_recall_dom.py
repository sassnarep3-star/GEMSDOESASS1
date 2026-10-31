#!/usr/bin/env python3
"""H-RECALL-DOM lane runner (preregistered in knowledge/hypotheses_20261031_recalldom.md).

Subcommands
    e1      emission-geometry sweep on a FIXED field (isolates geometry)
    e2      same machinery on a graded posterior built from the official stack
    canary  single-feature leakage canary on the withheld truth

Every number written to evidence/ is labelled HOLDOUT-DTI (evaluator version,
withheld positives, 95% CI) or DATA-MEASUREMENT. Nothing here projects a
leaderboard score and nothing uploads.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.gems.emission import catalogue_exclusion, poisson_disk_dots  # noqa: E402
from src.gems.holdout import (EVALUATOR_VERSION, auc_binary, build_folds,  # noqa: E402
                              score_pooled, score_pooled_farfield)

ALPHA = 0.2
BETA = 0.8
DATA = ROOT / "data"


def save(rel, obj):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")
    return p


def load_base():
    with rasterio.open(DATA / "official/sample_submission.tif") as s:
        raw = s.read(1)
    footprint = np.isfinite(raw)
    with rasterio.open(DATA / "official/existing_faults.tif") as s:
        catalogue = (s.read(1) == 1) & footprint
    return footprint, catalogue


def read_tif(path):
    with rasterio.open(path) as s:
        return s.read(1)


def folds_cached(footprint, catalogue):
    folds, n_seg = build_folds(catalogue, footprint)
    return folds, n_seg


def describe(pred, folds, tag, extra=None, n_boot=300):
    same = [pred] * len(folds)
    pooled = score_pooled(same, folds, n_boot=n_boot)
    far = score_pooled_farfield(same, folds, n_boot=100)
    row = dict(tag=tag, emitted=int(pred.sum()),
               evaluator=pooled["evaluator"], holdout_dti=pooled["holdout_dti"],
               ci95=pooled["ci95"], n_withheld_positives=pooled["n_withheld_positives"],
               tp=pooled["tp"], fp=pooled["fp"], fn=pooled["fn"],
               coverage=pooled["tp"] / (pooled["tp"] + pooled["fn"]) if pooled["tp"] + pooled["fn"] else 0.0,
               farfield_gt5px_dti=far["holdout_dti"], farfield_ci95=far["ci95"],
               evidence_class="HOLDOUT-DTI")
    if extra:
        row.update(extra)
    print(f"[e1] {tag:<44} n={row['emitted']:>7}  HOLDOUT-DTI {row['holdout_dti']:.4f} "
          f"[{row['ci95'][0]:.4f},{row['ci95'][1]:.4f}]  cov={row['coverage']:.3f} "
          f"far>{5}px {row['farfield_gt5px_dti']:.4f}", flush=True)
    return row


def cmd_e1(args):
    t0 = time.monotonic()
    footprint, catalogue = load_base()
    folds, n_seg = folds_cached(footprint, catalogue)
    print(f"[e1] evaluator {EVALUATOR_VERSION}; {n_seg} catalogue segments; "
          f"withheld positives {sum(f.n_test for f in folds)}", flush=True)

    field_path = DATA / "inputs/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif"
    h19 = read_tif(field_path)
    support = np.isfinite(h19) & (h19 > 0)
    print(f"[e1] H19-5 support {int(support.sum())} px "
          f"({100*support.sum()/footprint.sum():.2f}% of the footprint); "
          f"overlap with catalogue {100*(support & catalogue).sum()/max(1,int(catalogue.sum())):.1f}% of catalogue px",
          flush=True)

    rows = []
    for prune in (0, 2):
        allowed = footprint & (catalogue_exclusion(catalogue, prune) if prune else np.ones_like(footprint))
        # champion reproduction control
        dots = poisson_disk_dots(support.astype(np.float32), allowed, 44_090, 2.8)
        rows.append(describe(dots, folds, f"champion-repro prune{prune} md2.8 n44090"))
        for md, nmax in ((1.0, 10_000_000), (1.5, 10_000_000), (2.0, 10_000_000),
                         (4.0, 10_000_000), (6.0, 10_000_000)):
            d = poisson_disk_dots(support.astype(np.float32), allowed, nmax, md)
            rows.append(describe(d, folds, f"md{md} prune{prune} (full support thinned)"))
        # fixed-mass controls at the champion's mass
        for md in (1.0, 1.5, 2.0, 2.8):
            d = poisson_disk_dots(support.astype(np.float32), allowed, 37_654, md)
            rows.append(describe(d, folds, f"md{md} prune{prune} n37654 (mass-matched)"))

    out = dict(evidence_class="HOLDOUT-DTI", evaluator=EVALUATOR_VERSION,
               generated_utc=datetime.now(timezone.utc).isoformat(),
               hypothesis="H-RECALL-DOM E1: emission geometry at fixed field",
               field="H19-5 binary support (champion's own field)",
               field_support_px=int(support.sum()),
               n_segments=n_seg, n_withheld_positives=sum(f.n_test for f in folds),
               rows=rows, elapsed_seconds=round(time.monotonic() - t0, 1))
    save(args.out, out)
    print(f"[e1] wrote {args.out}")
    return 0


def cmd_canary(args):
    footprint, catalogue = load_base()
    folds, _ = folds_cached(footprint, catalogue)
    feats = {}
    h19 = read_tif(DATA / "inputs/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif")
    feats["h19_5_support"] = np.nan_to_num(h19, nan=0.0)
    for name in ("lidar_scarp_features", "geodawn_rad", "geodawn_extensions"):
        p = DATA / f"external/{name}_u8.tif"
        if not p.exists():
            continue
        with rasterio.open(p) as s:
            arr = s.read()
        meta = json.loads((DATA / f"external/{name}.json").read_text())
        names = meta.get("channels") or meta.get("bands") or []
        for i in range(arr.shape[0]):
            nm = f"{name}:{names[i] if i < len(names) else i}"
            feats[nm] = arr[i].astype(np.float32)
    rows = []
    for nm, f in feats.items():
        aucs = [auc_binary(f, fd.test_truth & fd.active) for fd in folds]
        m = float(np.mean(aucs))
        rows.append(dict(feature=nm, mean_auc=m, per_fold=[float(a) for a in aucs],
                         verdict="LEAKAGE" if m > 0.90 else "ok"))
        print(f"[canary] {nm:<52} AUC {m:.4f} {'<-- LEAKAGE' if m > 0.90 else ''}", flush=True)
    save(args.out, dict(evidence_class="LEAKAGE-CANARY", evaluator=EVALUATOR_VERSION,
                        generated_utc=datetime.now(timezone.utc).isoformat(),
                        threshold=0.90, rows=rows))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("e1"); p1.add_argument("--out", default="evidence/recall_dom/e1_geometry_sweep.json")
    p2 = sub.add_parser("canary"); p2.add_argument("--out", default="evidence/recall_dom/canary.json")
    p3 = sub.add_parser("e2"); p3.add_argument("--out", default="evidence/recall_dom/e2_graded.json")
    a = ap.parse_args()
    return {"e1": cmd_e1, "canary": cmd_canary}.get(a.cmd, lambda _: 1)(a)


if __name__ == "__main__":
    raise SystemExit(main())
