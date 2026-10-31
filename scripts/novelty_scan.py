#!/usr/bin/env python3
"""Scan a candidate against every competitive raster of the pinned 489-raster registry.

Measurements per raster (all with the shared, unmodified ``vendor.gems57.uniqueness`` code where a
comparator exists):

  * ``overlap3``  -- fraction of the candidate's dots within 3 px of that raster's positive support,
    the protocol's literal definition ("every finite positive pixel is a dot").
  * ``rho``       -- Spearman rank correlation on the footprint (sampled to ``RHO_SAMPLE`` pixels for
    speed; the sample size is recorded, and a |rho| that could exceed 0.90 is re-measured exactly).
  * ``jaccard``   -- overlap of the two binary dot sets.

Two-stage cost control, both conservative:

  1. ``window_bound``: for every raster, each candidate dot is tested for *any* positive neighbour in
     its 7x7 window (49 gathers on 37k indices -- cheap, no full-grid dilation). A 7x7 square window
     contains the radius-3 disk, so ``window_bound >= overlap3`` **always**: it is an upper bound, not
     an approximation.
  2. Every raster is scanned this way. The exact shared ``dot_overlap`` (disk dilation) is run for
     rasters with ``window_bound >= EXACT_AT``, and the exact value replaces the bound. Rasters below
     the threshold keep their bound and are labelled ``status="bounded"`` -- their true overlap is
     <= the reported number, which is what a clearance argument needs.

Synthetic calibration fixtures (``inputs/calibration/*``, ``*lattice*``) and the explicit 32x48
FORMAT_TEST file are reported separately and exempted (AMEND-LATTICE-01).

Usage: python scripts/novelty_scan.py <tif-or-npy> [--out evidence/kdam/novelty_<name>.json]
"""
from __future__ import annotations

import argparse
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
from src.gems.grid import read_band  # noqa: E402

INVENTORY = ROOT / "registry/focus_inventory_20261030.json"
OVERLAP_LIMIT = 0.70
RHO_LIMIT = 0.90
EXACT_AT = 0.05          # exact shared dot_overlap above this bound
RHO_SAMPLE = 500_000
R = 3


EXEMPT_PREFIXES = ("inputs/calibration/",)
EXEMPT_NAMES = ("gems36_format_test_not_submission.tif",)


def is_exempt(path: str) -> bool:
    """Exempt only the documented synthetic fixtures.

    Directory-based, not substring-based: a filename containing "lattice" is a *competitive*
    submission (e.g. `24gems-interior-offlattice-…`, `gems25-…-latticegap-…`) and must be compared.
    """
    p = path.lower()
    return p.startswith(EXEMPT_PREFIXES) or p.rsplit("/", 1)[-1] in EXEMPT_NAMES


def load_candidate(path: Path, shape=(3730, 3292)) -> np.ndarray:
    if path.suffix == ".npy":
        return np.load(path).astype(bool)
    if path.suffix == ".npz":
        z = np.load(path)
        return np.asarray(z[sorted(z.files)[0]], bool)
    with rasterio.open(path) as s:
        if s.shape != shape:
            raise SystemExit(f"candidate grid {s.shape} != {shape}")
        a = s.read(1)
    return np.nan_to_num(a, nan=0.0) > 0.0


