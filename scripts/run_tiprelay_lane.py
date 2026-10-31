#!/usr/bin/env python3
"""H-TIPRELAY lane, session 2026-10-31 — preregistered in knowledge/hypotheses_20261031.md.

Lane paragraph (frozen): **H-TIPRELAY continuation-geometry-supervised recovery** — the H-TVGB
thermal-anchored segment-withheld HistGradientBoosting learner augmented with three new
VISIBLE-only catalogue-geometry feature families: (1) tip-relay corridors (opposing visible
skeleton endpoints whose along-strike projections meet across an uncatalogued gap), (2) step-over /
relay-ramp gaps (pixels 2-8 px off the visible trace between two strands offset in strike), and
(3) strike persistence (local circular resultant of the visible strike field), plus a far-field
training-emphasis arm (positives > 500 m from visible faults x3), emitted at the live-evidenced
champion operating point (n=37,654 dots, 2.8 px Poisson spacing, > 600 m catalogue exclusion);
geothermal-anchor emission prior tested as a paired emission ablation. Scored on the shared
GEMSASS1-HR-v2-segment holdout; gated by the frozen 414-raster registry novelty scan.

Shared tools reused, never forked: src/gems/holdout.py, src/gems/metric.py, src/gems/features.py,
src/gems/emission.py, src/gems/thermal.py, src/gems/submission.py, scripts/novelty.py,
vendor/gems57/submission_writer.py. All output goes to evidence/tiprelay/ (new evidence in new
directories; the frozen 2026-10-30 thermal lane is never overwritten).

Sandbox budget: 3 GB RAM / 2 cores — static and thermal features are flattened to float16 on the
footprint immediately and full-grid float32 stacks are released; relay features are built one fold
at a time and flattened the same way.

Usage: python scripts/run_tiprelay_lane.py canary|e1|e2|e3|final|all
  canary : per-feature leakage AUCs on fold 0 (gate, not an experiment)
  e1     : paired feature ablation  A=hvtgb repro / B=+relay / C=+farfield-weight   (experiment 1)
  e2     : paired emission ablation plain vs geothermal-anchor-modulated, winner arm (experiment 2)
  e3/final: full-catalogue rebuild + emission + novelty + writer + run card      (experiment 3)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT))

from gems.grid import load_footprint, load_catalogue, sha256_file, WORK  # noqa: E402
from gems.holdout import (build_folds, catalogue_features, score_pooled, score_pooled_farfield,  # noqa: E402
                          auc_binary, EVALUATOR_VERSION, _tile_contributions, dti_from_counts)
from gems.features import build_static_features  # noqa: E402
from gems.emission import poisson_disk_dots, catalogue_exclusion  # noqa: E402
from gems.thermal import load_anchor_points, build_thermal_features  # noqa: E402

OUT = ROOT / 'evidence' / 'tiprelay'
OUT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(exist_ok=True)

BAR = dict(name='gems25-dotted-h19-5-d2-8 (0.2600 family base, un-pruned)',
           holdout_dti=0.1011, ci95=[0.0956, 0.1072])
REPO_BEST = dict(name='H-TVGB b6 shipped 2026-10-30 (repo incumbent at the registered b6 cell)',
                 holdout_dti=0.1287, ci95=[0.1231, 0.1355])
N_DOTS_E1 = 44_090        # E2-comparable cell from the 2026-10-30 lane
N_SHIP = 37_654           # live-evidenced champion operating point (preregistered)
SPACING = 2.8
PRUNE_SHIP_PX = 6.0       # registered 600 m catalogue exclusion at emission
RELAY_NAMES = ['relay_corridor', 'relay_logdist', 'stepover_band', 'strike_persist', 'tip_align']
CTX_NAMES = ['cat_logdist', 'cat_logtip', 'cat_dens', 'cat_strike_agree']

GAP_MIN_PX = 6            # relay corridor: minimum gap between opposing tips
GAP_MAX_PX = 80           # relay corridor: maximum gap
RELAY_CONE_DEG = 26.2     # strike/segment agreement half-width (doubled-angle cosine 0.66)
STEP_BAND = (2.0, 8.0)    # step-over: off-trace distance band
STEP_OFFSETS = (4, 6, 8)  # step-over: strand-probe offsets either side (px)
N_BINS = 18               # step-over strike bins over [0, pi)
ARM_A = 'A_hvtgb_repro'
ARM_B = 'B_tiprelay'
ARM_C = 'C_tiprel_ff'


# --------------------------------------------------------------------- relay features
def _skeleton_tips(visible: np.ndarray):
    """Skeleton endpoints (8-neighbour count == 1). AMENDMENT 2026-10-31 (pre-E1, canary gate):
    the first implementation estimated each tip's outgoing direction from a 9x9 interior centroid
    and required the connecting segment to stay inside a 20 deg cone of BOTH endpoint directions;
    on the real fold-0 catalogue this accepted ZERO pairs (centroid directions are too noisy for
    oblique relay bridges). The corridor test now uses the shared visible-strike field AT the tips
    (doubled-angle, mod pi), which is the physical quantity 'the mapped trace points along the
    gap'. Fold-0 yield: 275 pairs. The lane hypothesis is unchanged; only the estimator is fixed."""
    from skimage.morphology import skeletonize
    from scipy import ndimage
    sk = skeletonize(visible)
    nb = ndimage.convolve(sk.astype(np.uint8), np.ones((3, 3), np.uint8), mode='constant') - sk
    tips = sk & (nb == 1)
    ty, tx = np.nonzero(tips)
    return sk, tips, np.stack([ty, tx], 1).astype(np.float64)


