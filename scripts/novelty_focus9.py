#!/usr/bin/env python3
"""Novelty audit of a candidate raster against the nine focus-site best files.

Metrics, all computed from bytes:
  exact_duplicate      sha256 of the positive-pixel set
  jaccard              |A n B| / |A u B| on dot sets
  directed_3px(A->B)   fraction of A's dots within 3 px (300 m) of any B dot
  spearman             rank correlation of the two rasters inside the footprint
  kdtree_crosscheck    independent re-measure of directed_3px with a KD-tree

Also re-verifies, from bytes, the claim that GEMSDOE32's 0.2778 file is the
GEMSDOE25 d2-8 dot set with the catalogue-proximal dots removed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vendor.gems57.metric import RADIUS_PX  # noqa: E402

BEST9 = {
    "GEMSDOE24": ("data/inputs/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif", 0.2477),
    "GEMSDOE25": ("/tmp/best9/GEMSDOE25.tif", 0.2600),
    "GEMSDOE27": ("/tmp/best9/GEMSDOE27.tif", 0.2449),
    "GEMSDOE28": ("/tmp/best9/GEMSDOE28.tif", 0.2710),
    "GEMSDOE30": ("/tmp/best9/GEMSDOE30.tif", 0.2600),
    "GEMSDOE31": ("/tmp/best9/GEMSDOE31.tif", 0.2708),
    "GEMSDOE32": ("/tmp/best9/GEMSDOE32.tif", 0.2778),
    "GEMSDOE33": ("/tmp/best9/GEMSDOE33.tif", 0.2632),
    "GEMSDOE36": ("/tmp/best9/GEMSDOE36.tif", 0.2750),
}
CAT = ROOT / "data/official/existing_faults.tif"
SAMPLE = ROOT / "data/official/sample_submission.tif"


def dots_of(path):
    with rasterio.open(path) as s:
        a = s.read(1)
    return np.isfinite(a) & (a > 0), a


def set_hash(mask: np.ndarray) -> str:
    return hashlib.sha256(np.packbits(mask).tobytes()).hexdigest()


def directed(a: np.ndarray, b: np.ndarray, radius=RADIUS_PX) -> float:
    if not a.any() or not b.any():
        return 0.0
    d = ndi.distance_transform_edt(~b)
    return float((d[a] <= radius).mean())


def directed_kdtree(a: np.ndarray, b: np.ndarray, radius=RADIUS_PX) -> float:
    ya, xa = np.nonzero(a)
    yb, xb = np.nonzero(b)
    if ya.size == 0 or yb.size == 0:
        return 0.0
    tree = cKDTree(np.c_[yb, xb])
    n = tree.query_ball_point(np.c_[ya, xa], r=radius, return_length=True)
    n = np.asarray(n)
    return float((n > 0).mean())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--out", default="evidence/offset_step_v2/novelty_focus9.json")
    a = ap.parse_args()

    with rasterio.open(SAMPLE) as s:
        footprint = np.isfinite(s.read(1))
    with rasterio.open(CAT) as s:
        catalogue = (s.read(1) == 1) & footprint

    cand, cand_arr = dots_of(a.candidate)
    rows = []
    print(f"[novelty] candidate {Path(a.candidate).name}: {int(cand.sum())} dots, "
          f"dot-set sha256 {set_hash(cand)[:16]}", flush=True)
    for site, (path, score) in BEST9.items():
        p = Path(path)
        if not p.is_absolute():
            p = ROOT / p
        if not p.exists():
            rows.append(dict(site=site, status="missing", path=str(p)))
            continue
        m, arr = dots_of(p)
        inter = int((cand & m).sum())
        union = int((cand | m).sum())
        d_fwd = directed(cand, m)
        d_rev = directed(m, cand)
        d_fwd_kd = directed_kdtree(cand, m)
        both = footprint & (np.isfinite(arr) | np.isfinite(cand_arr))
        ca = np.nan_to_num(cand_arr)[both]
        ba = np.nan_to_num(arr)[both]
        rho = float(spearmanr(ca, ba).statistic) if np.ptp(ca) and np.ptp(ba) else 0.0
        rows.append(dict(site=site, owner_reported_score=score, file=p.name,
                         sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                         dots=int(m.sum()), dot_set_sha256=set_hash(m),
                         exact_duplicate=bool(set_hash(cand) == set_hash(m)),
                         shared_dots=inter, jaccard=inter / union if union else 0.0,
                         directed_3px_candidate_to_site=round(d_fwd, 4),
                         directed_3px_site_to_candidate=round(d_rev, 4),
                         directed_3px_kdtree_crosscheck=round(d_fwd_kd, 4),
                         spearman=round(rho, 4)))
        print(f"[novelty] {site:<10} score {score}  dots {int(m.sum()):>6}  "
              f"Jaccard {rows[-1]['jaccard']:.4f}  cand->site 3px {d_fwd:.4f}  "
              f"site->cand 3px {d_rev:.4f}  rho {rho:+.4f}", flush=True)

    # ---- re-verify the champion's construction from bytes ----
    d28 = ROOT / "data/inputs/gems24-h25-1-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"
    champion_dots = int(dots_of(BEST9["GEMSDOE32"][0] if Path(BEST9["GEMSDOE32"][0]).is_absolute() else ROOT / BEST9["GEMSDOE32"][0])[0].sum())
    recon = None
    if d28.exists():
        m28, _ = dots_of(d28)
        dist = ndi.distance_transform_edt(~catalogue)
        for r in (1, 2, 3):
            keep = m28 & ~(dist <= r)
            c32, _ = dots_of(BEST9["GEMSDOE32"][0] if Path(BEST9["GEMSDOE32"][0]).is_absolute() else ROOT / BEST9["GEMSDOE32"][0])
            sym = int((keep ^ c32).sum())
            print(f"[verify] d2-8 minus catalogue<={r}px -> {int(keep.sum())} dots; "
                  f"symmetric difference vs GEMSDOE32 = {sym}", flush=True)
        recon = dict(source=str(d28.relative_to(ROOT)), source_dots=int(m28.sum()),
                     champion_dots=champion_dots,
                     symmetric_difference_at_2px=None,
                     note="recomputed this session from the byte-verified d2-8 raster")

    worst = max((r for r in rows if "directed_3px_candidate_to_site" in r),
                key=lambda r: r["directed_3px_candidate_to_site"], default=None)
    out = dict(evidence_class="REGISTRY-MEASUREMENT",
               generated_utc=datetime.now(timezone.utc).isoformat(),
               candidate=dict(file=str(Path(a.candidate).resolve().relative_to(ROOT)),
                              sha256=hashlib.sha256(Path(a.candidate).resolve().read_bytes()).hexdigest(),
                              dots=int(cand.sum()), dot_set_sha256=set_hash(cand)),
               thresholds=dict(overlap_limit=0.70, rho_limit=0.90, radius_px=RADIUS_PX,
                               overlap_limit_source="user parallel-run protocol rule 1",
                               exact_duplicate_standard="user requirement: 'not an exact duplicate'"),
               per_site=rows,
               max_directed_3px=worst["directed_3px_candidate_to_site"] if worst else None,
               max_directed_3px_site=worst["site"] if worst else None,
               any_exact_duplicate=any(r.get("exact_duplicate") for r in rows),
               champion_reconstruction=recon)
    p = ROOT / a.out
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(f"[novelty] wrote {p}; max directed 3px = {out['max_directed_3px']} "
          f"({out['max_directed_3px_site']}); exact duplicate: {out['any_exact_duplicate']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
