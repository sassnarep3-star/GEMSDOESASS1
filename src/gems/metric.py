"""Distance-weighted Tversky Index (DTI) — the DOE GEMS Prize Challenge metric.

Source of the definition (official): DrivenData problem description, "Performance metric",
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
Parameters: alpha = 0.2 (false-positive weight), beta = 0.8 (false-negative weight),
triangular kernel k(d) = max(1 - d/R, 0) with R = 300 m = 3 pixels on the 100 m grid.

    TP_w = sum_{g in G} max_{x} p(x) * k(d(x, g))
    FP_w = sum_{x} p(x) * [1 - max_{g in G} k(d(x, g))]
    FN_w = sum_{g in G} [1 - max_{x} p(x) * k(d(x, g))]  =  |G| - TP_w
    DTI  = TP_w / (TP_w + alpha*FP_w + beta*FN_w + eps)

Known catalogue fault *pixels* are excluded from scoring (DrivenData staff, forum thread 11516:
https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516 ).
The `known` mask below implements that pixel-exact exclusion.

`dti_bruteforce` is an O(|G|*|P|) literal transcription used only by the unit tests to prove
`dti_exact` / `dti_binary` agree with the published equations.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

ALPHA = 0.2
BETA = 0.8
RADIUS_PX = 3.0
EPS = 1e-12


def kernel(d, radius: float = RADIUS_PX):
    return np.maximum(1.0 - np.asarray(d, dtype=np.float64) / radius, 0.0)


def _offsets(radius: float = RADIUS_PX):
    r = int(np.ceil(radius))
    out = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            k = float(kernel(np.hypot(dy, dx), radius))
            if k > 0.0:
                out.append((dy, dx, k))
    return out


_OFFS = _offsets()


def dti_from_counts(tp: float, fp: float, fn: float, alpha=ALPHA, beta=BETA) -> float:
    return float(tp / (tp + alpha * fp + beta * fn + EPS))


def dti_exact(pred, truth, active=None, alpha=ALPHA, beta=BETA) -> dict:
    """Exact DTI for soft predictions in [0, 1]. `active` = scored domain (footprint minus known pixels)."""
    pred = np.asarray(pred, dtype=np.float64)
    truth = np.asarray(truth, dtype=bool)
    active = np.ones(pred.shape, bool) if active is None else np.asarray(active, bool)
    p = np.where(active & np.isfinite(pred), pred, 0.0)
    if (p < 0).any() or (p > 1).any():
        raise ValueError("predictions must be in [0, 1]")
    g = truth & active
    H, W = p.shape
    yy, xx = np.nonzero(g)
    n = int(yy.size)
    if n == 0:
        return dict(tp=0.0, fp=float(p.sum()), fn=0.0, n_truth=0, dti=0.0)
    credit = np.zeros(n)
    for dy, dx, k in _OFFS:
        ny, nx = yy + dy, xx + dx
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        credit[ok] = np.maximum(credit[ok], p[ny[ok], nx[ok]] * k)
    tp = float(credit.sum())
    fn = float(n) - tp
    dg = distance_transform_edt(~g)
    fp = float((p * (1.0 - kernel(dg))).sum())
    return dict(tp=tp, fp=fp, fn=fn, n_truth=n, dti=dti_from_counts(tp, fp, fn, alpha, beta))


def dti_binary(pred_bool, truth, active=None, alpha=ALPHA, beta=BETA) -> dict:
    """Fast exact DTI for binary predictions via two Euclidean distance transforms."""
    p = np.asarray(pred_bool, bool)
    g = np.asarray(truth, bool)
    if active is not None:
        a = np.asarray(active, bool)
        p = p & a
        g = g & a
    n = int(g.sum())
    if n == 0:
        return dict(tp=0.0, fp=float(p.sum()), fn=0.0, n_truth=0, dti=0.0)
    if not p.any():
        return dict(tp=0.0, fp=0.0, fn=float(n), n_truth=n, dti=0.0)
    dp = distance_transform_edt(~p)
    tp = float(kernel(dp[g]).sum())
    fn = float(n) - tp
    dg = distance_transform_edt(~g)
    fp = float((1.0 - kernel(dg[p])).sum())
    return dict(tp=tp, fp=fp, fn=fn, n_truth=n, dti=dti_from_counts(tp, fp, fn, alpha, beta))


def dti_bruteforce(pred, truth, alpha=ALPHA, beta=BETA, radius=RADIUS_PX) -> dict:
    pred = np.asarray(pred, float)
    truth = np.asarray(truth, bool)
    gs = np.argwhere(truth)
    xs = np.argwhere(pred > 0)
    tp = 0.0
    for gy, gx in gs:
        best = 0.0
        for xy, xx_ in xs:
            best = max(best, pred[xy, xx_] * float(kernel(np.hypot(xy - gy, xx_ - gx), radius)))
        tp += best
    fp = 0.0
    for xy, xx_ in xs:
        best = 0.0
        for gy, gx in gs:
            best = max(best, float(kernel(np.hypot(xy - gy, xx_ - gx), radius)))
        fp += pred[xy, xx_] * (1.0 - best)
    fn = float(len(gs)) - tp
    return dict(tp=tp, fp=fp, fn=fn, n_truth=int(len(gs)), dti=dti_from_counts(tp, fp, fn, alpha, beta))