def relay_corridor_mask(visible: np.ndarray, tips_yx: np.ndarray, theta_tips: np.ndarray):
    """Accepted tip-to-tip relay segments (mutually strike-aligned across an open gap).

    Acceptance: both tips within RELAY_CONE_DEG of the connecting segment's bearing (doubled-angle
    cosine vs each tip's local strike, mod pi) AND the two tips' strikes mutually aligned within
    RELAY_CONE_DEG; the clearance test covers the OPEN gap only (first/last TRIM_PX samples
    excluded — the tip pixels themselves are visible-catalogue pixels)."""
    from scipy.spatial import cKDTree
    from skimage.draw import line as draw_line
    from scipy import ndimage
    H, W = visible.shape
    acc = np.zeros((H, W), np.int16)
    vis2 = ndimage.binary_dilation(visible, structure=np.ones((5, 5), bool))  # ~2 px clearance shell
    TRIM_PX = 3
    cone2 = float(np.cos(2 * np.deg2rad(RELAY_CONE_DEG)))
    n_pairs = 0
    if len(tips_yx) >= 2:
        tree = cKDTree(tips_yx)
        pairs = tree.query_pairs(GAP_MAX_PX, output_type='ndarray')
        for i, j in pairs:
            if j <= i:
                continue
            v = tips_yx[j] - tips_yx[i]
            d = float(np.hypot(*v))
            if d < GAP_MIN_PX + 2 * TRIM_PX:
                continue
            phi = float(np.arctan2(v[0], v[1]))
            if (np.cos(2 * (phi - theta_tips[i])) < cone2
                    or np.cos(2 * (phi - theta_tips[j])) < cone2
                    or np.cos(2 * (theta_tips[i] - theta_tips[j])) < cone2):
                continue  # not a strike-aligned relay across the gap
            rr, cc = draw_line(int(tips_yx[i][0]), int(tips_yx[i][1]),
                               int(tips_yx[j][0]), int(tips_yx[j][1]))
            if len(rr) <= 2 * TRIM_PX:
                continue
            rr_o, cc_o = rr[TRIM_PX:-TRIM_PX], cc[TRIM_PX:-TRIM_PX]
            # open gap: no visible pixel within ~2 px anywhere along the open segment
            if vis2[rr_o, cc_o].any():
                continue
            acc[rr_o, cc_o] += 1
            n_pairs += 1
    return acc, n_pairs


