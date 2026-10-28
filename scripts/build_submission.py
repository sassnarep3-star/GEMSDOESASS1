#!/usr/bin/env python3
"""Build the final unique submission from the promoted lane (E2-SWGB) and audit it automatically.

Pipeline (no human step):
  1. Five segment-withheld gradient-boosting models (one per holdout fold, exactly as in E2).
  2. Inference with the FULL catalogue as visible context; the 5 probability fields are averaged.
  3. Emission: Poisson-disk dots (2.8 px) from the averaged field, restricted to pixels > 2 px from
     any known catalogue pixel (exclusion radius 6 px = 600 m, applied BEFORE placement; chosen on the prune sweep).
  4. Lane audit vs the 17-raster registry (Spearman <= 0.90 and <= 70% dots within 3 px) — stop if duplicate.
  5. Validator (CRS/shape/transform == template, float32, no NaN/Inf anywhere, values in [0,1],
     zeros outside footprint, zero mass on catalogue pixels) — refuses to write a failing file.
  6. Writes swgb/downloads/<name>-zeros.tif, .zip, .checks.json and evidence/run_card.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.grid import load_footprint, load_catalogue, EVIDENCE, WORK, DOWNLOADS, sha256_file  # noqa: E402
from gems.holdout import build_folds, catalogue_features, EVALUATOR_VERSION                # noqa: E402
from gems.features import build_static_features                                            # noqa: E402
from gems.emission import poisson_disk_dots, catalogue_exclusion                           # noqa: E402
from gems.registry import lane_audit                                                       # noqa: E402
from gems.submission import write_submission                                               # noqa: E402

N_DOTS = 44_090
SPACING = 2.8
PRUNE_PX = 6.0   # chosen by evidence/e3_prune_sweep_e2.json: lane overlap 0.578 < 0.70, HOLDOUT-DTI 0.1401
STAMP = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def main():
    # This legacy builder compared only 17 published top files, omitting the pinned
    # GEMSDOE24 calibration lattice. Its existing output fails 44,033/44,090
    # dots within 3 px (>70%). Do not regenerate/write a purportedly approved TIFF.
    # See evidence/swgb/lattice_correction.json and scripts/audit_swgb_lattice.py.
    raise SystemExit('BLOCKED: historical SWGB lane duplicates the expanded registry; no new submission may be written')
    from sklearn.ensemble import HistGradientBoostingClassifier
    t0 = time.time()
    foot, cat = load_footprint(), load_catalogue()
    folds, n_seg = build_folds(cat, foot)
    feats, lidar_valid = build_static_features()
    fidx = np.flatnonzero(foot.ravel())
    static_names = sorted(feats.keys())
    flat = {n: feats[n].ravel()[fidx].astype(np.float16) for n in static_names}
    del feats
    ctx_names = ["cat_logdist", "cat_logtip", "cat_dens", "cat_strike_agree"]
    names = static_names + ctx_names
    strike_deg = (flat["lidar_strike"].astype(np.float32) - 1.0) / 254.0 * 180.0

    def ctx(visible):
        c = catalogue_features(visible, foot)
        d = dict(flat)
        d["cat_logdist"] = np.log1p(c["dist_vis"].ravel()[fidx]).astype(np.float16)
        d["cat_logtip"] = np.log1p(c["tip_vis"].ravel()[fidx]).astype(np.float16)
        d["cat_dens"] = c["dens_vis"].ravel()[fidx].astype(np.float16)
        d["cat_strike_agree"] = np.cos(2 * (np.deg2rad(strike_deg) - c["strike_vis"].ravel()[fidx])).astype(np.float16)
        return d

    def rows(ids, d):
        return np.stack([d[n][ids] for n in names], axis=1).astype(np.float32)

    rng = np.random.default_rng(7)
    models = []
    for fd in folds:
        d = ctx(fd.visible)
        guard = ndimage.binary_dilation(fd.test_truth, iterations=3)
        train_region = fd.active & ~guard
        pos_ids = np.flatnonzero((fd.train_truth & train_region).ravel()[fidx])
        negpool = (train_region & ~ndimage.binary_dilation(fd.train_truth, iterations=2)).ravel()[fidx]
        neg_ids = rng.choice(np.flatnonzero(negpool), size=min(600_000, int(negpool.sum())), replace=False)
        X = np.vstack([rows(pos_ids, d), rows(neg_ids, d)])
        y = np.r_[np.ones(len(pos_ids)), np.zeros(len(neg_ids))]
        w = np.r_[np.full(len(pos_ids), len(neg_ids) / len(pos_ids)), np.ones(len(neg_ids))]
        clf = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.08, max_leaf_nodes=31, min_samples_leaf=100,
                                             l2_regularization=1.0, random_state=fd.f)
        clf.fit(X, y, sample_weight=w)
        models.append(clf)
        del X, d
        print(f"  model {fd.f} trained ({len(pos_ids)} pos) {time.time()-t0:.0f}s", flush=True)

    # inference with the full catalogue visible
    d = ctx(cat)
    prob = np.zeros(fidx.size, np.float32)
    for c0 in range(0, fidx.size, 400_000):
        ids = np.arange(c0, min(c0 + 400_000, fidx.size))
        Xc = rows(ids, d)
        prob[ids] = np.mean([m.predict_proba(Xc)[:, 1] for m in models], axis=0)
    field = np.zeros(foot.size, np.float32); field[fidx] = prob; field = field.reshape(foot.shape)
    np.save(WORK / "final_field.npy", field)
    print(f"  field done {time.time()-t0:.0f}s", flush=True)

    allowed = foot & catalogue_exclusion(cat, PRUNE_PX)
    dots = poisson_disk_dots(field, allowed, N_DOTS, SPACING)
    dcat = ndimage.distance_transform_edt(~cat)
    emission = dict(n_dots=int(dots.sum()), spacing_px=SPACING, prune_px=PRUNE_PX,
                    dots_within_2px_of_catalogue=int((dcat[dots] <= 2).sum()), dots_on_catalogue=int((dots & cat).sum()),
                    dots_with_lidar=int((dots & lidar_valid).sum()), field_quantile_of_last_dot=float((field[foot] < field[dots].min()).mean()))

    audit = lane_audit(field, dots, foot)
    print(f"  lane audit: max spearman={audit['max_spearman']:.3f} max overlap={audit['max_frac_dots_within_3px']:.3f} duplicate={audit['is_duplicate']}", flush=True)

    sha8 = sha256_file(WORK / "final_field.npy")[:8]
    name = f"gemsass1-swgb-hrv2-{N_DOTS}dots-{STAMP}-{sha8}-zeros"
    note = f"GEMSASS1 SWGB: 5x segment-withheld HGB on lidar+GeoDAWN, {N_DOTS} dots 2.8px, >600m off-catalogue; HOLDOUT-DTI 0.140 vs base 0.101"
    verdict = "promote" if (not audit["is_duplicate"]) else "negative-duplicate"
    if audit["is_duplicate"]:
        print("DUPLICATE LANE — not writing a submission file")
        rep = None
    else:
        rep = write_submission(dots, foot, DOWNLOADS / f"{name}.tif", catalogue=cat, note=note,
                               meta=dict(lane="E2-SWGB", emission=emission))
        print(f"  wrote {rep['path']} sha256={rep['sha256'][:16]} all_checks={rep['all_checks_passed']}")

    e2 = json.loads((EVIDENCE / "e2_swgb_holdout.json").read_text())
    card = {
        "hypothesis": "New (uncatalogued) faults share the lidar scarp-morphology, radiometric and magnetic signature of catalogued faults; a learner trained to RECOVER WITHHELD catalogue segments from the visible catalogue + GeoDAWN/lidar layers transfers to the live task of finding faults missing from USGS/INGENIOUS.",
        "mechanism": "Segment-withheld gradient boosting (5 models, each trained on a different 20% of catalogue segments hidden together with the test 20%), features: 28 lidar/radiometric/magnetic layers + visible-only catalogue context (distance, tip distance, density, strike agreement). Averaged probability field -> Poisson-disk dots (2.8 px) placed only >2 px from the catalogue.",
        "named_non_fault_mimic": "Fluvial terrace risers, pluvial Lake Lahontan shorelines and road/canal embankments produce the same crest-convex/base-concave lidar dipole; lithologic contacts produce radiometric/magnetic edges without faulting.",
        "holdout_dti": {"label": "HOLDOUT-DTI", "evaluator": EVALUATOR_VERSION, "value": e2["holdout_dti"], "ci95": e2["ci95"],
                        "n_withheld_positives": e2["n_withheld_positives"], "bar_0p2600_family_base": e2["bar"]},
        "holdout_dti_shipped_emission": {"label": "HOLDOUT-DTI", "evaluator": EVALUATOR_VERSION,
                                          "emission": f"{N_DOTS} dots, {SPACING} px spacing, {PRUNE_PX:.0f} px catalogue exclusion",
                                          "source": "evidence/e3_prune_sweep_e2.json (prune_px == PRUNE_PX, n_dots == N_DOTS)"},
        "correlation_overlap_vs_registry": {"max_spearman": audit["max_spearman"], "max_frac_dots_within_3px": audit["max_frac_dots_within_3px"],
                                            "thresholds": audit["thresholds"], "is_duplicate": audit["is_duplicate"], "rows": audit["rows"]},
        "emission": emission,
        "raster_sha256": rep["sha256"] if rep else None,
        "validator_output": rep["checks"] if rep else None,
        "submission_name": f"{name}.tif" if rep else None,
        "submission_note": note,
        "note_length": len(note),
        "verdict": verdict,
        "score_labels": "No live score exists for this file. HOLDOUT-DTI is not a leaderboard score; projections are not scores.",
        "organizer_confirmed": None,
        "generated_utc": STAMP, "elapsed_s": round(time.time() - t0, 1), "n_segments": int(n_seg),
    }
    (EVIDENCE / "run_card.json").write_text(json.dumps(card, indent=2))
    print(json.dumps({k: card[k] for k in ("verdict", "raster_sha256", "submission_name", "note_length")}, indent=1))


if __name__ == "__main__":
    main()
