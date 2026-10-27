"""Registry of previously scored GEMSDOE rasters (9 focus sites) and the lane/uniqueness audit.

Scores are OWNER-REPORT (copied from the sibling site ledgers quoted in the project brief); the
rasters are the exact files published in each site's docs/downloads/. Uniqueness rules
(PARALLEL-RUN PROTOCOL §1): a candidate is a duplicate if its Spearman rank-correlation with any
registry raster exceeds 0.90 on the footprint, OR more than 70% of its dots fall within 3 px of
one registry raster's dots.
"""
from __future__ import annotations

import json

import numpy as np
from scipy import ndimage
from scipy.stats import spearmanr

from .grid import REGISTRY, binary_dots, sha256_file, read_band

# site, published file, owner-reported live score
REGISTRY_ENTRIES = [
    ("GEMSDOE24", "gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif", 0.2477),
    ("GEMSDOE24", "gems24-gvc1-negative-geothermal-lineament-submod-20261025-abe8e51c719d-zeros.tif", 0.0859),
    ("GEMSDOE25", "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif", 0.2600),
    ("GEMSDOE25", "gems25-h66-mgd-flank-sapd3-0-k3p5-20261025-da617550a0e9-zeros.tif", 0.0742),
    ("GEMSDOE27", "gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif", 0.2449),
    ("GEMSDOE27", "gems27-h29-hydrothermal-piedmont-celf-20261025-511898747886-allfinite.tif", 0.2190),
    ("GEMSDOE28", "gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan.tif", 0.2708),
    ("GEMSDOE28", "gems28-h32-1-prethin-tip-euler-d2-8-20261003-31e35eee884e-nan.tif", 0.2649),
    ("GEMSDOE28", "gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif", 0.2710),
    ("GEMSDOE28", "gems28-h38-1-hf-euler-r30-r1-20261003-56a9f473edc7-nan.tif", 0.2707),
    ("GEMSDOE28", "gems28-s18-mxtp-20261025-3e95505c011a-allfinite.tif", 0.0217),
    ("GEMSDOE30", "gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif", 0.2600),
    ("GEMSDOE30", "gems30-MSDB1-edge44090-20261025-e7856ec3f14a.tif", 0.1462),
    ("GEMSDOE31", "gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif", 0.2708),
    ("GEMSDOE32", "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif", 0.2778),
    ("GEMSDOE33", "GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif", 0.2632),
    ("GEMSDOE36", "gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif", 0.2750),
]

RANK_CORR_MAX = 0.90
DOT_OVERLAP_MAX = 0.70
OVERLAP_PX = 3


def load_registry():
    out = []
    for site, fn, score in REGISTRY_ENTRIES:
        p = REGISTRY / fn
        if not p.exists():
            continue
        a = read_band(p)
        out.append(dict(site=site, file=fn, score=score, path=p, field=np.nan_to_num(a, nan=0.0),
                        dots=binary_dots(p), sha256=sha256_file(p)))
    return out


def lane_audit(candidate_field: np.ndarray, candidate_dots: np.ndarray, footprint: np.ndarray,
               registry=None, sample: int = 400_000, seed: int = 0) -> dict:
    registry = load_registry() if registry is None else registry
    rng = np.random.default_rng(seed)
    fy, fx = np.nonzero(footprint)
    sel = rng.choice(fy.size, size=min(sample, fy.size), replace=False)
    cf = np.nan_to_num(candidate_field, nan=0.0)[fy[sel], fx[sel]]
    rows = []
    n_dots = int(candidate_dots.sum())
    for r in registry:
        rf = r["field"][fy[sel], fx[sel]]
        rho = spearmanr(cf, rf).correlation if np.std(rf) > 0 and np.std(cf) > 0 else 0.0
        d = ndimage.distance_transform_edt(~r["dots"])
        within = float((d[candidate_dots] <= OVERLAP_PX).sum() / max(n_dots, 1))
        rows.append(dict(site=r["site"], file=r["file"], owner_reported_score=r["score"],
                         spearman=float(0.0 if rho is None or np.isnan(rho) else rho),
                         frac_dots_within_3px=within, registry_dots=int(r["dots"].sum()),
                         duplicate=bool((rho is not None and rho > RANK_CORR_MAX) or within > DOT_OVERLAP_MAX)))
    worst_rho = max((x["spearman"] for x in rows), default=0.0)
    worst_ov = max((x["frac_dots_within_3px"] for x in rows), default=0.0)
    return dict(n_candidate_dots=n_dots, max_spearman=worst_rho, max_frac_dots_within_3px=worst_ov,
                is_duplicate=any(x["duplicate"] for x in rows), thresholds=dict(spearman=RANK_CORR_MAX, overlap=DOT_OVERLAP_MAX, px=OVERLAP_PX),
                rows=rows)
