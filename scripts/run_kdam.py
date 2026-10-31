#!/usr/bin/env python3
"""H-KDAM lane runner (2026-10-31): damage-zone radiometrics x potential-field contacts.

Sub-commands (each writes its own evidence file; nothing overwrites a previous run card):
  registry  -- build the union dot mask of the 489-raster pinned registry (novelty constraint)
  features  -- build and cache the label-free feature stack (float16) under work/kdam/
  canary    -- single-feature AUC leakage canary on fold 0 (AUC > 0.90 means leakage)
  e1        -- E1: 5 segment-withheld fields, protocol emission, pooled HOLDOUT-DTI
  e2        -- E2: paired E1 field with the registry-repulsive (novelty-by-construction) emission
  final     -- full-catalogue field -> submission GeoTIFF/ZIP through the fail-closed writer

Evidence: evidence/kdam/*.json. Feature cache and fields: work/kdam/ (git-ignored).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.gems import holdout as HO                     # noqa: E402
from src.gems.emission import catalogue_exclusion, poisson_disk_dots  # noqa: E402
from src.gems.grid import (load_catalogue, load_footprint, read_profile,  # noqa: E402
                           sha256_file)
from src.gems.kdam import build_kdam_features, rank_features  # noqa: E402
from src.gems.submission import write_submission  # noqa: E402

WORK = ROOT / "work/kdam"
EV = ROOT / "evidence/kdam"
REGISTRY_INV = ROOT / "registry/focus_inventory_20261030.json"

STATIC_NAMES = [
    "lidar_ex_max", "lidar_step_max", "lidar_lapneg_max", "lidar_relief", "lidar_coh100",
    "lidar_strike_cos2", "lidar_strike_sin2",
    "rad_K", "rad_Th", "rad_ThK", "kdep_halo", "kdep_deplete",
    "mag_TMI", "mag_tdr", "mag_theta", "mag_hgm500", "lineament_persist", "mcontact_dist",
    "xcal_agree",
]
CAT_NAMES = ["dist_vis", "dens_vis", "tip_vis"]

# pre-registered operating point: the champion's live-density cell (37,654 dots / 2.8 px / >2 px
# catalogue prune), so a score difference cannot come from emission density alone.
N_DOTS = 37_654
MIN_DIST_PX = 2.8
CAT_PRUNE_PX = 2.0
HGB = dict(max_iter=200, learning_rate=0.06, max_leaf_nodes=31, min_samples_leaf=40,
           l2_regularization=1.0, early_stopping=False, random_state=20261031)
N_TRAIN_NEG = 120_000
CHUNK = 400_000


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# --------------------------------------------------------------------------- registry union
def is_exempt(item: dict) -> bool:
    """Exempt only documented non-competitive fixtures (never a competitive prediction).

    The 5 px calibration lattice is a synthetic regular grid published as a `inputs/calibration`
    artifact, and one file is an explicit 32x48 FORMAT_TEST fixture. Everything else is a
    competitive submission raster and counts for the lane-drift rule.
    """
    p = item["path"].lower()
    return ("calibration" in p) or ("lattice" in p) or ("format_test" in p)


def cmd_registry(_args) -> int:
    inv = json.loads(REGISTRY_INV.read_text())
    union = np.zeros((3730, 3292), bool)
    rows, exempt = [], []
    for i, item in enumerate(inv["rasters"]):
        path = ROOT / item["local"]
        if not path.exists():
            raise SystemExit(f"registry file missing: {path}")
        if is_exempt(item):
            exempt.append(dict(repo=item["repo"], path=item["path"]))
            continue
        from src.gems.grid import read_band
        a = read_band(path)
        dots = np.nan_to_num(a, nan=0.0) > 0.0
        union |= dots
        rows.append(dict(repo=item["repo"], path=item["path"], positive_pixels=int(dots.sum())))
        del a, dots
        if (i + 1) % 50 == 0:
            log(f"registry {i + 1}/{len(inv['rasters'])}")
    WORK.mkdir(parents=True, exist_ok=True)
    np.save(WORK / "registry_union.npy", union)
    out = dict(generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               inventory=str(REGISTRY_INV.relative_to(ROOT)), snapshot_utc=inv["snapshot_utc"],
               rasters_in_inventory=len(inv["rasters"]), competitive_rasters=len(rows),
               exempt_fixtures=exempt, union_positive_pixels=int(union.sum()),
               footprint_cells=5_167_373,
               union_fraction_of_footprint=float(union.sum() / 5_167_373),
               scope="nine focus repos, competitive submission rasters only, synthetic calibration "
                     "fixtures exempt (AMEND-LATTICE-01)",
               per_raster=rows)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / "registry_union.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    log(f"union {union.sum()} px of 5,167,373 ({100 * union.sum() / 5_167_373:.2f}%)")
    return 0


# --------------------------------------------------------------------------- features
def load_static() -> tuple[np.ndarray, np.ndarray]:
    cache = WORK / "static.npz"
    if cache.exists():
        z = np.load(cache)
        return z["x"], z["valid"]
    WORK.mkdir(parents=True, exist_ok=True)
    log("building label-free feature stack (fft transforms)")
    feats, valid = build_kdam_features()
    x = rank_features(feats, valid, STATIC_NAMES)
    np.savez(cache, x=x, valid=valid)
    meta = dict(features=STATIC_NAMES, dtype="float16", scaling="percentile rank [0,1] over valid cells",
                valid_cells=int(valid.sum()))
    (EV / "feature_stack.json").write_text(json.dumps(meta, indent=2) + "\n")
    log(f"features {x.shape} valid {valid.sum()}")
    return x, valid


def cmd_features(_args) -> int:
    EV.mkdir(parents=True, exist_ok=True)
    x, valid = load_static()
    print(json.dumps(dict(shape=x.shape, names=STATIC_NAMES, valid_cells=int(valid.sum()))))
    return 0


def design_matrix(x: np.ndarray, cat: dict[str, np.ndarray], idx: np.ndarray) -> np.ndarray:
    cols = [x[i].ravel()[idx] for i in range(x.shape[0])]
    cols += [cat[c].ravel()[idx] for c in CAT_NAMES]
    return np.column_stack(cols).astype(np.float32)


# --------------------------------------------------------------------------- canary
def cmd_canary(_args) -> int:
    x, valid = load_static()
    foot = load_footprint()
    cat = load_catalogue()
    folds, _ = HO.build_folds(cat, foot)
    f0 = folds[0]
    truth = f0.test_truth
    out = dict(evidence_class="LEAKAGE-CANARY, NOT A DTI SCORE", evaluator=HO.EVALUATOR_VERSION,
               fold=0, n_withheld_positives=int(truth.sum()), features={}, flagged_over_0p90={})
    for i, n in enumerate(STATIC_NAMES):
        score = np.where(valid, x[i].astype(np.float32), np.nan)
        ok = np.isfinite(score)
        auc = HO.auc_binary(np.where(ok, score, 0.0), truth, sample=200_000)
        out["features"][n] = auc
        if auc > 0.90:
            out["flagged_over_0p90"][n] = auc
    EV.mkdir(parents=True, exist_ok=True)
    (EV / "leakage_canary.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(json.dumps(out["features"], indent=2))
    print("flagged:", out["flagged_over_0p90"])
    return 0


# --------------------------------------------------------------------------- fields
def fit_field(x, valid, cat_feats, train_truth, foot, active_neg, seed=0):
    from sklearn.ensemble import HistGradientBoostingClassifier
    rng = np.random.default_rng(seed)
    pos = np.flatnonzero(train_truth.ravel() & valid.ravel())
    neg_pool = np.flatnonzero(active_neg.ravel() & valid.ravel())
    neg = rng.choice(neg_pool, size=min(N_TRAIN_NEG, neg_pool.size), replace=False)
    idx = np.concatenate([pos, neg])
    X = design_matrix(x, cat_feats, idx)
    y = np.concatenate([np.ones(pos.size), np.zeros(neg.size)])
    w = np.where(y > 0, 1.0, pos.size / max(neg.size, 1))
    clf = HistGradientBoostingClassifier(**HGB)
    clf.fit(X, y, sample_weight=w)
    del X
    return clf


def predict_field(clf, x, cat_feats, foot, valid) -> np.ndarray:
    field = np.zeros(foot.shape, np.float32)
    idx = np.flatnonzero(foot.ravel())
    for s in range(0, idx.size, CHUNK):
        sub = idx[s:s + CHUNK]
        X = design_matrix(x, cat_feats, sub)
        field.ravel()[sub] = clf.predict_proba(X)[:, 1]
        del X
    field[~foot] = 0.0
    return field


def emit(field, allowed, n_dots=N_DOTS, min_dist=MIN_DIST_PX):
    return poisson_disk_dots(field, allowed, n_dots, min_dist, max_candidates=1_500_000)


def novelty_mask() -> np.ndarray:
    union = np.load(WORK / "registry_union.npy")
    # 4 px, not 3: a dot at exactly 3 px is inside the protocol's <=3 px overlap test after rounding
    return ndimage.distance_transform_edt(~union) > 4.0


# --------------------------------------------------------------------------- E1
def champion_comparator(folds) -> dict:
    """Pooled HOLDOUT-DTI of the incumbent family field under the SAME emission rules.

    `gems25-dotted-h19-5-d2-8` (44,090 dots, the 0.2600 live base of every file >= 0.24 in the
    nine focus sites) and its 2 px-pruned 0.2778 descendant are scored with the shared evaluator,
    unpruned and pruned, so a field comparison is like-for-like instead of against a quoted number.
    """
    import json
    inv = json.loads(REGISTRY_INV.read_text())
    paths = {r["path"].split("/")[-1]: r["local"] for r in inv["rasters"]}
    out = {}
    for fname, label in [("gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif", "family_base_44090"),
                         ("gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif", "live_champion_37654")]:
        from src.gems.grid import read_band
        a = read_band(paths[fname])
        dots = np.nan_to_num(a, nan=0.0) > 0.0
        pooled = HO.score_pooled([dots] * len(folds), folds, n_boot=200)
        out[label] = dict(holdout_dti=pooled["holdout_dti"], ci95=pooled["ci95"],
                          n_dots=int(dots.sum()), tp=pooled["tp"], fp=pooled["fp"], fn=pooled["fn"],
                          raw_file=fname)
        del a, dots
    return out


def cmd_e1(_args) -> int:
    """E1: five segment-withheld fields; two preregistered emission rules per field."""
    t0 = time.time()
    x, valid = load_static()
    foot = load_footprint()
    cat = load_catalogue()
    folds, n_seg = HO.build_folds(cat, foot)
    allowed = {"A_unpruned": foot & valid,
               "B_prune2": catalogue_exclusion(cat, CAT_PRUNE_PX) & foot & valid}
    fields = (WORK / "fields")
    fields.mkdir(parents=True, exist_ok=True)
    preds = {k: [] for k in allowed}
    per_fold = []
    for f in folds:
        cf = {k: v for k, v in HO.catalogue_features(f.visible, foot).items() if k in CAT_NAMES}
        t1 = time.time()
        clf = fit_field(x, valid, cf, f.train_truth, foot, f.active & ~f.train_truth, seed=f.f)
        field = predict_field(clf, x, cf, foot, valid)
        np.save(fields / f"fold{f.f}.npy", field.astype(np.float16))
        row = dict(fold=f.f, n_test=f.n_test, fit_s=round(time.time() - t1, 1))
        for k, al in allowed.items():
            dots = emit(field, al)
            sc = HO.score_pooled([dots], [f], n_boot=100)
            preds[k].append(dots)
            row[k] = dict(emitted=int(dots.sum()), dti=sc["holdout_dti"], ci95=sc["ci95"],
                          tp=sc["tp"], fp=sc["fp"])
        per_fold.append(row)
        log(f"fold {f.f}: A_unpruned {row['A_unpruned']['dti']:.4f}  B_prune2 {row['B_prune2']['dti']:.4f}")
        del cf, clf, field
    arms = {}
    for k in allowed:
        pooled = HO.score_pooled(preds[k], folds, n_boot=300)
        ff = HO.score_pooled_farfield(preds[k], folds)
        arms[k] = dict(holdout_dti=pooled["holdout_dti"], ci95=pooled["ci95"],
                       tp=pooled["tp"], fp=pooled["fp"], fn=pooled["fn"],
                       farfield_gt5px=dict(holdout_dti=ff["holdout_dti"], ci95=ff["ci95"]))
    comparators = champion_comparator(folds)
    out = dict(evidence_class="HOLDOUT-DTI", lane="H-KDAM", experiment="E1",
               evaluator=HO.EVALUATOR_VERSION, n_withheld_positives=int(sum(f.n_test for f in folds)),
               n_segments=n_seg, alpha=0.2, beta=0.8, radius_m=300.0,
               emission=dict(n_dots_target=N_DOTS, min_dist_px=MIN_DIST_PX,
                             arms="A_unpruned = no catalogue mask; B_prune2 = catalogue prune 2 px"),
               model=dict(kind="HistGradientBoostingClassifier", params=HGB, n_train_neg=N_TRAIN_NEG,
                          features=STATIC_NAMES + CAT_NAMES),
               arms=arms, comparators_same_emission=comparators, per_fold=per_fold,
               runtime_s=round(time.time() - t0, 1),
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    EV.mkdir(parents=True, exist_ok=True)
    (EV / "e1_holdout.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(json.dumps(dict(arms=arms, comparators=comparators), indent=2))
    return 0


# --------------------------------------------------------------------------- E2
def cmd_e2(_args) -> int:
    """E2 (paired): same fold fields, same operating point, plus the novelty constraint.

    The constraint mask is `work/kdam/exclusion.npy`: everything within 4 px of the dots of any
    registry raster that the unconstrained candidate exceeded 70% overlap with. It is derived by
    `novelty_scan.py` from the *unconstrained* candidate and then frozen, so E2 cannot tune it.
    """
    x, valid = load_static()
    foot = load_footprint()
    cat = load_catalogue()
    folds, _ = HO.build_folds(cat, foot)
    excl_path = WORK / "exclusion.npy"
    if not excl_path.exists():
        raise SystemExit("work/kdam/exclusion.npy missing: run novelty_scan.py on the base candidate first")
    keep = ~np.load(excl_path)
    allowed = {"B_prune2": catalogue_exclusion(cat, CAT_PRUNE_PX) & foot & valid,
               "C_novelty": catalogue_exclusion(cat, CAT_PRUNE_PX) & foot & valid & keep}
    preds = {k: [] for k in allowed}
    per_fold = []
    for f in folds:
        field = np.load(WORK / "fields" / f"fold{f.f}.npy").astype(np.float32)
        row = dict(fold=f.f, n_test=f.n_test)
        for k, al in allowed.items():
            dots = emit(field, al)
            sc = HO.score_pooled([dots], [f], n_boot=100)
            preds[k].append(dots)
            row[k] = dict(emitted=int(dots.sum()), dti=sc["holdout_dti"], ci95=sc["ci95"],
                          tp=sc["tp"], fp=sc["fp"])
        per_fold.append(row)
        log(f"fold {f.f}: B {row['B_prune2']['dti']:.4f}  C {row['C_novelty']['dti']:.4f}")
        del field
    arms = {}
    for k in preds:
        pooled = HO.score_pooled(preds[k], folds, n_boot=300)
        ff = HO.score_pooled_farfield(preds[k], folds)
        arms[k] = dict(holdout_dti=pooled["holdout_dti"], ci95=pooled["ci95"], tp=pooled["tp"],
                       fp=pooled["fp"], fn=pooled["fn"],
                       farfield_gt5px=dict(holdout_dti=ff["holdout_dti"], ci95=ff["ci95"]))
    deltas = np.array([r["C_novelty"]["dti"] - r["B_prune2"]["dti"] for r in per_fold])
    out = dict(evidence_class="HOLDOUT-DTI", lane="H-KDAM", experiment="E2-paired-novelty-constrained",
               evaluator=HO.EVALUATOR_VERSION,
               n_withheld_positives=int(sum(f.n_test for f in folds)),
               arms=arms, paired_delta_mean=float(deltas.mean()),
               paired_delta_per_fold=deltas.tolist(),
               novelty_rule="no dot within 4 px of the dots of any registry raster the unconstrained "
                            "candidate exceeded 70% 3 px overlap with (frozen mask, derived before scoring)",
               per_fold=per_fold, runtime_s=None,
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    (EV / "e2_paired_novelty.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(json.dumps(dict(arms=arms, paired_delta=out["paired_delta_mean"]), indent=2))
    return 0


# --------------------------------------------------------------------------- final
def cmd_final(args) -> int:
    t0 = time.time()
    x, valid = load_static()
    foot = load_footprint()
    cat = load_catalogue()
    cf = HO.catalogue_features(cat, foot)          # full catalogue = the live-legal context
    cf = {k: cf[k] for k in CAT_NAMES}
    clf = fit_field(x, valid, cf, cat, foot, (foot & ~cat), seed=20261031)
    field = predict_field(clf, x, cf, foot, valid)
    allowed = catalogue_exclusion(cat, CAT_PRUNE_PX) & foot & valid
    if args.mode == "novelty":
        allowed &= ~np.load(WORK / "exclusion.npy")
    dots = emit(field, allowed)
    np.save(WORK / f"candidate_{args.mode}.npy", dots)
    log(f"{args.mode}: emitted {int(dots.sum())} dots")
    if args.mode == "base":
        print(json.dumps(dict(mode="base", n_dots=int(dots.sum()),
                              saved=str(WORK / "candidate_base.npy"),
                              note="unconstrained candidate for the novelty scan only; not published")))
        return 0
    name = args.name
    out_tif = ROOT / "docs/downloads" / f"{name}.tif"
    note = ("GEMSASS1 H-KDAM: K/Th depletion x magnetic contact/lineament corroboration, "
            "37654d 2.8px >2px offcat, registry-repulsive")
    note = note[:140]
    rep = write_submission(dots.astype(np.float32), foot, out_tif, catalogue=cat, note=note,
                           meta=dict(lane="H-KDAM", n_dots=int(dots.sum()), registry_repulsive_px=4.0))
    out = dict(evidence_class="FORMAT-VALIDATOR (from bytes; not a score)", lane="H-KDAM",
               experiment="final", submission=name, validator=rep,
               profile=read_profile(out_tif), sha256=sha256_file(out_tif),
               n_dots=int(dots.sum()), runtime_s=round(time.time() - t0, 1),
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    (EV / f"final_{name}.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(json.dumps(dict(ok=rep["all_checks_passed"], positive_pixels=rep["positive_pixels"],
                          sha256=rep["sha256"], note=rep["submission_note"]), indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("registry", "features", "canary", "e1", "e2", "final"):
        p = sub.add_parser(name)
        if name == "final":
            p.add_argument("--name", default="gemsass1-kdam-alteration-contact-37654-20261031-zeros")
            p.add_argument("--mode", choices=["base", "novelty"], default="base")
    args = ap.parse_args()
    return {"registry": cmd_registry, "features": cmd_features, "canary": cmd_canary,
            "e1": cmd_e1, "e2": cmd_e2, "final": cmd_final}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