def relay_features(visible: np.ndarray, catf: dict, lidar_valid: np.ndarray, foot: np.ndarray):
    """The three continuation-geometry families. EVERYTHING derives from the VISIBLE fault mask
    of the current fold (or the full catalogue at inference) - never from hidden segments.
    Returns float32 full-grid arrays (caller flattens to float16 and releases)."""
    from scipy import ndimage
    H, W = visible.shape
    dist_vis = catf['dist_vis']
    strike = catf['strike_vis']
    _, tips, tips_yx = _skeleton_tips(visible)
    theta_tips = strike[tips_yx[:, 0].astype(int), tips_yx[:, 1].astype(int)]
    acc, n_pairs = relay_corridor_mask(visible, tips_yx, theta_tips)
    feats = {}
    corr_any = acc > 0
    feats['relay_corridor'] = ndimage.gaussian_filter(acc.astype(np.float32), 2.0).astype(np.float32)
    del acc
    feats['relay_logdist'] = np.log1p(ndimage.distance_transform_edt(~corr_any)).astype(np.float32)
    del corr_any
    # --- step-over band: off-trace pixel with visible strands on BOTH sides, offset in strike ---
    band = ((dist_vis >= STEP_BAND[0]) & (dist_vis <= STEP_BAND[1]))
    theta_bin = np.clip((strike / (np.pi / N_BINS)).astype(np.int8), 0, N_BINS - 1)
    both = np.zeros((H, W), bool)
    for b in range(N_BINS):
        sel = theta_bin == b
        if not sel.any():
            continue
        th = (b + 0.5) * (np.pi / N_BINS)
        ny, nx = -float(np.sin(th)), float(np.cos(th))   # unit normal to strand strike
        side_plus = np.zeros((H, W), bool)
        side_minus = np.zeros((H, W), bool)
        for off in STEP_OFFSETS:
            dy, dx = int(round(off * ny)), int(round(off * nx))
            sh_p = np.zeros((H, W), bool)
            ys0, ys1 = max(dy, 0), H + min(dy, 0)
            xs0, xs1 = max(dx, 0), W + min(dx, 0)
            sh_p[ys0:ys1, xs0:xs1] = visible[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
            side_plus |= sh_p
            sh_m = np.zeros((H, W), bool)
            ys0, ys1 = max(-dy, 0), H + min(-dy, 0)
            xs0, xs1 = max(-dx, 0), W + min(-dx, 0)
            sh_m[ys0:ys1, xs0:xs1] = visible[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx]
            side_minus |= sh_m
        both |= sel & side_plus & side_minus
    feats['stepover_band'] = (band & both).astype(np.float32)
    del band, both, theta_bin
    # --- strike persistence: local circular resultant of the doubled visible-strike angle ---
    c = ndimage.gaussian_filter(np.cos(2 * strike).astype(np.float32), 5.0)
    s = ndimage.gaussian_filter(np.sin(2 * strike).astype(np.float32), 5.0)
    feats['strike_persist'] = np.sqrt(c * c + s * s).astype(np.float32)
    del c, s
    # --- tip alignment: bearing to nearest visible tip along that tip's strike (mod pi) ---
    _, (iy, ix) = ndimage.distance_transform_edt(~tips, return_indices=True)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bearing = np.arctan2(iy.astype(np.float32) - yy, ix.astype(np.float32) - xx)
    del yy, xx
    tip_ang = strike[iy, ix]           # strike of the nearest visible tip (shared visible-strike field)
    d2 = np.cos(2 * (bearing - tip_ang))
    del bearing, tip_ang, iy, ix
    dist_tip = ndimage.distance_transform_edt(~tips)
    gate = (dist_tip >= 2.0) & (dist_tip <= 60.0)
    feats['tip_align'] = np.where(gate, np.maximum(d2, 0.0), 0.0).astype(np.float32)
    del d2, gate, dist_tip, tips
    lv = lidar_valid.astype(np.float32)
    for k in feats:
        feats[k] = (feats[k] * lv).astype(np.float32)
        feats[k][~foot] = 0.0
    meta = dict(n_tips=int(len(tips_yx)), n_relay_pairs=int(n_pairs),
                n_stepover_px=int((feats['stepover_band'] > 0).sum()))
    return feats, meta


# --------------------------------------------------------------------- context
def rank01(a: np.ndarray, mask: np.ndarray) -> np.ndarray:
    out = np.zeros(a.shape, np.float32)
    v = a[mask]
    r = np.empty(v.size, np.float32)
    order = np.argsort(v, kind='stable')
    r[order] = np.arange(v.size, dtype=np.float32) / max(v.size - 1, 1)
    out[mask] = r
    return out


def context():
    """Low-RAM context: static + thermal features flattened to float16 on the footprint."""
    t0 = time.time()
    foot, cat = load_footprint(), load_catalogue()
    folds, n_seg = build_folds(cat, foot)
    fidx = np.flatnonzero(foot.ravel())
    feats, lidar_valid = build_static_features()
    flat = {n: feats[n].ravel()[fidx].astype(np.float16) for n in sorted(feats.keys())}
    strike_grid = feats['lidar_strike'].copy()   # full-grid f32 needed by the thermal builder
    del feats
    anchors = load_anchor_points()
    th_feats, th_meta = build_thermal_features(anchors, strike_grid)
    del strike_grid, anchors
    flat_th = {n: th_feats[n].ravel()[fidx].astype(np.float16) for n in sorted(th_feats.keys())}
    del th_feats
    print(f'context ready: {n_seg} segments, {time.time()-t0:.1f}s', flush=True)
    return foot, cat, folds, flat, flat_th, th_meta, lidar_valid


def flatten_relay(rel: dict, fidx: np.ndarray) -> dict:
    return {n: rel[n].ravel()[fidx].astype(np.float16) for n in sorted(rel.keys())}


def ctx_flat(flat: dict, catf: dict, fidx: np.ndarray, strike_flat: dict) -> dict:
    """Visible-only catalogue context, flattened (same formula as gems.features.add_catalogue_context)."""
    out = {}
    out['cat_logdist'] = np.log1p(catf['dist_vis'].ravel()[fidx]).astype(np.float16)
    out['cat_logtip'] = np.log1p(catf['tip_vis'].ravel()[fidx]).astype(np.float16)
    out['cat_dens'] = catf['dens_vis'].ravel()[fidx].astype(np.float16)
    strike_deg = (strike_flat['lidar_strike'].astype(np.float32) - 1.0) / 254.0 * 180.0
    d = np.deg2rad(strike_deg) - catf['strike_vis'].ravel()[fidx]
    out['cat_strike_agree'] = np.cos(2 * d).astype(np.float16)
    return out


# --------------------------------------------------------------------- canary
def canary():
    foot, cat, folds, flat, flat_th, th_meta, lidar_valid = context()
    fd = folds[0]
    fidx = np.flatnonzero(foot.ravel())
    catf = catalogue_features(fd.visible, foot)
    rel, rel_meta = relay_features(fd.visible, catf, lidar_valid, foot)
    flat_rel = flatten_relay(rel, fidx)
    del rel
    base = dict(flat)
    base.update(ctx_flat(flat, catf, fidx, flat))
    base.update(flat_th)
    base.update(flat_rel)
    del catf
    act_ids = np.flatnonzero(fd.active.ravel()[fidx])
    truth_ids = fd.test_truth.ravel()[fidx]
    rows, flagged = {}, {}
    for name in sorted(base.keys()):
        auc = auc_binary(np.asarray(base[name][act_ids], np.float32), truth_ids[act_ids])
        rows[name] = auc
        if max(auc, 1 - auc) > 0.90:
            flagged[name] = auc
    out = dict(evaluator=EVALUATOR_VERSION, fold=0, n_withheld_positives=fd.n_test,
               relay_meta=rel_meta, thermal_meta=th_meta,
               new_feature_auc={k: rows[k] for k in RELAY_NAMES},
               auc_all=rows, flagged_over_0p90=flagged, canary_pass=not flagged,
               excluded_by_design=['dist_known_fault_px (label-derived column, never loaded)'])
    (OUT / 'leakage_canary.json').write_text(json.dumps(out, indent=2))
    print('new-feature AUCs:', {k: round(v, 3) for k, v in out['new_feature_auc'].items()})
    print('flagged (>0.90):', flagged)
    return out


# --------------------------------------------------------------------- E1 helpers
def _tile_stack(dots_a, dots_b, folds):
    tiles = []
    for fd, da, db in zip(folds, dots_a, dots_b):
        ta = np.concatenate([x.ravel() for x in _tile_contributions(da, fd.test_truth, fd.active)])
        tb = np.concatenate([x.ravel() for x in _tile_contributions(db, fd.test_truth, fd.active)])
        tiles.append((ta.reshape(3, -1), tb.reshape(3, -1)))
    A = np.concatenate([t[0] for t in tiles], axis=1)
    B = np.concatenate([t[1] for t in tiles], axis=1)
    rng2 = np.random.default_rng(11)
    live = np.nonzero((A.sum(0) + B.sum(0)) > 0)[0]
    deltas = []
    for _ in range(300):
        smp = rng2.choice(live, size=live.size, replace=True)
        deltas.append(dti_from_counts(*A[:, smp].sum(1)) - dti_from_counts(*B[:, smp].sum(1)))
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return [float(lo), float(hi)]


def load_fields(arm: str, n_folds: int = 5):
    z = np.load(WORK / f'tiprelay_{arm}_fields.npz')
    return [z[f'arr_{i}'].astype(np.float32) for i in range(n_folds)]


# --------------------------------------------------------------------- E1 (paired feature ablation)
def run_e1():
    from sklearn.ensemble import HistGradientBoostingClassifier
    from scipy import ndimage
    t0 = time.time()
    foot, cat, folds, flat, flat_th, th_meta, lidar_valid = context()
    fidx = np.flatnonzero(foot.ravel())
    static_names = sorted(flat.keys())
    th_names = sorted(flat_th.keys())
    rel_names = list(RELAY_NAMES)
    arms = {
        ARM_A: static_names + CTX_NAMES + th_names,
        ARM_B: static_names + CTX_NAMES + th_names + rel_names,
        ARM_C: static_names + CTX_NAMES + th_names + rel_names,   # same columns; different weights
    }
    rng = np.random.default_rng(7)
    results = {}
    dots_out = {arm: [] for arm in arms}
    rel_meta_by_fold = {}
    for fd in folds:
        catf = catalogue_features(fd.visible, foot)
        rel, rel_meta = relay_features(fd.visible, catf, lidar_valid, foot)
        rel_meta_by_fold[fd.f] = rel_meta
        flat_rel = flatten_relay(rel, fidx)
        del rel
        base = dict(flat)
        base.update(ctx_flat(flat, catf, fidx, flat))
        base.update(flat_th)
        base.update(flat_rel)
        del catf, flat_rel
        guard = ndimage.binary_dilation(fd.test_truth, iterations=3)
        train_region = fd.active & ~guard
        pos = (fd.train_truth & train_region).ravel()[fidx]
        negpool = (train_region & ~ndimage.binary_dilation(fd.train_truth, iterations=2)).ravel()[fidx]
        neg_ids = rng.choice(np.flatnonzero(negpool), size=min(600_000, int(negpool.sum())), replace=False)
        pos_ids = np.flatnonzero(pos)
        y = np.r_[np.ones(len(pos_ids)), np.zeros(len(neg_ids))]
        w_base = np.r_[np.full(len(pos_ids), len(neg_ids) / len(pos_ids)), np.ones(len(neg_ids))]
        for arm, names in arms.items():
            rows_sel = np.vstack([np.stack([base[n][ids] for n in names], axis=1)
                                  for ids in (pos_ids, neg_ids)]).astype(np.float32)
            if arm == ARM_C:
                # far-field emphasis: positive pixels >500 m (5 px) from VISIBLE faults weighted x3
                dv = base['cat_logdist'][pos_ids]  # log1p(dist px)
                w = w_base.copy()
                w[:len(pos_ids)] = np.where(dv > np.log1p(5.0), 3.0 * w_base[:len(pos_ids)], w_base[:len(pos_ids)])
            else:
                w = w_base
            clf = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.08, max_leaf_nodes=31,
                                                 min_samples_leaf=100, l2_regularization=1.0,
                                                 random_state=fd.f)
            clf.fit(rows_sel, y, sample_weight=w)
            del rows_sel
            act_ids = np.flatnonzero(fd.active.ravel()[fidx])
            prob = np.zeros(fidx.size, np.float32)
            for c in range(0, act_ids.size, 400_000):
                ch = act_ids[c:c + 400_000]
                prob[ch] = clf.predict_proba(np.stack([base[n][ch] for n in names], axis=1).astype(np.float32))[:, 1]
            field = np.zeros(foot.size, np.float32)
            field[fidx] = prob
            field = field.reshape(foot.shape)
            np.savez_compressed(WORK / f'tiprelay_{arm}_f{fd.f}.npz', field.astype(np.float32))
            dots = poisson_disk_dots(field, fd.active & (field > 0), N_DOTS_E1, SPACING)
            del field, prob
            dots_out[arm].append(dots)
            print(f'  fold {fd.f} {arm}: pos={len(pos_ids)} {time.time()-t0:.0f}s', flush=True)
        del base
    for arm in arms:
        s = score_pooled(dots_out[arm], folds)
        ff = score_pooled_farfield(dots_out[arm], folds)
        results[arm] = dict(holdout_dti=s['holdout_dti'], ci95=s['ci95'], farfield=ff['holdout_dti'],
                            farfield_ci95=ff['ci95'], per_fold=s['per_fold'])
        print(f'{arm}: {s["holdout_dti"]:.4f} [{s["ci95"][0]:.4f},{s["ci95"][1]:.4f}] farfield {ff["holdout_dti"]:.4f}', flush=True)
    # consolidate per-fold field npz into per-arm archives (work/ is gitignored scratch)
    for arm in arms:
        arrs = [np.load(WORK / f'tiprelay_{arm}_f{fd.f}.npz')['arr_0'] for fd in folds]
        np.savez_compressed(WORK / f'tiprelay_{arm}_fields.npz', *arrs)
        del arrs
        for fd in folds:
            (WORK / f'tiprelay_{arm}_f{fd.f}.npz').unlink()
    dBA_ci = _tile_stack(dots_out[ARM_B], dots_out[ARM_A], folds)
    dBA = float(results[ARM_B]['holdout_dti'] - results[ARM_A]['holdout_dti'])
    dCB_ci = _tile_stack(dots_out[ARM_C], dots_out[ARM_B], folds)
    dCB = float(results[ARM_C]['holdout_dti'] - results[ARM_B]['holdout_dti'])
    out = dict(experiment='E1-paired-tiprelay', hypothesis='relay/stepover/persistence features + far-field emphasis',
               evaluator=EVALUATOR_VERSION, n_withheld_positives=int(sum(f.n_test for f in folds)),
               arms=results, delta_B_minus_A=dict(value=dBA, ci95=dBA_ci),
               delta_C_minus_B=dict(value=dCB, ci95=dCB_ci),
               relay_meta_by_fold=rel_meta_by_fold, thermal_meta=th_meta,
               relay_features=rel_names, bar=BAR, repo_best=REPO_BEST,
               beats_bar=max(r['holdout_dti'] for r in results.values()) > BAR['holdout_dti'],
               n_dots=N_DOTS_E1, spacing_px=SPACING, elapsed_s=round(time.time() - t0, 1))
    (OUT / 'e1_paired_ablation.json').write_text(json.dumps(out, indent=2))
    print(json.dumps({'delta_B_minus_A': dBA, 'ci': dBA_ci, 'delta_C_minus_B': dCB, 'ci': dCB_ci,
                      'beats_bar': out['beats_bar']}))
    return out


