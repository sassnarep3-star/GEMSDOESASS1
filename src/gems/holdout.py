"""Hide-and-recover holdout (evaluator GEMSASS1-HR-v1).

Protocol (fixed before any experiment was run):
  * Segments = 8-connected components of the known catalogue raster (existing_faults.tif == 1).
  * Segments are assigned to K=5 folds by a seeded random draw per segment (v2). v1 grouped segments
    by 20 km tile; that made every withheld truth pixel far from any visible fault (canary: distance
    to visible had AUC 0.626 in the wrong direction), which does not mimic the live task where new
    faults are interleaved with catalogued ones. Whole segments + a 3 px buffer are still withheld.
  * For fold f: TEST truth  = pixels of fold-f segments.
                TRAIN truth = pixels of fold-((f+1) mod K) segments (used only by supervised lanes).
                VISIBLE     = catalogue minus (test ∪ train) segments.
                BUFFER      = pixels within BUFFER_PX of a hidden segment that are visible faults
                              are also removed from VISIBLE and excluded from scoring.
    Every catalogue-derived feature is computed from VISIBLE only (`catalogue_features`).
  * Scoring domain for fold f: footprint & ~VISIBLE (pixel-exact mask, as the organizer does for
    known faults) & ~BUFFER-excluded. Pooled DTI = DTI(sum TP, sum FP, sum FN) over the 5 folds.
  * 95% CI: block bootstrap over 50x50-pixel tiles of the per-tile (TP, FP, FN) contributions.

The withheld positives of the *test* side are the number reported with every HOLDOUT-DTI figure.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage

from .metric import ALPHA, BETA, dti_from_counts, kernel

EVALUATOR_VERSION = "GEMSASS1-HR-v2-segment"
K_FOLDS = 5
BUFFER_PX = 3
TILE_PX = 50
BLOCK_M = None   # v1 used 20 km tiles (see evidence/holdout_calibration_v1_tiles.json); v2 = whole segments
SEED = 20261027


@dataclass
class Fold:
    f: int
    visible: np.ndarray      # bool HxW
    test_truth: np.ndarray   # bool HxW
    train_truth: np.ndarray  # bool HxW
    active: np.ndarray       # bool HxW scoring domain
    n_test: int


def segment_folds(catalogue: np.ndarray, k: int = K_FOLDS, seed: int = SEED):
    lab, n = ndimage.label(catalogue, structure=np.ones((3, 3), int))
    idx = np.arange(1, n + 1)
    cy = ndimage.mean(np.indices(catalogue.shape)[0], lab, idx)
    cx = ndimage.mean(np.indices(catalogue.shape)[1], lab, idx)
    rng = np.random.default_rng(seed)
    if BLOCK_M is None:
        fold_of_seg = rng.integers(0, k, size=n).astype(np.int64)
    else:
        ty = (np.asarray(cy) * 100.0 // BLOCK_M).astype(np.int64)
        tx = (np.asarray(cx) * 100.0 // BLOCK_M).astype(np.int64)
        tiles = {}
        for a, b in zip(ty.tolist(), tx.tolist()):
            if (a, b) not in tiles:
                tiles[(a, b)] = int(rng.integers(0, k))
        fold_of_seg = np.array([tiles[(a, b)] for a, b in zip(ty.tolist(), tx.tolist())], dtype=np.int64)
    fold_map = np.full(catalogue.shape, -1, np.int8)
    fold_map[catalogue] = fold_of_seg[lab[catalogue] - 1]
    return fold_map, n


def build_folds(catalogue: np.ndarray, footprint: np.ndarray, k: int = K_FOLDS, seed: int = SEED):
    fold_map, n_seg = segment_folds(catalogue, k, seed)
    folds = []
    for f in range(k):
        test = fold_map == f
        train = fold_map == ((f + 1) % k)
        hidden = test | train
        near_hidden = ndimage.binary_dilation(hidden, iterations=BUFFER_PX)
        buffer_excl = catalogue & near_hidden & ~hidden
        visible = catalogue & ~hidden & ~buffer_excl
        active = footprint & ~visible & ~buffer_excl
        folds.append(Fold(f, visible, test & footprint, train & footprint, active, int((test & footprint).sum())))
    return folds, n_seg


def catalogue_features(visible: np.ndarray, footprint: np.ndarray) -> dict:
    """Catalogue-derived features computed from VISIBLE faults only.

    dist_vis   : Euclidean distance (px) to the nearest visible fault pixel
    strike_vis : strike (radians, mod pi) of the nearest visible fault, from a sigma=2 structure tensor
    tip_vis    : distance (px) to the nearest visible-segment end point (skeleton endpoints)
    dens_vis   : visible fault density in a sigma=15 px (1.5 km) Gaussian window
    """
    dist, (iy, ix) = ndimage.distance_transform_edt(~visible, return_indices=True)
    sm = ndimage.gaussian_filter(visible.astype(np.float32), 2.0)
    gy = ndimage.sobel(sm, axis=0)
    gx = ndimage.sobel(sm, axis=1)
    jxx = ndimage.gaussian_filter(gx * gx, 2.0)
    jyy = ndimage.gaussian_filter(gy * gy, 2.0)
    jxy = ndimage.gaussian_filter(gx * gy, 2.0)
    # gradient orientation of the fault raster; strike is perpendicular to the gradient
    theta_grad = 0.5 * np.arctan2(2 * jxy, jxx - jyy)
    strike_at_fault = (theta_grad + np.pi / 2) % np.pi
    strike_vis = strike_at_fault[iy, ix]
    # skeleton endpoints as tips
    from skimage.morphology import skeletonize
    sk = skeletonize(visible)
    nb = ndimage.convolve(sk.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - sk
    tips = sk & (nb == 1)
    tip_vis = ndimage.distance_transform_edt(~tips) if tips.any() else np.full(visible.shape, 1e4)
    dens_vis = ndimage.gaussian_filter(visible.astype(np.float32), 15.0)
    return dict(dist_vis=dist.astype(np.float32), strike_vis=strike_vis.astype(np.float32),
                tip_vis=tip_vis.astype(np.float32), dens_vis=dens_vis.astype(np.float32))


def _tile_contributions(pred_bool: np.ndarray, truth: np.ndarray, active: np.ndarray):
    p = pred_bool & active
    g = truth & active
    H, W = p.shape
    ty = np.arange(H) // TILE_PX
    tx = np.arange(W) // TILE_PX
    nty, ntx = ty.max() + 1, tx.max() + 1
    tile_id = (ty[:, None] * ntx + tx[None, :])
    n_tiles = nty * ntx
    tp = np.zeros(n_tiles)
    fn = np.zeros(n_tiles)
    fp = np.zeros(n_tiles)
    if g.any():
        dp = ndimage.distance_transform_edt(~p) if p.any() else np.full(p.shape, 1e4)
        credit = kernel(dp[g])
        np.add.at(tp, tile_id[g], credit)
        np.add.at(fn, tile_id[g], 1.0 - credit)
    if p.any():
        dg = ndimage.distance_transform_edt(~g) if g.any() else np.full(p.shape, 1e4)
        np.add.at(fp, tile_id[p], 1.0 - kernel(dg[p]))
    return tp, fp, fn


def score_pooled(preds_by_fold, folds, n_boot: int = 300, seed: int = 0) -> dict:
    """preds_by_fold: list of binary HxW predictions, one per fold (may be the same array)."""
    tps, fps, fns = [], [], []
    per_fold = []
    for pb, fd in zip(preds_by_fold, folds):
        tp, fp, fn = _tile_contributions(pb, fd.test_truth, fd.active)
        tps.append(tp); fps.append(fp); fns.append(fn)
        per_fold.append(dict(fold=fd.f, n_test=fd.n_test, tp=float(tp.sum()), fp=float(fp.sum()),
                             fn=float(fn.sum()), dti=dti_from_counts(tp.sum(), fp.sum(), fn.sum()),
                             emitted=int((pb & fd.active).sum())))
    TP = np.concatenate(tps); FP = np.concatenate(fps); FN = np.concatenate(fns)
    pooled = dti_from_counts(TP.sum(), FP.sum(), FN.sum())
    rng = np.random.default_rng(seed)
    live = np.nonzero((TP + FP + FN) > 0)[0]
    boots = []
    for _ in range(n_boot):
        s = rng.choice(live, size=live.size, replace=True)
        boots.append(dti_from_counts(TP[s].sum(), FP[s].sum(), FN[s].sum()))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return dict(evaluator=EVALUATOR_VERSION, holdout_dti=float(pooled), ci95=[float(lo), float(hi)],
                n_withheld_positives=int(sum(f.n_test for f in folds)),
                tp=float(TP.sum()), fp=float(FP.sum()), fn=float(FN.sum()), per_fold=per_fold)


def auc_binary(score: np.ndarray, truth: np.ndarray, sample: int = 400_000, seed: int = 0) -> float:
    """Rank AUC of a per-pixel score for truth vs background (used by the leakage canary)."""
    rng = np.random.default_rng(seed)
    pos = score[truth]
    neg = score[~truth]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    if neg.size > sample:
        neg = rng.choice(neg, sample, replace=False)
    if pos.size > sample:
        pos = rng.choice(pos, sample, replace=False)
    from scipy.stats import rankdata
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[:pos.size].sum() - pos.size * (pos.size + 1) / 2) / (pos.size * neg.size))


FARFIELD_PX = 5


def score_pooled_farfield(preds_by_fold, folds, min_dist_px: int = FARFIELD_PX, n_boot: int = 100) -> dict:
    """Same pooled DTI, but truth AND scoring domain restricted to pixels > min_dist_px from the fold's
    VISIBLE faults. Diagnostic for the live regime: the catalogue-flank raster h66 (dots 3-15 px from
    the catalogue) scored 0.0742 live while the 0.2778 file has a median catalogue distance of ~20 px,
    so near-visible credit on the holdout must not be mistaken for live credit."""
    sub = []
    for fd in folds:
        far = ndimage.distance_transform_edt(~fd.visible) > min_dist_px
        sub.append(Fold(fd.f, fd.visible, fd.test_truth & far, fd.train_truth, fd.active & far, int((fd.test_truth & far).sum())))
    out = score_pooled(preds_by_fold, sub, n_boot=n_boot)
    out["evaluator"] = EVALUATOR_VERSION + f"-farfield>{min_dist_px}px"
    return out