def spearman_sampled(a: np.ndarray, b: np.ndarray, foot: np.ndarray, rng, exact=False) -> float:
    idx = np.flatnonzero(foot.ravel())
    if not exact and idx.size > RHO_SAMPLE:
        idx = rng.choice(idx, RHO_SAMPLE, replace=False)
    x = a.ravel()[idx].astype(np.float32)
    y = b.ravel()[idx].astype(np.float32)
    if x.size < 100 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    rx, ry = rankdata(x), rankdata(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    den = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    return float((rx * ry).sum() / den) if den else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("candidate")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    cand_path = Path(args.candidate)
    mine = load_candidate(cand_path)
    if not mine.any():
        raise SystemExit("candidate has no dots")
    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as s:
        foot = np.isfinite(s.read(1))
    inv = json.loads(INVENTORY.read_text())
    H, W = mine.shape
    ys, xs = np.nonzero(mine)
    n_dots = ys.size
    # 7x7 window offsets (contains the radius-3 disk)
    offs = [(dy, dx) for dy in range(-R, R + 1) for dx in range(-R, R + 1)]
    rng = np.random.default_rng(20261031)

    rows, exempt = [], []
    t0 = time.time()
    for i, item in enumerate(inv["rasters"]):
        if is_exempt(item["path"]):
            exempt.append(dict(repo=item["repo"], path=item["path"]))
            continue
        a = read_band(ROOT / item["local"])
        theirs = np.nan_to_num(a, nan=0.0) > 0.0
        if theirs.shape != mine.shape:
            rows.append(dict(repo=item["repo"], path=item["path"], sha256=item["sha256"],
                             status="incompatible-grid", shape=list(theirs.shape),
                             their_dots=int(theirs.sum()), overlap3=None, rho=None,
                             duplicate=False, window_bound=None, jaccard=None,
                             on_dot_fraction=None))
            del a, theirs
            continue
        the_y, the_x = np.nonzero(theirs)
        their_dots = the_y.size
        hit = np.zeros(n_dots, bool)
        for dy, dx in offs:
            yy, xx = ys + dy, xs + dx
            ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
            if ok.any():
                hit[ok] |= theirs[yy[ok], xx[ok]]
        bound = float(hit.mean())
        row = dict(repo=item["repo"], path=item["path"], sha256=item["sha256"],
                   their_dots=their_dots, window_bound=bound)
        # exact set comparisons
        inter = int((theirs & mine).sum())
        union = int((theirs | mine).sum())
        row["jaccard"] = inter / union if union else 0.0
        row["on_dot_fraction"] = float(theirs[ys, xs].mean())
        rho_sample = RHO_SAMPLE
        row["rho"] = spearman_sampled(mine, theirs, foot, rng)
        if bound >= EXACT_AT:
            row["overlap3"] = dot_overlap(mine, theirs, 3.0)
            row["status"] = "exact"
            if abs(row["rho"]) > 0.80 or np.isnan(row["rho"]):
                row["rho"] = spearman_sampled(mine, theirs, foot, rng, exact=True)
                rho_sample = int(foot.sum())
        else:
            row["overlap3"] = None
            row["status"] = "bounded"
        row["rho_sample_pixels"] = rho_sample
        row["duplicate"] = bool((row["overlap3"] if row["overlap3"] is not None else bound) > OVERLAP_LIMIT
                                or (row["rho"] is not None and not np.isnan(row["rho"]) and row["rho"] > RHO_LIMIT))
        rows.append(row)
        del a, theirs, the_y, the_x
        if (i + 1) % 100 == 0:
            print(f"scan {i + 1}/{len(inv['rasters'])} measured={len(rows)} t={time.time() - t0:.0f}s", flush=True)

    exact_rows = [r for r in rows if r["overlap3"] is not None]
    bounded = [r for r in rows if r["overlap3"] is None and r.get("status") == "bounded"]
    incompatible = [r for r in rows if r.get("status") == "incompatible-grid"]
    comparable = [r for r in rows if r.get("status") != "incompatible-grid"]
    worst = max(comparable, key=lambda r: (r["overlap3"] if r["overlap3"] is not None else r["window_bound"]))
    offenders = [r for r in rows if r["duplicate"]]
    out = dict(
        candidate=str(cand_path), candidate_dots=int(n_dots),
        registry_inventory=str(INVENTORY.relative_to(ROOT)), snapshot_utc=inv["snapshot_utc"],
        rasters_in_inventory=len(inv["rasters"]), competitive_rasters=len(rows),
        measured_exactly=len(exact_rows), bounded=len(bounded), screened_out=0,
        incompatible_grid=len(incompatible),
        thresholds=dict(overlap_limit=OVERLAP_LIMIT, rho_limit=RHO_LIMIT, radius_px=3.0),
        method="every candidate dot tested against a 7x7 window (upper bound on the 3 px disk overlap); "
               "exact shared dot_overlap wherever the bound is >= 0.05; Spearman sampled to "
               f"{RHO_SAMPLE} footprint pixels, re-measured exactly when |rho| > 0.80",
        max_overlap3=max((r["overlap3"] for r in exact_rows), default=None),
        max_overlap3_upper_bound=max(max((r["overlap3"] for r in exact_rows), default=0.0),
                                     max((r["window_bound"] for r in bounded), default=0.0)),
        worst_raster=dict(repo=worst["repo"], path=worst["path"],
                          overlap3=worst["overlap3"] if worst["overlap3"] is not None else worst["window_bound"],
                          status=worst["status"]),
        max_rho=max((r["rho"] for r in rows if r["rho"] is not None and not np.isnan(r["rho"])), default=None),
        duplicates=[dict(repo=r["repo"], path=r["path"],
                         overlap3=r["overlap3"] if r["overlap3"] is not None else r["window_bound"],
                         status=r["status"], rho=r["rho"]) for r in offenders],
        exempt_fixtures=exempt,
        cleared=(len(offenders) == 0),
        cleared_scope="all %d competitive rasters: %d exact, %d bounded above by the reported value, "
                      "%d on an incompatible grid" % (len(rows), len(exact_rows), len(bounded),
                                                      len(incompatible)),
        per_raster=rows, runtime_s=round(time.time() - t0, 1),
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    dest = Path(args.out) if args.out else ROOT / f"evidence/kdam/novelty_{cand_path.stem}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, allow_nan=False, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("candidate_dots", "measured_exactly", "bounded", "max_overlap3",
                                          "max_overlap3_upper_bound", "max_rho", "cleared",
                                          "worst_raster")}, indent=2))
    print("offenders:", [(r["repo"], r["path"].split("/")[-1], round(r["overlap3"], 4), r["status"])
                         for r in offenders[:10]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
