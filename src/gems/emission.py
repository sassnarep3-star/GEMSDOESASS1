"""Emission: turn a continuous field into a sparse binary "dotted" prediction.

Why dots: with alpha=0.2, every emitted unit of mass that is not within 300 m of a new fault costs
0.2 in the denominator, while a truth pixel is credited by the *single best* prediction within
300 m. Emitting isolated pixels spaced ~2-3 px apart along a candidate trace keeps most of the
coverage of a solid line at a fraction of the FP mass (see knowledge/01 for the derivation of the
break-even rule k > 0.2*DTI for a single new dot on uncovered truth).

`poisson_disk_dots` greedily takes the highest-scoring pixels subject to a minimum spacing,
optionally excluding anything within `cat_prune_px` of the known catalogue (score-time masking
means a dot on a catalogue pixel is ignored, and a dot 1-2 px away is scored at full FP risk).
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage


def poisson_disk_dots(field: np.ndarray, allowed: np.ndarray, n_dots: int, min_dist_px: float,
                      max_candidates: int = 600_000) -> np.ndarray:
    """Greedy priority Poisson-disk sampling: highest field value first, reject within min_dist."""
    H, W = field.shape
    vals = np.where(allowed, field, -np.inf).ravel()
    order = np.argsort(-vals, kind="stable")[:max_candidates]
    order = order[np.isfinite(vals[order])]
    r = int(np.ceil(min_dist_px))
    occupied = np.zeros((H + 2 * r, W + 2 * r), bool)
    dy, dx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (dy * dy + dx * dx) < (min_dist_px * min_dist_px)
    out = np.zeros(H * W, bool)
    taken = 0
    for idx in order:
        y, x = divmod(int(idx), W)
        if occupied[y + r, x + r]:
            continue
        out[idx] = True
        occupied[y:y + 2 * r + 1, x:x + 2 * r + 1] |= disk
        taken += 1
        if taken >= n_dots:
            break
    return out.reshape(H, W)


def catalogue_exclusion(catalogue: np.ndarray, prune_px: float) -> np.ndarray:
    """Pixels farther than prune_px from any known catalogue pixel (allowed region)."""
    d = ndimage.distance_transform_edt(~catalogue)
    return d > prune_px
