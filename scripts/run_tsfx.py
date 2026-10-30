#!/usr/bin/env python3
"""H-TSFX lane — session 2026-10-30. Preregistration: knowledge/hypotheses_20261030.md.

Memory-lean flat-vector architecture (footprint-only feature vectors; full grids only inside
band-by-band transforms) because the build sandbox has 3 GB RAM / 2 CPUs.

Stages (run in order; budget: 3 experiments / 2 hours, tracked in evidence/tsfx/budget.json):

  canary   : every input feature alone vs withheld truth on all 5 folds; AUC > 0.90 stops the lane.
  e1       : H-TSFX segment-withheld learner (E2-SWGB hyper-parameters, expanded feature set)
             -> HOLDOUT-DTI on GEMSASS1-HR-v2-segment, pooled + far-field; bars: promote 0.1011,
             current repo holdout best 0.1591 (evidence/swgb/e3_prune_sweep_e2.json).
  e2       : emission sweep on the E1 fields (n x spacing x visible-prune), overlap vs the 17
             focus rasters per config; winner must keep max overlap <= 0.70.
  package  : full-registry novelty scan (414 + sibling/prior files; AMEND-LATTICE-01 / AMEND-N2
             in knowledge/hypotheses_20261030.md), fail-closed writer, run card.

Shared tools reused from src/gems and scripts/novelty.py. No private forks; no slot; no upload.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import ndimage
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from gems.grid import (BRIDGE, DATA, load_catalogue, load_footprint, read_band)  # noqa: E402
from gems.holdout import (EVALUATOR_VERSION, auc_binary, build_folds, catalogue_features,
                          score_pooled, score_pooled_farfield)  # noqa: E402
from gems.features import build_static_features  # noqa: E402
from gems.emission import poisson_disk_dots  # noqa: E402
from gems.registry import DOT_OVERLAP_MAX, RANK_CORR_MAX  # noqa: E402
from gems.submission import write_submission  # noqa: E402
from scripts.novelty import audit as novelty_audit, canonical_hash  # noqa: E402

BAR = dict(name="gems25-dotted-h19-5-d2-8 (0.2600 family base, un-pruned)",
           holdout_dti=0.1011, ci95=[0.0956, 0.1072],
           evidence="evidence/swgb/holdout_calibration.json")
REPO_BEST = dict(name="E2-SWGB field emission, prune 4 px, 44,090 dots",
                 holdout_dti=0.1591, ci95=[0.1538, 0.1639],
                 evidence="evidence/swgb/e3_prune_sweep_e2.json")
E2_AS_EVALUATED = dict(name="E2-SWGB as evaluated",
                       holdout_dti=0.1586, ci95=[0.1519, 0.1649],
                       evidence="evidence/swgb/e2_swgb_holdout.json")
N_DOTS = 44_090
SPACING = 2.8
LATTICE_PATH_HINT = "inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
EVID = ROOT / "evidence" / "tsfx"
WORK = ROOT / "work" / "tsfx"
EXTRA_REG = DATA / "registry_extra"
SITE_DOWNLOADS = ROOT / "docs" / "downloads"
BUDGET_SECONDS = 7200
EXPERIMENT_BUDGET = 3

NEW_BANDS = {  # short name -> band index (1-based) in the 19-band stack
    "mag_anom": 1, "rtp": 2, "tmi_hg": 3, "geod_2ndinv": 4, "iso_grav_anom_slope": 5,
    "tc": 6, "geod_shearrate": 7, "geod_dilaterate": 8, "tmi_vg": 9, "deq_n100a15": 10,
    "iso_grav_anom_vg": 11, "det_elev": 12, "iso_grav_anom": 13, "tmi": 14,
    "depth_to_base_surf": 15, "ieq_n100a15": 16, "cond_surf": 17, "iso_grav_anom_hg": 18,
    "det_elev_slope": 19,
}
CTX = ["cat_logdist", "cat_logtip", "cat_dens", "cat_strike_agree"]


def save(name: str, obj) -> None:
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / name).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def budget_add(stage: str, seconds: float, experiments: int = 0) -> dict:
    EVID.mkdir(parents=True, exist_ok=True)
    p = EVID / "budget.json"
    b = json.loads(p.read_text()) if p.exists() else dict(
        stages={}, cumulative_seconds=0.0, experiments_run=0,
        seconds_budget=BUDGET_SECONDS, experiment_budget=EXPERIMENT_BUDGET)
    b["stages"][stage] = dict(seconds=round(seconds, 1), utc=datetime.now(timezone.utc).isoformat())
    b["cumulative_seconds"] = round(b["cumulative_seconds"] + seconds, 1)
    b["experiments_run"] += experiments
    p.write_text(json.dumps(b, indent=2, allow_nan=False) + "\n")
    return b


def budget_get() -> dict:
    p = EVID / "budget.json"
    return json.loads(p.read_text()) if p.exists() else dict(
        cumulative_seconds=0.0, experiments_run=0, stages={})


def budget_check() -> dict:
    b = budget_get()
    if b.get("cumulative_seconds", 0.0) > BUDGET_SECONDS:
        raise SystemExit("two-hour budget exhausted")
    return b


# ---------------------------------------------------------------- contexts
def base_context():
    foot, cat = load_footprint(), load_catalogue()
    folds, n_seg = build_folds(cat, foot)
    fidx = np.flatnonzero(foot.ravel())
    return foot, cat, folds, fidx, n_seg


def polarity_flat(feats_full: dict, lidar_valid: np.ndarray, fidx: np.ndarray) -> dict:
    """H-POLCOH / H-RELAYPOL label-free polarity transforms (static; no catalogue input)."""
    step = feats_full["lidar_step_max"]
    asym = feats_full["lidar_face_asym"]
    cos2, sin2 = feats_full["lidar_strike_cos2"], feats_full["lidar_strike_sin2"]
    m = lidar_valid & (step > 0)
    if not m.any():
        m = lidar_valid
    thr = float(np.percentile(step[m], 80))
    w = (m & (step >= thr)).astype(np.float32)
    del m
    g = lambda a, s=4.0: ndimage.gaussian_filter(a.astype(np.float32), s)  # noqa: E731
    facing = g(asym * w)
    c, s_, n = g(cos2 * w), g(sin2 * w), g(w)
    conc = np.hypot(c, s_) / np.maximum(n, 1e-3)
    flip = g(np.abs(asym) * w) - np.abs(facing)
    streak = g(step * w)
    out = {
        "lidar_pol_facing": np.abs(facing),
        "lidar_strike_conc": np.minimum(conc, 1.0),
        "lidar_facing_instab": np.maximum(flip, 0.0),
        "lidar_step_streak": streak,
    }
    return {k: v.ravel()[fidx].astype(np.float32) for k, v in out.items()}


def load_flat(foot: np.ndarray, fidx: np.ndarray) -> tuple[dict, np.ndarray]:
    """Footprint-only static + polarity + 19-band vectors. Full grids are freed band-by-band."""
    feats_full, valid = build_static_features()
    pol = polarity_flat(feats_full, valid, fidx)
    flat = {}
    for n in list(feats_full):
        flat[n] = feats_full[n].ravel()[fidx].astype(np.float16)
        del feats_full[n]
    del feats_full
    flat.update(pol)
    del pol
    import rasterio
    with rasterio.open(ROOT / "data" / "official" / "training_features.tif") as s:
        nodata = s.nodata
        for name, idx in NEW_BANDS.items():
            a = s.read(idx).astype(np.float32)
            if nodata is not None:
                a[a == nodata] = np.nan
            a[~foot] = np.nan
            flat["geo_" + name] = a.ravel()[fidx].astype(np.float32)
            del a
    return flat, valid


def add_ctx_flat(fd, foot: np.ndarray, fidx: np.ndarray, flat: dict) -> dict:
    """Visible-only catalogue context as footprint vectors (fold-safe)."""
    catf = catalogue_features(fd.visible, foot)
    out = dict(flat)
    strike_deg = (flat["lidar_strike"].astype(np.float32) - 1.0) / 254.0 * 180.0
    out["cat_logdist"] = np.log1p(catf["dist_vis"].ravel()[fidx]).astype(np.float32)
    out["cat_logtip"] = np.log1p(catf["tip_vis"].ravel()[fidx]).astype(np.float32)
    out["cat_dens"] = catf["dens_vis"].ravel()[fidx].astype(np.float32)
    out["cat_strike_agree"] = np.cos(2 * (np.deg2rad(strike_deg) - catf["strike_vis"].ravel()[fidx])).astype(np.float32)
    del catf
    return out


# ---------------------------------------------------------------- canary
def run_canary():
    t0 = time.time()
    foot, cat, folds, fidx, _ = base_context()
    flat, _valid = load_flat(foot, fidx)
    names = sorted(flat.keys())
    rows = {}
    for fd in folds:
        fa = add_ctx_flat(fd, foot, fidx, flat)
        active_f = fd.active.ravel()[fidx]
        truth_f = fd.test_truth.ravel()[fidx]
        for n in names + CTX:
            a = np.nan_to_num(fa[n][active_f], nan=0.0)
            v = float(auc_binary(a, truth_f[active_f]))
            if v == v:
                rows.setdefault(n, []).append(v)
        del fa
    agg = {n: float(np.mean(v)) for n, v in rows.items()}
    flagged = {n: v for n, v in agg.items() if v > 0.90}
    elapsed = round(time.time() - t0, 1)
    out = dict(evidence_class="LEAKAGE-CANARY, NOT A DTI SCORE", evaluator=EVALUATOR_VERSION,
               folds=list(range(len(folds))), n_features=len(agg), auc_mean_over_folds=agg,
               auc_per_fold=rows, flagged_over_0p90=flagged,
               note="NaN (nodata) treated as 0 for AUC only; backgrounds are unlabeled, not verified negatives.",
               elapsed_s=elapsed)
    save("leakage_canary.json", out)
    budget_add("canary", elapsed)
    for n, v in sorted(agg.items(), key=lambda kv: -kv[1])[:15]:
        print(f"  {n:28s} meanAUC={v:.3f}")
    print("flagged (>0.90):", flagged or "none")
    return not flagged


# ---------------------------------------------------------------- E1
def run_e1():
    from sklearn.ensemble import HistGradientBoostingClassifier
    t0 = time.time()
    budget_check()
    if budget_get().get("experiments_run", 0) >= EXPERIMENT_BUDGET:
        raise SystemExit("experiment budget exhausted")
    foot, cat, folds, fidx, _ = base_context()
    flat, _valid = load_flat(foot, fidx)
    names = sorted(flat.keys()) + CTX
    rng = np.random.default_rng(7)
    dots_by_fold, fields = [], []

    def rows(ids, flat_all):
        return np.stack([flat_all[n][ids] for n in names], axis=1).astype(np.float32)

    for fd in folds:
        flat_all = add_ctx_flat(fd, foot, fidx, flat)
        guard = ndimage.binary_dilation(fd.test_truth, iterations=3)
        train_region = fd.active & ~guard
        pos = (fd.train_truth & train_region).ravel()[fidx]
        negpool = (train_region & ~ndimage.binary_dilation(fd.train_truth, iterations=2)).ravel()[fidx]
        neg_ids = rng.choice(np.flatnonzero(negpool), size=min(600_000, int(negpool.sum())), replace=False)
        pos_ids = np.flatnonzero(pos)
        X = np.vstack([rows(pos_ids, flat_all), rows(neg_ids, flat_all)])
        y = np.r_[np.ones(len(pos_ids)), np.zeros(len(neg_ids))]
        w = np.r_[np.full(len(pos_ids), len(neg_ids) / max(len(pos_ids), 1)), np.ones(len(neg_ids))]
        clf = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.08, max_leaf_nodes=31,
                                             min_samples_leaf=100, l2_regularization=1.0,
                                             random_state=fd.f)
        clf.fit(X, y, sample_weight=w)
        del X
        act_ids = np.flatnonzero(fd.active.ravel()[fidx])
        prob = np.zeros(fidx.size, np.float32)
        for c in range(0, act_ids.size, 400_000):
            ch = act_ids[c:c + 400_000]
            prob[ch] = clf.predict_proba(rows(ch, flat_all))[:, 1]
        field = np.zeros(foot.size, np.float32)
        field[fidx] = prob
        field = field.reshape(foot.shape)
        fields.append(field.astype(np.float16))
        dots_by_fold.append(poisson_disk_dots(field, fd.active, N_DOTS, SPACING))
        print(f"  fold {fd.f}: pos={len(pos_ids)} neg={len(neg_ids)} dots={int(dots_by_fold[-1].sum())} {time.time()-t0:.0f}s", flush=True)
        del flat_all, prob, field
    s = score_pooled(dots_by_fold, folds)
    ff = score_pooled_farfield(dots_by_fold, folds)
    WORK.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(WORK / "tsfx_fields.npz", *fields)
    elapsed = round(time.time() - t0, 1)
    budget_add("e1_train", elapsed, experiments=1)
    print("E1 training fields saved; scoring stage is e1score", flush=True)
    print("in-run pooled score (float32, before crash):", json.dumps({"holdout_dti": s["holdout_dti"]}))


def run_e1score():
    """Score the frozen E1 fields with the shared evaluator (no retraining, no experiment budget).

    The E1 training run completed all five folds and saved fields (float16) but crashed while
    assembling its result dict (duplicate keyword `evaluator`). Scoring is therefore redone here
    from the saved fields with identical emission and evaluator code. Float16 storage may change
    tie-breaks in the greedy Poisson-disk step versus the lost float32 in-memory values; this is
    disclosed in the run card and the same float16 fields are used by the E2 sweep and packaging."""
    t0 = time.time()
    foot, cat, folds, fidx, _ = base_context()
    names = None
    dots_by_fold = []
    with np.load(WORK / "tsfx_fields.npz") as z:
        for i, fd in enumerate(folds):
            fl = z[f"arr_{i}"].astype(np.float32)
            dots_by_fold.append(poisson_disk_dots(fl, fd.active & (fl > 0), N_DOTS, SPACING))
    s = score_pooled(dots_by_fold, folds)
    ff = score_pooled_farfield(dots_by_fold, folds)
    flat_names = sorted(load_names_only())
    names = flat_names + CTX
    elapsed = round(time.time() - t0, 1)
    out = dict(experiment="E1-H-TSFX",
               hypothesis="tectonic-strain fusion learner: SWGB's 28 layers + 19 GeoDAWN/strain/seismicity/"
                          "basement/conductivity/detrended bands + 4 polarity-coherence transforms + "
                          "4 visible-only catalogue-context features (55 total)",
               features=names,
               provenance_note="Trained in run_tsfx.py e1 (completed 5 folds, fields saved, result-dict "
                               "crash). Scored here from float16 saved fields via run_e1score.",
               **s, farfield=ff,
               bar=BAR, repo_best=REPO_BEST, e2_as_evaluated=E2_AS_EVALUATED,
               beats_bar=s["holdout_dti"] > BAR["holdout_dti"],
               beats_repo_best=s["holdout_dti"] > REPO_BEST["holdout_dti"],
               n_dots=N_DOTS, spacing_px=SPACING, elapsed_s=elapsed)
    save("e1_tsfx_holdout.json", out)
    budget_add("e1_score", elapsed)
    print(json.dumps({k: out[k] for k in ("holdout_dti", "ci95", "n_withheld_positives",
                                          "beats_bar", "beats_repo_best")}))
    print("farfield:", json.dumps({k: ff[k] for k in ("holdout_dti", "ci95")}))


def load_names_only():
    """Feature names in the exact order used by load_flat (no grid loading)."""
    from gems.features import build_static_features as _b  # noqa: F401 (names mirror load_flat)
    import json as _j
    lidar_use = ["ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max", "downface_max",
                 "upface_max", "cross_max", "relief", "coh100", "strike"]
    base = ["lidar_" + n for n in lidar_use] + ["lidar_strike_cos2", "lidar_strike_sin2",
            "lidar_dipole", "lidar_face_asym"]
    rad = _j.loads((ROOT / "data/features/geodawn_rad.json").read_text())["channels"]
    ext = _j.loads((ROOT / "data/features/geodawn_extensions.json").read_text())["channels"]
    base += ["rad_" + n for n in rad] + ["mag_" + n if n.startswith("TMI") else "rad_" + n for n in ext]
    base += ["mag_hgrad_s2", "mag_hgrad_s5", "rad_K_grad_s3", "rad_ThK_grad_s3", "lidar_ex_max_s3"]
    base += ["lidar_pol_facing", "lidar_strike_conc", "lidar_facing_instab", "lidar_step_streak"]
    base += ["geo_" + n for n in NEW_BANDS]
    return base


# ---------------------------------------------------------------- E2
def _dots17(foot: np.ndarray) -> list:
    """17 focus rasters as boolean dot masks only (memory-lean; no full float fields)."""
    import rasterio
    from gems.grid import REGISTRY
    from gems.registry import REGISTRY_ENTRIES
    out = []
    for site, fn, score in REGISTRY_ENTRIES:
        p = REGISTRY / fn
        if not p.exists():
            continue
        with rasterio.open(p) as src:
            a = src.read(1)
        dots = (np.nan_to_num(a, nan=0.0) > 0.5) & foot
        out.append(dict(site=site, file=fn, score=score, dots=dots))
        del a
    return out


def run_e2():
    t0 = time.time()
    budget_check()
    if budget_get().get("experiments_run", 0) >= EXPERIMENT_BUDGET:
        raise SystemExit("experiment budget exhausted")
    foot, cat, folds, fidx, _ = base_context()
    z = np.load(WORK / "tsfx_fields.npz")
    fields = [z[f"arr_{i}"].astype(np.float32) for i in range(len(folds))]
    reg = _dots17(foot)
    grid = []
    for prune in (2.0, 4.0, 6.0):
        for n_dots in (37_654, 44_090):
            for sp in (2.8, 3.3):
                dots = []
                for fl, fd in zip(fields, folds):
                    allowed = fd.active & (fl > 0)
                    if prune > 0:
                        allowed = allowed & (ndimage.distance_transform_edt(~fd.visible) > prune)
                    dots.append(poisson_disk_dots(fl, allowed, n_dots, sp))
                s = score_pooled(dots, folds, n_boot=100)
                union = np.zeros(foot.shape, bool)
                for d in dots:
                    union |= d
                worst, worst_file = 0.0, None
                for r in reg:
                    edt = ndimage.distance_transform_edt(~r["dots"])
                    w = float((edt[union] <= 3).sum() / max(int(union.sum()), 1))
                    del edt
                    if w > worst:
                        worst, worst_file = w, r["file"]
                grid.append(dict(prune_px=prune, n_dots=n_dots, spacing_px=sp,
                                 holdout_dti=s["holdout_dti"], ci95=s["ci95"],
                                 max_overlap=worst, worst_file=worst_file,
                                 total_dots=int(union.sum())))
                print(f"  prune={prune} n={n_dots} sp={sp}: DTI={s['holdout_dti']:.4f} "
                      f"[{s['ci95'][0]:.4f},{s['ci95'][1]:.4f}] ov={worst:.3f}", flush=True)
    eligible = [g for g in grid if g["max_overlap"] <= DOT_OVERLAP_MAX]
    best = max(eligible or grid, key=lambda g: g["holdout_dti"])
    elapsed = round(time.time() - t0, 1)
    out = dict(experiment="E2-emission-sweep", field="H-TSFX", grid=grid, best=best,
               any_unique_eligible=bool(eligible), bar=BAR, repo_best=REPO_BEST,
               beats_repo_best=best["holdout_dti"] > REPO_BEST["holdout_dti"], elapsed_s=elapsed)
    save("e2_emission_sweep.json", out)
    budget_add("e2", elapsed, experiments=1)
    print("best:", json.dumps(best))


# ---------------------------------------------------------------- packaging
def _extras() -> list:
    """Sibling/prior published files outside the nine-site registry (git clone, no API quota)."""
    rows = []
    local = [
        ("GEMSDOESASS1-SWGB", ROOT / "swgb" / "downloads" / "gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif"),
        ("GEMSDOESASS1-PBSC", ROOT / "docs" / "downloads" / "gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif"),
    ]
    EXTRA_REG.mkdir(parents=True, exist_ok=True)
    for repo in ("GEMSDOESASS2", "GEMSDOESASS3"):
        tmp = WORK / f"clone_{repo}"
        try:
            if not tmp.exists():
                subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none",
                                "--sparse", f"https://github.com/sassnarep3-star/{repo}.git", str(tmp)],
                               check=True, timeout=300)
            subprocess.run(["git", "-C", str(tmp), "sparse-checkout", "set", "--no-cone",
                            "/docs/downloads/*"], check=True, timeout=120)
            got = 0
            for cand in sorted((tmp / "docs" / "downloads").glob("*.tif")):
                dest = EXTRA_REG / f"{repo}-{cand.name}"
                dest.write_bytes(cand.read_bytes())
                local.append((f"{repo}-{cand.name}", dest))
                got += 1
            if not got:
                rows.append(dict(site=repo, file="docs/downloads/*.tif", missing=True, duplicate=False))
        except Exception as error:  # extras are additive; missing is recorded, never fatal
            rows.append(dict(site=repo, file="docs/downloads/*.tif", missing=True,
                             error=str(error)[:200], duplicate=False))
    for site, p in local:
        if p.exists():
            rows.append(dict(site=site, file=p.name, path=str(p)))
        else:
            rows.append(dict(site=site, file=p.name, missing=True, duplicate=False))
    return rows


def _scan_full(candidate: np.ndarray, footprint: np.ndarray, inventory: dict, stage: str) -> dict:
    """Full 414-raster scan via the shared novelty audit (no early stop), then AMEND-LATTICE-01
    classification: competitive rows gate the verdict; the calibration fixture is measured and
    reported as IR-LATTICE-01."""
    receipt = novelty_audit(candidate, footprint, inventory, ROOT,
                            BRIDGE / "sample_submission.tif", stage=stage, stop_on_duplicate=False)
    local_by_key = {(r["repo"], r["path"]): r["local"] for r in inventory["rasters"]}
    lattice_row, unassessable_rows = None, []
    for row in receipt["comparisons"]:
        if row.get("status") == "unassessable-nonfinite-inside-footprint":
            unassessable_rows.append(row)
        if LATTICE_PATH_HINT in str(row.get("path", "")):
            lattice_row = row
    # AMEND-N2: re-measure unassessable priors with nonfinite -> 0 support (thresholds unchanged).
    import rasterio
    for row in unassessable_rows:
        p = ROOT / local_by_key[(row["repo"], row["path"])]
        with rasterio.open(p) as src:
            old = np.nan_to_num(src.read(1), nan=0.0)
        v_old = old[footprint]
        vals = candidate[footprint]
        rho = spearmanr(vals, v_old).correlation
        old_dots = (old > 0) & footprint
        d = ndimage.distance_transform_edt(~old_dots)
        cand_dots = candidate > 0
        ov = float((d[cand_dots] <= 3).sum() / max(int(cand_dots.sum()), 1))
        del d
        rho_f = float(rho) if rho == rho else 0.0
        row.update(status="compared-amended-n2", spearman=rho_f,
                   directed_overlap_within_3px=ov,
                   canonical_values_sha256=canonical_hash(v_old),
                   duplicate=bool(rho_f > RANK_CORR_MAX or ov > DOT_OVERLAP_MAX))
        del old, v_old, old_dots
    competitive = [r for r in receipt["comparisons"]
                   if str(r.get("status", "")).startswith("compared") and r is not lattice_row]
    comp_dup = [r for r in competitive if r.get("duplicate")]
    max_rho = max((r.get("spearman") for r in competitive if r.get("spearman") is not None), default=None)
    max_ov = max((r.get("directed_overlap_within_3px") for r in competitive
                  if r.get("directed_overlap_within_3px") is not None), default=None)
    comparisons_complete = len(receipt["comparisons"]) == len(inventory["rasters"])
    cleared = bool(comparisons_complete and not comp_dup and max_rho is not None
                   and max_rho <= RANK_CORR_MAX and max_ov is not None and max_ov <= DOT_OVERLAP_MAX)
    return dict(
        stage=stage, registry_size=len(inventory["rasters"]),
        processed=len(receipt["comparisons"]), comparisons_complete=comparisons_complete,
        amended_n2_rows=len(unassessable_rows),
        amendment="AMEND-LATTICE-01 + AMEND-N2 (knowledge/hypotheses_20261030.md)",
        competitive=dict(
            n=len(competitive), max_spearman=max_rho, max_frac_dots_within_3px=max_ov,
            duplicates=[dict(repo=r["repo"], path=r["path"], spearman=r.get("spearman"),
                             overlap=r.get("directed_overlap_within_3px")) for r in comp_dup],
            duplicate=bool(comp_dup), cleared=cleared),
        ir_lattice_01=dict(
            path=lattice_row.get("path") if lattice_row else None,
            measured_overlap_within_3px=lattice_row.get("directed_overlap_within_3px") if lattice_row else None,
            measured_spearman=lattice_row.get("spearman") if lattice_row else None,
            policy="measured, reported, excluded from pass/fail per AMEND-LATTICE-01 — "
                   "witness: the 0.2778 champion itself scores 99.915% against this 5 px grid",
            status="FLAGGED-IRREGULARITY" if lattice_row else "not-present"),
        raw_max_spearman=receipt["max_spearman"],
        raw_max_overlap=receipt["max_directed_overlap_within_3px"],
        candidate_values_sha256=receipt["candidate_values_sha256"],
        thresholds=dict(spearman=RANK_CORR_MAX, overlap=DOT_OVERLAP_MAX, px=3),
        comparison_method=receipt["comparison_method"],
    )


def _extras_scan(candidate_dots: np.ndarray, footprint: np.ndarray, rows: list) -> dict:
    out_rows = []
    n = max(int(candidate_dots.sum()), 1)
    cand_v = candidate_dots.astype(np.float32)[footprint]
    for r in rows:
        if r.get("missing") or not r.get("path"):
            out_rows.append(r)
            continue
        a = np.nan_to_num(read_band(Path(r["path"])), nan=0.0)
        rd = (a > 0.5) & footprint
        if not rd.any():
            out_rows.append(dict(site=r["site"], file=r["file"], empty_prior=True, duplicate=False))
            del a, rd
            continue
        d = ndimage.distance_transform_edt(~rd)
        ov = float((d[candidate_dots] <= 3).sum() / n)
        del d
        rho = spearmanr(cand_v, a[footprint]).correlation
        del a, rd
        rho_f = float(rho) if rho == rho else 0.0
        out_rows.append(dict(site=r["site"], file=r["file"], frac_dots_within_3px=ov,
                             spearman=rho_f, duplicate=bool(rho_f > RANK_CORR_MAX or ov > DOT_OVERLAP_MAX)))
    dup = any(r.get("duplicate") for r in out_rows)
    return dict(rows=out_rows,
                max_spearman=max((r.get("spearman") or 0.0) for r in out_rows),
                max_frac_dots_within_3px=max((r.get("frac_dots_within_3px") or 0.0) for r in out_rows),
                is_duplicate=dup)


def paired_vs_e2(mine: dict, frozen_e2: dict) -> dict:
    """Paired per-fold DTI differences vs the frozen E2-SWGB run (same folds/evaluator)."""
    rows = []
    for a, b in zip(mine["per_fold"], frozen_e2["per_fold"]):
        rows.append(dict(fold=a["fold"], mine=a["dti"], e2=b["dti"], delta=a["dti"] - b["dti"]))
    d = np.array([r["delta"] for r in rows])
    mean = float(d.mean())
    se = float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else float("nan")
    from scipy.stats import t as tdist
    tcrit = float(tdist.ppf(0.975, len(d) - 1)) if len(d) > 1 else float("nan")
    return dict(method="paired per-fold DTI difference vs frozen E2-SWGB on identical folds "
                       "(GEMSASS1-HR-v2-segment); t-interval over 5 folds",
                n_folds=int(len(d)), mean_delta=mean, ci95=[mean - tcrit * se, mean + tcrit * se],
                improves=bool(mean - tcrit * se > 0), rows=rows)


def run_package():
    t0 = time.time()
    budget = budget_check()
    if budget.get("experiments_run", 0) >= EXPERIMENT_BUDGET:
        raise SystemExit("experiment budget exhausted before packaging")
    foot, cat, folds, fidx, _ = base_context()
    e1 = json.loads((EVID / "e1_tsfx_holdout.json").read_text())
    e2 = json.loads((EVID / "e2_emission_sweep.json").read_text())
    canary = json.loads((EVID / "leakage_canary.json").read_text())
    best = e2["best"]

    # --- mean field, accumulated one fold at a time (3 GB sandbox: never hold 5 full grids)
    mean_field = np.zeros(foot.shape, np.float32)
    with np.load(WORK / "tsfx_fields.npz") as z:
        for i in range(len(folds)):
            mean_field += z[f"arr_{i}"].astype(np.float32)
    mean_field /= len(folds)

    # --- protocol dots (the measured artifact) re-derived with the winning config
    protocol_dots = []
    for i, fd in enumerate(folds):
        with np.load(WORK / "tsfx_fields.npz") as z:
            fl = z[f"arr_{i}"].astype(np.float32)
        allowed = fd.active & (fl > 0)
        if best["prune_px"] > 0:
            allowed = allowed & (ndimage.distance_transform_edt(~fd.visible) > best["prune_px"])
        protocol_dots.append(poisson_disk_dots(fl, allowed, best["n_dots"], best["spacing_px"]))
        del fl
    s_protocol = score_pooled(protocol_dots, folds)
    s_farfield = score_pooled_farfield(protocol_dots, folds)
    frozen_e2 = json.loads((ROOT / "evidence" / "swgb" / "e2_swgb_holdout.json").read_text())
    paired = paired_vs_e2(s_protocol, frozen_e2)

    # --- shipped emission: the champion's proven live edit — full published catalogue, > 2 px
    full_cat_excl = ndimage.distance_transform_edt(~cat) > 2.0
    allowed_ship = foot & full_cat_excl
    shipped_dots = poisson_disk_dots(mean_field, allowed_ship, best["n_dots"], best["spacing_px"])
    del allowed_ship, full_cat_excl
    shipped_file_holdout = score_pooled([shipped_dots] * len(folds), folds, n_boot=100)
    print("protocol per-fold dots:", [d["emitted"] for d in s_protocol["per_fold"]],
          "shipped dots:", int(shipped_dots.sum()), flush=True)

    # --- novelty: surface pre-placement (mean field), then final shipped dots
    inventory = json.loads((ROOT / "registry" / "focus_inventory.json").read_text())
    print("novelty stage: surface ...", flush=True)
    t_scan = time.time()
    surface_receipt = _scan_full(np.where(foot, mean_field, 0.0), foot, inventory, "surface")
    save("novelty_surface.json", surface_receipt)
    print("  competitive:", json.dumps(surface_receipt["competitive"]),
          f"({time.time()-t_scan:.0f}s)", flush=True)
    del mean_field
    if not surface_receipt["competitive"]["cleared"]:
        budget_add("package_surface_stop", time.time() - t0)
        raise SystemExit("STOP: surface duplicate vs competitive registry — no placement")

    print("novelty stage: dots ...", flush=True)
    t_scan = time.time()
    ship_field = shipped_dots.astype(np.float32)
    dots_receipt = _scan_full(ship_field, foot, inventory, "dots")
    extras_rows = _extras()
    extras_receipt = _extras_scan(shipped_dots, foot, extras_rows)
    save("novelty_dots.json", dots_receipt)
    save("novelty_extras.json", extras_receipt)
    print("  competitive:", json.dumps(dots_receipt["competitive"]),
          f"({time.time()-t_scan:.0f}s)", flush=True)
    print("  extras:", json.dumps({k: extras_receipt[k] for k in
                                   ("max_spearman", "max_frac_dots_within_3px", "is_duplicate")}), flush=True)
    del ship_field

    novelty_ok = bool(surface_receipt["competitive"]["cleared"]
                      and dots_receipt["competitive"]["cleared"]
                      and not extras_receipt["is_duplicate"])
    canary_pass = not canary["flagged_over_0p90"]
    beats_bar = s_protocol["holdout_dti"] > BAR["holdout_dti"]
    beats_repo_best = s_protocol["holdout_dti"] > REPO_BEST["holdout_dti"]
    paired_ok = paired["improves"]

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    digest = canonical_hash(shipped_dots.astype(np.float32)[foot])[:12]
    name = f"gemsass1-tsfx-{int(shipped_dots.sum())}dots-{ts}-{digest}-zeros"
    note = (f"H-TSFX strain+seismic+scarp learner {int(shipped_dots.sum())}d prune2fullcat; "
            f"HOLDOUT-DTI {s_protocol['holdout_dti']:.4f}; unique; IR-LATTICE-01 flagged")
    if len(note) > 140:
        raise ValueError(f"note too long: {len(note)}")

    write_receipt = None
    tif = SITE_DOWNLOADS / f"{name}.tif"
    if novelty_ok and canary_pass:
        write_receipt = write_submission(shipped_dots.astype(np.float32), foot, tif,
                                         catalogue=cat, note=note,
                                         meta=dict(lane="H-TSFX", evidence="evidence/tsfx/run_card.json",
                                                   protocol_holdout=s_protocol["holdout_dti"],
                                                   amendment="AMEND-LATTICE-01"))
        validator_ok = write_receipt["all_checks_passed"]
    else:
        validator_ok = False

    promote = bool(canary_pass and beats_repo_best and novelty_ok and validator_ok and paired_ok)
    elapsed = round(time.time() - t0, 1)

    card = dict(
        schema_version=1,
        generated_utc=datetime.now(timezone.utc).isoformat(),
        lane="H-TSFX",
        hypothesis="Unmapped Holocene fault scarps in the NW Great Basin sit where geodetic strain rate, "
                   "instrumental seismicity and basement-step context coincide with lidar scarp polarity "
                   "morphology; a segment-withheld learner over those layers recovers fault scarps that "
                   "the visible USGS/INGENIOUS catalogue does not contain.",
        mechanism="HistGradientBoosting on 55 features (SWGB's 28 + 19 GeoDAWN/strain/seismicity/"
                  "basement/conductivity/detrended bands + 4 polarity-coherence transforms + 4 "
                  "visible-only catalogue-context features), 5 segment-withheld folds, hyper-parameters "
                  "identical to frozen E2-SWGB (clean feature-set ablation); Poisson-disk emission.",
        named_non_fault_mimic="Fluvial terrace risers and canal banks (facing follows drainage, not "
                              "regional dip); pluvial Lake Lahontan shorelines; lithologic contacts and "
                              "flight-line seams; seismicity-distance bands follow population/instrument "
                              "coverage; interpolated geodetic strain-rate is a smooth prior, not a scarp.",
        evidence_classes=dict(
            holdout_dti="HOLDOUT-DTI", evaluator=EVALUATOR_VERSION,
            n_withheld_positives=s_protocol["n_withheld_positives"],
            projection_note="No leaderboard projection is recorded as a score; no ORGANIZER-CONFIRMED "
                            "receipt exists in this session.",
        ),
        holdout_dti=dict(label="HOLDOUT-DTI", evaluator=EVALUATOR_VERSION,
                         protocol_dots=s_protocol, farfield=s_farfield,
                         shipped_file_diagnostic=shipped_file_holdout,
                         protocol_config=dict(prune_px_vs_visible=best["prune_px"],
                                              n_dots=best["n_dots"], spacing_px=best["spacing_px"])),
        bars=dict(promote_bar=BAR, repo_holdout_best=REPO_BEST, e2_as_evaluated=E2_AS_EVALUATED,
                  beats_promote_bar=beats_bar, beats_repo_best=beats_repo_best),
        paired_vs_frozen_e2=paired,
        canary=dict(passed=canary_pass, flagged=canary["flagged_over_0p90"],
                    max_mean_auc=max(canary["auc_mean_over_folds"].values())),
        correlation_overlap_vs_registry=dict(
            surface=surface_receipt["competitive"], dots=dots_receipt["competitive"],
            ir_lattice_01=dots_receipt["ir_lattice_01"],
            ir_lattice_01_surface=surface_receipt["ir_lattice_01"], extras=extras_receipt,
            amendment="AMEND-LATTICE-01 (lattice witness: the 0.2778 champion = 99.915% vs the 5 px grid)"),
        raster_sha256=write_receipt["sha256"] if write_receipt else None,
        validator_output=({k: write_receipt["checks"][k] for k in write_receipt["checks"]}
                          | dict(all_checks_passed=validator_ok,
                                 positive_pixels=write_receipt["positive_pixels"],
                                 min=write_receipt["min"], max=write_receipt["max"])
                          if write_receipt else {"status": "not written — gates failed"}),
        submission_name=f"{name}.tif" if write_receipt else None,
        submission_zip=(write_receipt["zip"]["path"].rsplit("/", 1)[-1] if write_receipt else None),
        submission_note=note if write_receipt else None,
        planned_submission_name=f"{name}.tif", planned_note=note, note_length=len(note),
        artifact=str(tif.relative_to(ROOT)) if write_receipt else None,
        budget=dict(**{k: budget.get(k) for k in ("experiments_run", "cumulative_seconds")},
                    seconds_budget=BUDGET_SECONDS, experiment_budget=EXPERIMENT_BUDGET,
                    stage_seconds=elapsed),
        slot=dict(used=0, selector_implemented=False,
                  policy="promotion to a real slot is a separate selector step within the weekly cap"),
        verdict="promote" if promote else "negative",
        promote_reasons=dict(canary_pass=canary_pass, beats_promote_bar=beats_bar,
                             beats_repo_best=beats_repo_best, novelty_ok=novelty_ok,
                             validator_ok=validator_ok, paired_improves=paired_ok),
        ok_to_submit=promote,
        amendments=["AMEND-LATTICE-01", "AMEND-N2"],
        limitations=[
            "HOLDOUT-DTI is a hide-and-recover gate, not a leaderboard projection; no local instrument "
            "ranks within the 0.24-0.28 H19-5 family (Spearman -0.08, evidence/swgb/holdout_calibration.json).",
            "No DrivenData auth: owner-reported ledger scores stay OWNER-REPORT; the 0.4413/0.3195 "
            "leaderboard claims conflict and remain unverified.",
            "Registry scope = 414 TIFFs in nine public focus repos + sibling files measured; other "
            "competitors' private submissions are not covered.",
            "IR-LATTICE-01 remains a flagged irregularity by design: the raw 3 px overlap vs the "
            "calibration grid is reported, excluded from pass/fail only under AMEND-LATTICE-01.",
        ],
    )
    save("run_card.json", card)
    budget_add("package", elapsed)
    print(json.dumps(dict(verdict=card["verdict"], ok_to_submit=promote,
                          holdout=s_protocol["holdout_dti"], ci=s_protocol["ci95"],
                          farfield=s_farfield["holdout_dti"], paired_mean=paired["mean_delta"],
                          paired_ci=paired["ci95"], novelty_ok=novelty_ok,
                          submission=card["submission_name"]), indent=2))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd != "canary" and not (EVID / "leakage_canary.json").exists():
        raise SystemExit("run canary first")
    if cmd == "canary":
        ok = run_canary()
        raise SystemExit(0 if ok else 2)
    canary = json.loads((EVID / "leakage_canary.json").read_text())
    if canary["flagged_over_0p90"]:
        raise SystemExit("canary flagged; stop")
    if cmd == "e1":
        run_e1()
    elif cmd == "e1score":
        run_e1score()
    elif cmd == "e2":
        e1 = json.loads((EVID / "e1_tsfx_holdout.json").read_text())
        if not e1["beats_bar"]:
            raise SystemExit("E1 did not beat the 0.1011 promote bar; E2 sweep not authorized")
        run_e2()
    elif cmd == "package":
        if (EVID / "run_card.json").exists():
            raise SystemExit("frozen run card already exists; do not overwrite")
        run_package()
    else:
        raise SystemExit("usage: run_tsfx.py canary|e1|e1score|e2|package")


if __name__ == "__main__":
    main()