def e1_winner(e1: dict) -> str:
    """Preregistered rule: B over A only if its paired 95% CI excludes 0; C over B the same way;
    otherwise stay with A."""
    best = ARM_A
    if e1['delta_B_minus_A']['ci95'][0] > 0:
        best = ARM_B
        if e1['delta_C_minus_B']['ci95'][0] > 0:
            best = ARM_C
    return best


# --------------------------------------------------------------------- E2 (paired emission ablation)
def run_e2(winner: str | None = None):
    t0 = time.time()
    e1 = json.loads((OUT / 'e1_paired_ablation.json').read_text())
    arm = winner or e1_winner(e1)
    foot, cat, folds, flat, flat_th, th_meta, lidar_valid = context()
    del flat, flat_th
    fidx = np.flatnonzero(foot.ravel())
    # anchor-density rank for the emission prior — rebuilt exactly as the shared thermal builder
    # constructs `th_anchor_dens` (gems.thermal.build_thermal_features), so the E2 prior is the
    # same label-free anchor-density field the learner saw, not a new instrument.
    from scipy import ndimage
    anchors = load_anchor_points()
    mass = (anchors['anchor'].astype(np.float32) + 0.5 * anchors['hot'].astype(np.float32)
            + 0.5 * anchors['paleo'].astype(np.float32))
    dens = ndimage.gaussian_filter(mass, 15.0).astype(np.float32)
    del mass, anchors
    anchor_rank = rank01(dens, foot)
    del dens
    fields = load_fields(arm)
    variants = {}
    dots_by_variant = {}
    for name, mod in (('plain', False), ('anchor_modulated', True)):
        dots = []
        for fl, fd in zip(fields, folds):
            f = fl
            if mod:
                f = rank01(fl, foot) * (0.8 + 0.2 * anchor_rank)
            allowed = fd.active & catalogue_exclusion(fd.visible, PRUNE_SHIP_PX) & (f > 0)
            dots.append(poisson_disk_dots(f, allowed, N_SHIP, SPACING))
        dots_by_variant[name] = dots
        s = score_pooled(dots, folds, n_boot=300)
        ff = score_pooled_farfield(dots, folds, n_boot=100)
        variants[name] = dict(holdout_dti=s['holdout_dti'], ci95=s['ci95'],
                              farfield=ff['holdout_dti'], farfield_ci95=ff['ci95'])
        print(f'{name}: {s["holdout_dti"]:.4f} [{s["ci95"][0]:.4f},{s["ci95"][1]:.4f}] farfield {ff["holdout_dti"]:.4f}', flush=True)
    dci = _tile_stack(dots_by_variant['anchor_modulated'], dots_by_variant['plain'], folds)
    dmod = float(variants['anchor_modulated']['holdout_dti'] - variants['plain']['holdout_dti'])
    out = dict(experiment='E2-emission-prior', hypothesis='geothermal anchor density as emission prior (NEXT_STEPS 4c)',
               winner_arm=arm, evaluator=EVALUATOR_VERSION, n_withheld_positives=int(sum(f.n_test for f in folds)),
               variants=variants, delta_modulated_minus_plain=dict(value=dmod, ci95=dci),
               shipped_cell=dict(n_dots=N_SHIP, spacing_px=SPACING, prune_px=PRUNE_SHIP_PX),
               bar=BAR, elapsed_s=round(time.time() - t0, 1))
    (OUT / 'e2_emission_ablation.json').write_text(json.dumps(out, indent=2))
    print(json.dumps(out['delta_modulated_minus_plain']))
    return out


