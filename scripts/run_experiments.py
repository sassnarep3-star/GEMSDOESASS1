#!/usr/bin/env python3
"""Pre-registered experiments on the hide-and-recover holdout (evaluator GEMSASS1-HR-v1).

Bar (frozen before running): HOLDOUT-DTI of the un-pruned 0.2600 family base
`gems25-dotted-h19-5-d2-8` on this evaluator = 0.1011 [0.0956, 0.1072] (evidence/holdout_calibration.json).

  canary : every feature alone -> AUC on fold-0 withheld truth (AUC > 0.90 = leakage until proven otherwise)
  E1     : RFPD  range-front piedmont scarp dipole (rule-based, label-free; visible-catalogue gated)
  E2     : SWGB  segment-withheld gradient boosting (trained on withheld TRAIN segments, visible-only context)
  E3     : emission sweep on the better field (n_dots x spacing), then final build on the full catalogue

Usage: python3 scripts/run_experiments.py canary|e1|e2|e3
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.grid import load_footprint, load_catalogue, EVIDENCE, WORK          # noqa: E402
from gems.holdout import build_folds, catalogue_features, score_pooled, score_pooled_farfield, auc_binary, EVALUATOR_VERSION  # noqa: E402
from gems.features import build_static_features, add_catalogue_context, stack  # noqa: E402
from gems.emission import poisson_disk_dots                                     # noqa: E402

BAR = dict(name="gems25-dotted-h19-5-d2-8 (0.2600 family base, un-pruned)", holdout_dti=0.1011, ci95=[0.0956, 0.1072])
N_DOTS = 44_090
SPACING = 2.8
WORK.mkdir(exist_ok=True)
EVIDENCE.mkdir(exist_ok=True)


def rank01(a: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Rank-normalise inside mask to [0,1] (0 outside)."""
    out = np.zeros(a.shape, np.float32)
    v = a[mask]
    r = np.empty(v.size, np.float32)
    order = np.argsort(v, kind="stable")
    r[order] = np.arange(v.size, dtype=np.float32) / max(v.size - 1, 1)
    out[mask] = r
    return out


def context():
    foot, cat = load_footprint(), load_catalogue()
    folds, n_seg = build_folds(cat, foot)
    feats, lidar_valid = build_static_features()
    return foot, cat, folds, feats, lidar_valid


def canary():
    foot, cat, folds, feats, lidar_valid = context()
    fd = folds[0]
    catf = catalogue_features(fd.visible, foot)
    allf = add_catalogue_context(feats, catf)
    rows = {}
    dom = fd.active
    for n, a in allf.items():
        rows[n] = auc_binary(a[dom], fd.test_truth[dom])
        rows[n + "__neg"] = 1.0 - rows[n]
    flagged = {k: v for k, v in rows.items() if v > 0.90}
    out = dict(evaluator=EVALUATOR_VERSION, fold=0, n_withheld_positives=fd.n_test, auc=rows, flagged_over_0p90=flagged)
    (EVIDENCE / "leakage_canary.json").write_text(json.dumps(out, indent=2))
    for k, v in sorted(rows.items(), key=lambda kv: -kv[1])[:12]:
        print(f"  {k:28s} AUC={v:.3f}")
    print("flagged (>0.90):", flagged)


def e1_field(allf: dict, lidar_valid: np.ndarray, foot: np.ndarray) -> np.ndarray:
    """RFPD: paired crest-convexity/base-concavity scarp dipole, strike-parallel to the nearest visible
    fault (|dStrike| <= 30 deg), 300 m - 3 km from it (the piedmont / hanging-wall habitat of young
    basinward-stepping splays), weighted by along-strike coherence."""
    dist = np.expm1(allf["cat_logdist"])
    band = (dist >= 3) & (dist <= 30)
    parallel = allf["cat_strike_agree"] >= 0.5
    dip = rank01(allf["lidar_dipole"], foot & lidar_valid)
    asym = rank01(np.abs(allf["lidar_face_asym"]), foot & lidar_valid)
    coh = rank01(allf["lidar_coh100"], foot & lidar_valid)
    field = (0.5 * dip + 0.3 * asym + 0.2 * coh) * band * parallel * lidar_valid
    return field.astype(np.float32)


