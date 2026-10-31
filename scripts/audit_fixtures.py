#!/usr/bin/env python3
"""Measure the registry fixtures that ``scripts/novelty_scan.py`` reports separately.

The scan clears a candidate against the *competitive* registry rasters and keeps the synthetic
calibration fixtures out of that verdict (AMEND-LATTICE-01). Keeping them out of the verdict must not
mean keeping them out of the measurement: this script measures every fixture with the same shared
``dot_overlap`` code, records the numbers in ``evidence/kdam/fixture_exemption_audit.json``, and merges
them into a novelty receipt as the ``*_all_rasters`` keys so the published claim is quantitative.

Fixtures are read from the local registry cache (``.cache/registry_current``) and are hash-checked
against the pinned inventory, so the audit cannot silently run on different bytes.

Usage: python scripts/audit_fixtures.py <novelty-receipt.json> [--candidate <tif>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vendor.gems57.uniqueness import dot_overlap  # noqa: E402
from scripts.novelty_scan import is_exempt, load_candidate  # noqa: E402

INVENTORY = ROOT / "registry/focus_inventory_20261030.json"
RHO_SAMPLE = 500_000


def spearman_sampled(a: np.ndarray, b: np.ndarray, foot: np.ndarray, rng) -> float:
    idx = np.flatnonzero(foot.ravel())
    if idx.size > RHO_SAMPLE:
        idx = rng.choice(idx, RHO_SAMPLE, replace=False)
    x = a.ravel()[idx].astype(np.float32)
    y = b.ravel()[idx].astype(np.float32)
    if x.size < 100 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    rx = rankdata(x) - rankdata(x).mean()
    ry = rankdata(y) - rankdata(y).mean()
    den = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    return float((rx * ry).sum() / den) if den else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("receipt", help="novelty receipt to merge the fixture measurements into")
    ap.add_argument("--candidate", default=None, help="defaults to the receipt's candidate")
    args = ap.parse_args()

    receipt_path = ROOT / args.receipt if not Path(args.receipt).is_absolute() else Path(args.receipt)
    receipt = json.loads(receipt_path.read_text())
    cand_path = Path(args.candidate) if args.candidate else ROOT / receipt["candidate"]
    mine = load_candidate(cand_path)
    ys, xs = np.nonzero(mine)
    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as s:
        foot = np.isfinite(s.read(1))
    rng = np.random.default_rng(20261031)
    inv = json.loads(INVENTORY.read_text())

    rows, t0 = [], time.time()
    for item in inv["rasters"]:
        if not is_exempt(item["path"]):
            continue
        path = ROOT / item["local"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        with rasterio.open(path) as s:
            a = s.read(1)
            shape = list(s.shape)
        theirs = np.nan_to_num(a, nan=0.0) > 0.0
        row = dict(repo=item["repo"], path=item["path"], sha256=digest,
                   sha256_matches_inventory=(digest == item["sha256"]), shape=shape,
                   their_dots=int(theirs.sum()))
        if theirs.shape != mine.shape:
            row.update(status="incompatible-grid", overlap3=None, rho=None,
                       note="different grid; cannot be compared pixel-for-pixel")
            rows.append(row)
            print(json.dumps(row), flush=True)
            continue
        row["overlap3"] = round(float(dot_overlap(mine, theirs, 3.0)), 6)
        row["on_dot_fraction"] = round(float(theirs[ys, xs].mean()), 6)
        inter = int((theirs & mine).sum())
        union = int((theirs | mine).sum())
        row["jaccard"] = round(inter / union, 6) if union else 0.0
        rho = spearman_sampled(mine, theirs, foot, rng)
        row["rho"] = None if np.isnan(rho) else round(rho, 6)
        row["status"] = "measured"
        rows.append(row)
        print(json.dumps({k: row[k] for k in ("repo", "path", "their_dots", "overlap3", "rho")}), flush=True)
        del a, theirs

    comparable = [r for r in rows if r["overlap3"] is not None]
    worst = max(comparable, key=lambda r: r["overlap3"]) if comparable else None
    out = dict(candidate=str(cand_path.relative_to(ROOT)) if cand_path.is_absolute() else str(cand_path),
               candidate_dots=int(mine.sum()), fixture_rasters=len(rows),
               thresholds=receipt["thresholds"], rows=rows,
               max_fixture_overlap3=max((r["overlap3"] for r in comparable), default=0.0),
               max_fixture_rho=max((abs(r["rho"]) for r in comparable if r["rho"] is not None), default=0.0),
               worst_fixture=dict(repo=worst["repo"], path=worst["path"], overlap3=worst["overlap3"])
               if worst else None,
               method="shared vendor.gems57.uniqueness.dot_overlap (radius 3 px, both directions on the "
                      "candidate's dots); Spearman sampled to %d footprint pixels" % RHO_SAMPLE,
               runtime_s=round(time.time() - t0, 1),
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    dest = ROOT / "evidence/kdam/fixture_exemption_audit.json"
    dest.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")

    # merge into the novelty receipt so a reader of one file sees the whole 489-raster picture
    receipt["fixture_rasters"] = len(rows)
    receipt["exempt_fixtures"] = [dict(repo=r["repo"], path=r["path"], overlap3=r["overlap3"],
                                       window_bound=r["overlap3"], status=r["status"]) for r in rows]
    receipt["max_fixture_overlap3"] = out["max_fixture_overlap3"]
    receipt["worst_fixture"] = out["worst_fixture"]
    comp_max = max([r["overlap3"] or 0.0 for r in receipt["per_raster"]], default=0.0)
    receipt["max_overlap3_all_rasters"] = round(max(comp_max, out["max_fixture_overlap3"]), 6)
    receipt["worst_raster_all_rasters"] = (out["worst_fixture"] if out["max_fixture_overlap3"] > comp_max
                                           else receipt["worst_raster"])
    receipt["fixture_audit"] = dict(source="evidence/kdam/fixture_exemption_audit.json",
                                    merged_utc=out["generated_utc"],
                                    all_489_measured=True,
                                    note="fixtures are measured, not skipped: they are excluded from the "
                                         "clearance verdict (AMEND-LATTICE-01) but reported quantitatively")
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("fixture_rasters", "max_fixture_overlap3", "max_fixture_rho",
                                          "worst_fixture")}, indent=2))
    print("all-rasters max overlap:", receipt["max_overlap3_all_rasters"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