# --------------------------------------------------------------------- E3 / final build
def read_tif(path):
    import rasterio
    with rasterio.open(path) as s:
        return s.read(1)


def final_build(arm: str | None = None, prune_px: float = PRUNE_SHIP_PX):
    """Retrain the fold models, predict with FULL-catalogue context, emit at the registered b6 cell,
    write the TIFF via the shared fail-closed writer, then novelty + validator audits."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from scipy import ndimage
    t0 = time.time()
    e1 = json.loads((OUT / 'e1_paired_ablation.json').read_text())
    arm = arm or e1_winner(e1)
    foot, cat, folds, flat, flat_th, th_meta, lidar_valid = context()
    fidx = np.flatnonzero(foot.ravel())
    static_names = sorted(flat.keys())
    th_names = sorted(flat_th.keys())
    rel_names = list(RELAY_NAMES)
    names = static_names + CTX_NAMES + th_names + rel_names

    # full-catalogue context for inference
    full_catf = catalogue_features(cat, foot)
    full_rel, full_rel_meta = relay_features(cat, full_catf, lidar_valid, foot)
    infer = dict(flat)
    infer.update(ctx_flat(flat, full_catf, fidx, flat))
    infer.update({n: full_rel[n].ravel()[fidx].astype(np.float16) for n in rel_names})
    infer.update(flat_th)
    del full_catf, full_rel

    rng = np.random.default_rng(7)
    prob_sum = np.zeros(fidx.size, np.float32)
    for fd in folds:
        catf = catalogue_features(fd.visible, foot)
        rel, _ = relay_features(fd.visible, catf, lidar_valid, foot)
        base = dict(flat)
        base.update(ctx_flat(flat, catf, fidx, flat))
        base.update({n: rel[n].ravel()[fidx].astype(np.float16) for n in rel_names})
        base.update(flat_th)
        del catf, rel
        guard = ndimage.binary_dilation(fd.test_truth, iterations=3)
        train_region = fd.active & ~guard
        pos = (fd.train_truth & train_region).ravel()[fidx]
        negpool = (train_region & ~ndimage.binary_dilation(fd.train_truth, iterations=2)).ravel()[fidx]
        neg_ids = rng.choice(np.flatnonzero(negpool), size=min(600_000, int(negpool.sum())), replace=False)
        pos_ids = np.flatnonzero(pos)
        X = np.vstack([np.stack([base[n][pos_ids] for n in names], axis=1),
                       np.stack([base[n][neg_ids] for n in names], axis=1)]).astype(np.float32)
        y = np.r_[np.ones(len(pos_ids)), np.zeros(len(neg_ids))]
        w = np.r_[np.full(len(pos_ids), len(neg_ids) / len(pos_ids)), np.ones(len(neg_ids))]
        if arm == ARM_C:
            dv = base['cat_logdist'][pos_ids]
            w[:len(pos_ids)] = np.where(dv > np.log1p(5.0), 3.0 * w[:len(pos_ids)], w[:len(pos_ids)])
        clf = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.08, max_leaf_nodes=31,
                                             min_samples_leaf=100, l2_regularization=1.0, random_state=fd.f)
        clf.fit(X, y, sample_weight=w)
        del X
        for c in range(0, fidx.size, 400_000):
            ch = slice(c, c + 400_000)
            prob_sum[ch] += clf.predict_proba(np.stack([infer[n][ch] for n in names], axis=1).astype(np.float32))[:, 1]
        print(f'  fold {fd.f} trained+predicted {time.time()-t0:.0f}s', flush=True)
    field = np.zeros(foot.size, np.float32)
    field[fidx] = prob_sum / len(folds)
    del prob_sum
    field = field.reshape(foot.shape)

    allowed = foot & catalogue_exclusion(cat, prune_px) & (field > 0)
    dots = poisson_disk_dots(field, allowed, N_SHIP, SPACING)
    pred = np.where(dots, 1.0, 0.0).astype(np.float32)
    del dots, allowed

    # ---------------- novelty: surface BEFORE placement, dots AFTER placement ----------------
    from scripts.novelty import audit as novelty_audit, canonical_hash
    inv = json.loads((ROOT / 'registry/focus_inventory.json').read_text())

    def cached_audit(prediction, stage, cache_name):
        cache = OUT / cache_name
        digest = canonical_hash(np.asarray(prediction, np.float32)[foot])
        if cache.exists():
            prev = json.loads(cache.read_text())
            if prev.get('candidate_values_sha256') == digest and prev.get('comparisons_complete'):
                print(f'novelty {stage}: reusing complete cached scan', flush=True)
                return prev
        res = novelty_audit(prediction, foot, inv, ROOT, ROOT / 'data/bridge/sample_submission.tif',
                            stage=stage, stop_on_duplicate=False)
        cache.write_text(json.dumps(res, default=str))
        return res

    surface = cached_audit(field, 'surface', 'novelty_surface.json')
    dots_audit = cached_audit(pred, 'dots', 'novelty_dots.json')

    def maxima(rows, exclude_lattice):
        sp, ov, worst = [], [], None
        for r in rows:
            if r.get('status') != 'compared':
                continue
            if exclude_lattice and 'lattice' in r.get('path', '').lower():
                continue
            if r.get('spearman') is not None:
                sp.append(r['spearman'])
            o = r.get('directed_overlap_within_3px')
            if o is not None:
                ov.append(o)
                if worst is None or o > worst[1]:
                    worst = (r.get('path'), o, r.get('spearman'))
        return dict(max_spearman=max(sp) if sp else None, max_overlap=max(ov) if ov else None, worst=worst)

    comp_surface = maxima(surface['comparisons'], exclude_lattice=True)
    comp_dots = maxima(dots_audit['comparisons'], exclude_lattice=True)
    full_dots = maxima(dots_audit['comparisons'], exclude_lattice=False)
    digest = canonical_hash(pred[foot])
    exact_dupes = [r['path'] for r in dots_audit['comparisons']
                   if r.get('canonical_values_sha256') == digest or r.get('exact_values_equal')]
    dots_audit['exact_duplicate'] = bool(exact_dupes)
    dots_audit['exact_duplicate_paths'] = exact_dupes
    lattice_rows = [dict(path=r.get('path'), spearman=r.get('spearman'),
                         overlap=r.get('directed_overlap_within_3px'))
                    for r in dots_audit['comparisons'] if 'lattice' in r.get('path', '').lower()]
    lane_drift_duplicate = ((comp_surface['max_spearman'] or 0) > 0.90
                            or (comp_dots['max_overlap'] or 0) > 0.70)

    # explicit uniqueness vs THIS repo's prior release (the 2026-10-30 H-TVGB b6 file)
    prior_vs = {}
    prior_path = ROOT / 'docs/downloads/gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif'
    if prior_path.exists():
        from vendor.gems57.uniqueness import dot_overlap
        prior = np.nan_to_num(read_tif(prior_path), nan=0.0)
        prior_vs = dict(path=prior_path.name,
                        directed_overlap_within_3px=float(dot_overlap(pred, prior)))
        del prior

    # ---------------- package via shared fail-closed writer ----------------
    from vendor.gems57.submission_writer import write_submission
    e2j = json.loads((OUT / 'e2_emission_ablation.json').read_text()) if (OUT / 'e2_emission_ablation.json').exists() else {}
    shipped_hold = e2j.get('variants', {}).get('plain', {})
    hold_val = shipped_hold.get('holdout_dti')
    note = (f"GEMSASS1 H-TIPRELAY tip-relay/stepover/persistence {int(pred.sum())}d "
            f">600m-offcat 2.8px; HOLDOUT-DTI "
            + (f"{hold_val:.4f}" if hold_val is not None else "n/a") + " vs bar 0.101")
    name = f"gemsass1-tiprelay-continuation-{int(pred.sum())}-b6-20261031"
    dest = ROOT / 'docs' / 'downloads'
    tif_path = dest / f"{name}-zeros.tif"
    write_submission(tif_path, pred, ROOT / 'data/bridge/sample_submission.tif', foot,
                     note=note, name=name, catalogue=cat,
                     metadata=dict(hypothesis='H-TIPRELAY continuation-geometry supervised recovery',
                                   evaluator=EVALUATOR_VERSION, arm=arm,
                                   n_dots=int(pred.sum()), spacing_px=SPACING, prune_px=prune_px))
    from gems.submission import validate
    v = validate(tif_path, foot, cat)
    sha = sha256_file(tif_path)

    # ---------------- run card ----------------
    hold = e1['arms'][arm]
    card = dict(
        schema='gemsass1.run_card.v3', generated_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        hypothesis='H-TIPRELAY: uncatalogued fault continuations concentrate where visible traces end in mutually facing tips (relay corridors), between offset parallel strands (step-over gaps), and beyond straight (persistent) traces; a segment-withheld learner carrying these VISIBLE-only continuation-geometry families recovers hidden segments better than the thermal-anchored baseline.',
        mechanism=f'5 x HistGradientBoosting (250 it) on 28 GeoDAWN/lidar layers + visible-only catalogue context + 10 thermal-anchor features + 5 relay-geometry features ({",".join(rel_names)}); fold models averaged with full-catalogue context; Poisson-disk 2.8 px, n={N_SHIP}, >600 m catalogue exclusion at emission (registered b6 cell).',
        named_non_fault_mimic='Pluvial shoreline benches and fluvial terrace risers (straight, coherent, can bridge between real scarps); road/canal embankments; magma-dike margins (persistent strike, step-over-like offsets).',
        arm=arm,
        holdout_dti=dict(label='HOLDOUT-DTI', evaluator=EVALUATOR_VERSION,
                         value=hold['holdout_dti'], ci95=hold['ci95'],
                         farfield_true_gt500m_from_visible=hold['farfield'],
                         n_withheld_positives=e1['n_withheld_positives'],
                         delta_B_minus_A=e1['delta_B_minus_A'], delta_C_minus_B=e1['delta_C_minus_B'],
                         shipped_cell_emission=shipped_hold,
                         e2_emission=e2j.get('delta_modulated_minus_plain'),
                         bar=BAR, repo_best=REPO_BEST),
        correlation_overlap_vs_registry=dict(
            surface_competitive=comp_surface, dots_competitive=comp_dots, dots_full_registry=full_dots,
            thresholds=dict(spearman=0.90, overlap=0.70, px=3),
            lane_drift_duplicate=bool(lane_drift_duplicate),
            lattice_rows=lattice_rows,
            prior_repo_release_overlap=prior_vs,
            ir_lattice_01='evidence/thermal/lattice_amendment.md'),
        raster_sha256=sha, raster_name=tif_path.name,
        validator_output=v, submission_name=name,
        note=note, note_length=len(note),
        verdict='promote' if (hold['holdout_dti'] > BAR['holdout_dti'] and not lane_drift_duplicate) else 'negative',
        ok_to_download_and_submit=bool(v['all_checks_passed'] and not lane_drift_duplicate and not exact_dupes
                                       and hold['holdout_dti'] > BAR['holdout_dti']),
        submission_slots_used=0,
        evidence_class=dict(holdout='HOLDOUT-DTI', live_scores='OWNER-REPORT (no organizer receipt in this group)'),
        experiments_run=3, experiment_budget=3, elapsed_s=round(time.time() - t0, 1),
        relay_meta_full_catalogue=full_rel_meta,
        limitations=[
            'No organizer receipt: every historical score is OWNER-REPORT, never ORGANIZER-CONFIRMED.',
            'HOLDOUT-DTI is not a leaderboard forecast (proxy-live Spearman -0.08 over the 17-file family).',
            'IR-LATTICE-01: the 13gems calibration lattice covers >=99% of any dotted file at 3 px; both readings are reported.',
            'Registry scope = nine public focus repos (414 TIFF blobs, frozen 2026-10-27 pins) + this repo prior release; global novelty unverified.',
        ])
    (OUT / 'run_card.json').write_text(json.dumps(card, indent=2, default=str))

    # ---------------- release.json: gates + estimate for the generated site ----------------
    gates = [
        ('Validator: values in [0,1], no NaN anywhere, exact competition grid', bool(v['all_checks_passed'])),
        ('Not an exact duplicate of any registry raster or prior repo file', not exact_dupes),
        ('Lane-drift gate vs competitive registry (Spearman ≤ 0.90, 3 px overlap ≤ 70%)', not lane_drift_duplicate),
        (f"HOLDOUT-DTI beats the 0.2600-family bar (0.1011): E1 arm {hold['holdout_dti']:.4f}; shipped b6 cell {shipped_hold.get('holdout_dti', float('nan')):.4f}",
         bool(hold['holdout_dti'] > BAR['holdout_dti'] and (hold_val is None or hold_val > BAR['holdout_dti']))),
        ('Zero positive mass on mapped catalogue faults', bool(v['checks'].get('zero_mass_on_known_catalogue_pixels', False))),
        ('No weekly submission slot used by this workspace', card['submission_slots_used'] == 0),
    ]
    bar_v = BAR['holdout_dti']
    ff = hold['farfield']
    hv = hold['holdout_dti']
    shv = hold_val if hold_val is not None else float('nan')
    est = (
        f"ESTIMATE (low confidence, projection — NOT a score): live score may land near "
        f"<strong>0.22–0.34</strong>. Family anchors: the 0.2600 live champion family measures {bar_v:.4f} on this "
        f"holdout and the 0.2778 champion is its pruned subset; this file measures {hv:.4f} pooled "
        f"(far-field {ff:.4f}; shipped-cell emission {shv:.4f}) at the champion operating point. "
        f"No local instrument is calibrated to the live task (holdout↔live Spearman −0.08 over 17 rasters), "
        f"so this range is advisory only.")
    release = dict(card=card, gates=gates, estimate_text=est, e1=e1, e2=e2j,
                   validator=v, novelty=dict(surface=comp_surface, dots=comp_dots,
                                             dots_full_registry=full_dots, lattice_rows=lattice_rows,
                                             prior_repo_release_overlap=prior_vs))
    (OUT / 'release.json').write_text(json.dumps(release, indent=2, default=str))
    print(json.dumps({k: card[k] for k in ('raster_sha256', 'verdict', 'ok_to_download_and_submit')}))
    return card


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    steps = ['canary', 'e1', 'e2', 'final'] if cmd == 'all' else [cmd]
    for s in steps:
        if s == 'canary':
            canary()
        elif s == 'e1':
            run_e1()
        elif s == 'e2':
            run_e2(*(sys.argv[2:3] or [None]))
        elif s in ('e3', 'final'):
            final_build(*(sys.argv[2:3] or [None]))
        else:
            raise SystemExit(f'unknown step {s}')