def run_e1():
    t0 = time.time()
    foot, cat, folds, feats, lidar_valid = context()
    dots_by_fold, fields = [], []
    for fd in folds:
        catf = catalogue_features(fd.visible, foot)
        allf = add_catalogue_context(feats, catf)
        field = e1_field(allf, lidar_valid, foot)
        fields.append(field.astype(np.float16))
        dots_by_fold.append(poisson_disk_dots(field, fd.active & (field > 0), N_DOTS, SPACING))
        print(f"  fold {fd.f}: dots={int(dots_by_fold[-1].sum())}", flush=True)
    s = score_pooled(dots_by_fold, folds)
    np.savez_compressed(WORK / "e1_fields.npz", *fields)
    out = dict(experiment="E1-RFPD", hypothesis="range-front piedmont scarp dipole", **s, bar=BAR,
               beats_bar=s["holdout_dti"] > BAR["holdout_dti"], n_dots=N_DOTS, spacing_px=SPACING, elapsed_s=round(time.time() - t0, 1))
    (EVIDENCE / "e1_rfpd_holdout.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: out[k] for k in ("holdout_dti", "ci95", "n_withheld_positives", "beats_bar")}))


FEATURE_NAMES = None


def run_e2(static_only: bool = False):
    """Memory-lean: features are flattened to footprint-only float16 vectors; prediction is chunked."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from scipy import ndimage
    t0 = time.time()
    foot, cat, folds, feats, lidar_valid = context()
    fidx = np.flatnonzero(foot.ravel())                  # footprint pixel ids
    static_names = sorted(feats.keys())
    flat = {n: feats[n].ravel()[fidx].astype(np.float16) for n in static_names}
    del feats
    ctx_names = ["cat_logdist", "cat_logtip", "cat_dens", "cat_strike_agree"]
    names = static_names + ([] if static_only else ctx_names)
    tag = "e2b_static" if static_only else "e2"
    rng = np.random.default_rng(7)
    dots_by_fold, fields = [], []
    pos_in_foot = np.zeros(foot.shape, bool)

    def rows(sel_flat_ids, flat_all):
        return np.stack([flat_all[n][sel_flat_ids] for n in names], axis=1).astype(np.float32)

    for fd in folds:
        catf = catalogue_features(fd.visible, foot)
        strike_deg = (flat["lidar_strike"].astype(np.float32) - 1.0) / 254.0 * 180.0
        flat_all = dict(flat)
        flat_all["cat_logdist"] = np.log1p(catf["dist_vis"].ravel()[fidx]).astype(np.float16)
        flat_all["cat_logtip"] = np.log1p(catf["tip_vis"].ravel()[fidx]).astype(np.float16)
        flat_all["cat_dens"] = catf["dens_vis"].ravel()[fidx].astype(np.float16)
        flat_all["cat_strike_agree"] = np.cos(2 * (np.deg2rad(strike_deg) - catf["strike_vis"].ravel()[fidx])).astype(np.float16)
        del catf
        guard = ndimage.binary_dilation(fd.test_truth, iterations=3)
        train_region = fd.active & ~guard
        pos = (fd.train_truth & train_region).ravel()[fidx]
        negpool = (train_region & ~ndimage.binary_dilation(fd.train_truth, iterations=2)).ravel()[fidx]
        neg_ids = rng.choice(np.flatnonzero(negpool), size=min(600_000, int(negpool.sum())), replace=False)
        pos_ids = np.flatnonzero(pos)
        X = np.vstack([rows(pos_ids, flat_all), rows(neg_ids, flat_all)])
        y = np.r_[np.ones(len(pos_ids)), np.zeros(len(neg_ids))]
        w = np.r_[np.full(len(pos_ids), len(neg_ids) / len(pos_ids)), np.ones(len(neg_ids))]
        clf = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.08, max_leaf_nodes=31, min_samples_leaf=100,
                                             l2_regularization=1.0, random_state=fd.f)
        clf.fit(X, y, sample_weight=w)
        del X
        act = fd.active.ravel()[fidx]
        act_ids = np.flatnonzero(act)
        prob = np.zeros(fidx.size, np.float32)
        for c in range(0, act_ids.size, 400_000):
            ch = act_ids[c:c + 400_000]
            prob[ch] = clf.predict_proba(rows(ch, flat_all))[:, 1]
        field = np.zeros(foot.size, np.float32); field[fidx] = prob; field = field.reshape(foot.shape)
        fields.append(field.astype(np.float16))
        dots_by_fold.append(poisson_disk_dots(field, fd.active, N_DOTS, SPACING))
        print(f"  fold {fd.f}: pos={len(pos_ids)} neg={len(neg_ids)} dots={int(dots_by_fold[-1].sum())} {time.time()-t0:.0f}s", flush=True)
        del flat_all, prob
    s = score_pooled(dots_by_fold, folds)
    ff = score_pooled_farfield(dots_by_fold, folds)
    np.savez_compressed(WORK / f"{tag}_fields.npz", *fields)
    out = dict(experiment="E2b-SWGB-static" if static_only else "E2-SWGB", hypothesis="segment-withheld supervised learner" + (" (no catalogue context)" if static_only else ""),
               features=names, **s, farfield=ff, bar=BAR,
               beats_bar=s["holdout_dti"] > BAR["holdout_dti"], n_dots=N_DOTS, spacing_px=SPACING, elapsed_s=round(time.time() - t0, 1))
    (EVIDENCE / f"{tag}_swgb_holdout.json".replace("e2_", "e2_")).write_text(json.dumps(out, indent=2))
    print("farfield:", json.dumps({k: ff[k] for k in ("holdout_dti", "ci95", "n_withheld_positives")}))
    print(json.dumps({k: out[k] for k in ("holdout_dti", "ci95", "n_withheld_positives", "beats_bar")}))


def run_e3(which: str):
    t0 = time.time()
    foot, cat, folds, feats, lidar_valid = context()
    z = np.load(WORK / f"{which}_fields.npz")
    fields = [z[f"arr_{i}"].astype(np.float32) for i in range(len(folds))]
    grid = []
    for n_dots in (30_000, 38_000, 44_090, 52_000, 60_000):
        for sp in (2.3, 2.8, 3.3):
            dots = [poisson_disk_dots(fl, fd.active & (fl > 0), n_dots, sp) for fl, fd in zip(fields, folds)]
            s = score_pooled(dots, folds, n_boot=100)
            grid.append(dict(n_dots=n_dots, spacing_px=sp, holdout_dti=s["holdout_dti"], ci95=s["ci95"]))
            print(f"  n={n_dots} sp={sp}: {s['holdout_dti']:.4f} [{s['ci95'][0]:.4f},{s['ci95'][1]:.4f}]", flush=True)
    best = max(grid, key=lambda g: g["holdout_dti"])
    out = dict(experiment="E3-emission-sweep", field=which, grid=grid, best=best, bar=BAR, elapsed_s=round(time.time() - t0, 1))
    (EVIDENCE / f"e3_emission_sweep_{which}.json").write_text(json.dumps(out, indent=2))
    print("best", best)


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"canary": canary, "e1": run_e1, "e2": run_e2, "e2b": lambda: run_e2(static_only=True)}.get(cmd, lambda: run_e3(sys.argv[2]))()
