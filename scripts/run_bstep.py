#!/usr/bin/env python3
"""H-BSTEP lane (basement-step concordance learner) — session 2026-10-31.

Preregistration: knowledge/hypotheses_20261031.md (written before any run).
Budget: 3 experiments / 2 h, tracked in evidence/bstep/budget.json.

Stages (run in order):
  canary  : every input feature alone vs withheld truth on all 5 folds; AUC > 0.90 stops the lane.
  e1      : H-BSTEP segment-withheld learner (E2-SWGB hyper-parameters, augmented feature set)
            -> HOLDOUT-DTI on GEMSASS1-HR-v2-segment at the comparable operating point
            (n=37,654 / 2.8 px / >2 px catalogue exclusion). Bars: 0.1011 (family base),
            0.1586/0.1591 (repo incumbents).
  e2      : emission sensitivity on the saved E1 fields: {2,6} px x {37,654, 44,090} plus the
            preregistered anti-collision variant; pooled + far-field HOLDOUT-DTI, quick
            per-raster overlap vs the competitive family set. Shipped cell is fixed a priori
            at 37,654 / 2.8 px / >6 px; the sweep is sensitivity evidence only.
  package : single full-catalogue model (the proper live field), shipped-cell emission,
            surface novelty before placement + dots novelty after placement (414-raster frozen
            registry + every repo prior; AMEND-LATTICE-01 / AMEND-N2), fail-closed writer
            (zeros outside footprint), validator, run card + release.json.

Shared tools reused unchanged: src/gems/{grid,holdout,features,emission,submission,metric},
scripts/novelty.py, vendor/gems57/submission_writer.py, vendor/gems57/uniqueness.py.
Lane-local helpers (concordance transforms, tiered emission) live here; no shared tool is forked.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from gems.grid import (BRIDGE, DATA, load_catalogue, load_footprint, read_band,  # noqa: E402
                       sha256_file)
from gems.holdout import (EVALUATOR_VERSION, auc_binary, build_folds, catalogue_features,  # noqa: E402
                          score_pooled, score_pooled_farfield)
from gems.features import build_static_features  # noqa: E402
from gems.emission import poisson_disk_dots, catalogue_exclusion  # noqa: E402
from gems.submission import validate as format_validate  # noqa: E402
from vendor.gems57.uniqueness import dot_overlap  # noqa: E402

BAR = dict(name="gems25-dotted-h19-5-d2-8 (0.2600 family base, un-pruned)",
           holdout_dti=0.1011, ci95=[0.0956, 0.1072],
           evidence="evidence/swgb/holdout_calibration.json")
REPO_BEST = dict(name="E2-SWGB emitted, prune 4 px, 44,090 dots (repo holdout best)",
                 holdout_dti=0.1591, ci95=[0.1538, 0.1639],
                 evidence="evidence/swgb/e3_prune_sweep_e2.json")
E2_SWGB = dict(name="E2-SWGB as evaluated", holdout_dti=0.1586, ci95=[0.1519, 0.1649],
               evidence="evidence/swgb/e2_swgb_holdout.json")

N_SHIP = 37_654          # the only live-evidenced dot count (champion ladder)
SPACING = 2.8
PRUNE_COMPARABLE = 2.0   # comparable protocol cell (every prior HOLDOUT-DTI number)
PRUNE_SHIP = 6.0         # preregistered shipped cell (600 m far-field exclusion at emission)

EVID = ROOT / "evidence" / "bstep"
WORK = ROOT / "work" / "bstep"
BUDGET_SECONDS = 7200
EXPERIMENT_BUDGET = 3

# 19-band derived stack (identical mapping to scripts/run_tsfx.py NEW_BANDS)
GEO_BANDS = {
    "mag_anom": 1, "rtp": 2, "tmi_hg": 3, "geod_2ndinv": 4, "iso_grav_anom_slope": 5,
    "tc": 6, "geod_shearrate": 7, "geod_dilaterate": 8, "tmi_vg": 9, "deq_n100a15": 10,
    "iso_grav_anom_vg": 11, "det_elev": 12, "iso_grav_anom": 13, "tmi": 14,
    "depth_to_base_surf": 15, "ieq_n100a15": 16, "cond_surf": 17, "iso_grav_anom_hg": 18,
    "det_elev_slope": 19,
}
CTX = ["cat_logdist", "cat_logtip", "cat_dens", "cat_strike_agree"]

# ridge sources for the concordance transforms: name -> (band keys, sigma)
RIDGE_SPECS = {
    "step": (["depth_to_base_surf"], 3.0),      # H-BSTEP: basement depth step
    "grav": (["iso_grav_anom_hg"], 2.0),        # gravity horizontal-gradient maxima
    "mag": (["tmi_hg"], 2.0),                   # magnetic horizontal-gradient maxima
    "cond": (["cond_surf"], 3.0),               # H-CONDUCTIVE-GOUGE: conductivity edge
    "dil": (["geod_dilaterate"], 4.0),          # H-STRAIN-BOUNDARY: dilatation sign-change lines
    "shear": (["geod_shearrate"], 3.0),
    "slope": (["det_elev_slope"], 2.0),
    "quakes": (["ieq_n100a15", "deq_n100a15"], 3.0),   # H-QUAKE-CURV (canary-watched)
}
NEW_FEATURES = ["bst_step_ridge", "bst_grav_ridge", "bst_mag_ridge", "bst_triple",
                "bst_step_grav", "bst_step_mag", "gouge_cond_step", "strain_edge",
                "quake_curv", "relay_bridge"]


def save(name: str, obj) -> None:
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / name).write_text(json.dumps(obj, indent=2, allow_nan=False, default=float) + "\n")


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


def budget_check() -> dict:
    p = EVID / "budget.json"
    b = json.loads(p.read_text()) if p.exists() else dict(cumulative_seconds=0.0, experiments_run=0)
    if b.get("cumulative_seconds", 0.0) > BUDGET_SECONDS:
        raise SystemExit("two-hour budget exhausted")
    if b.get("experiments_run", 0) >= EXPERIMENT_BUDGET:
        raise SystemExit("experiment budget exhausted")
    return b


def rank01_vec(v: np.ndarray) -> np.ndarray:
    """Rank-normalise a footprint vector to [0,1]."""
    out = np.empty(v.size, np.float32)
    order = np.argsort(v, kind="stable")
    out[order] = np.arange(v.size, dtype=np.float32) / max(v.size - 1, 1)
    return out


def _gm_grid(a: np.ndarray, sigma: float) -> np.ndarray:
    g = ndimage.gaussian_filter(a.astype(np.float32), sigma)
    return np.hypot(ndimage.sobel(g, axis=0), ndimage.sobel(g, axis=1)).astype(np.float32)


def concordance_features(foot: np.ndarray, fidx: np.ndarray) -> dict:
    """H-BSTEP / H-CONDUCTIVE-GOUGE / H-STRAIN-BOUNDARY / H-QUAKE-CURV / H-RELAYBRIDGE
    transforms (label-free, catalogue-independent). Nodata (NaN) is mean-filled inside the
    footprint before ridge filtering; outputs are rank-normalised footprint vectors."""
    import rasterio
    fshape = foot.shape
    ridge: dict[str, np.ndarray] = {}
    with rasterio.open(ROOT / "data" / "official" / "training_features.tif") as s:
        nodata = s.nodata
        for rname, (keys, sigma) in RIDGE_SPECS.items():
            acc = None
            for k in keys:
                a = s.read(GEO_BANDS[k]).astype(np.float32)
                bad = ~np.isfinite(a)
                if nodata is not None:
                    bad |= a == np.float32(nodata)
                bad |= np.abs(a) >= 1e30          # sentinels beyond the physical range
                m = ~bad & foot
                fill = float(a[m].mean(dtype=np.float64)) if m.any() else 0.0
                a = np.where(m, a, fill)
                gm = _gm_grid(a, sigma)
                acc = gm if acc is None else acc + gm
                del a, gm, bad, m
            vec = acc.ravel()[fidx]
            ridge[rname] = rank01_vec(np.nan_to_num(vec, nan=0.0))
            del acc, vec
    step, grav, mag = ridge["step"], ridge["grav"], ridge["mag"]
    cond, dil, shear, slope, quakes = (ridge["cond"], ridge["dil"], ridge["shear"],
                                       ridge["slope"], ridge["quakes"])
    out = {
        "bst_step_ridge": step,
        "bst_grav_ridge": grav,
        "bst_mag_ridge": mag,
        "bst_triple": step * grav * mag,
        "bst_step_grav": step * grav,
        "bst_step_mag": step * mag,
        "gouge_cond_step": cond * step,
        "strain_edge": dil * shear * slope,
        "quake_curv": quakes * slope,
    }
    del ridge
    # H-RELAYBRIDGE: polarity-flip x strike concordance x cohesion (lidar scarp stack)
    feats_full, valid = build_static_features()
    step_l = feats_full["lidar_step_max"]
    asym = feats_full["lidar_face_asym"]
    cos2, sin2 = feats_full["lidar_strike_cos2"], feats_full["lidar_strike_sin2"]
    coh = feats_full["lidar_coh100"]
    m = valid & (step_l > 0)
    if not m.any():
        m = valid
    thr = float(np.percentile(step_l[m], 80))
    w = (m & (step_l >= thr)).astype(np.float32)
    del m
    g = lambda a, s=4.0: ndimage.gaussian_filter(a.astype(np.float32), s)  # noqa: E731
    facing = g(asym * w)
    c, s_, n = g(cos2 * w), g(sin2 * w), g(w)
    conc = np.minimum(np.hypot(c, s_) / np.maximum(n, 1e-3), 1.0)
    flip = np.maximum(g(np.abs(asym) * w) - np.abs(facing), 0.0)
    del facing, c, s_, n, w, cos2, sin2, asym, step_l
    relay = (flip * conc * np.maximum(coh, 0.0)).ravel()[fidx]
    del flip, conc, coh, feats_full
    out["relay_bridge"] = rank01_vec(np.nan_to_num(relay, nan=0.0))
    for k in list(out):
        out[k] = np.nan_to_num(out[k].astype(np.float32), nan=0.0)
    return out


def load_flat(foot: np.ndarray, fidx: np.ndarray) -> dict:
    """Static lidar/GeoDAWN u8-stack features + raw 19-band vectors + concordance transforms."""
    feats_full, valid = build_static_features()
    flat = {}
    for n in list(feats_full):
        flat[n] = feats_full[n].ravel()[fidx].astype(np.float16)
        del feats_full[n]
    del feats_full
    import rasterio
    with rasterio.open(ROOT / "data" / "official" / "training_features.tif") as s:
        nodata = s.nodata
        for name, idx in GEO_BANDS.items():
            a = s.read(idx).astype(np.float32)
            bad = ~np.isfinite(a)
            if nodata is not None:
                bad |= a == np.float32(nodata)
            bad |= np.abs(a) >= 1e30
            a[bad] = np.nan
            a[~foot] = np.nan
            flat["geo_" + name] = a.ravel()[fidx].astype(np.float32)
            del a, bad
    flat.update(concordance_features(foot, fidx))
    return flat


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


def quick_family_registry() -> list[dict]:
    """Competitive family set for cheap per-raster checks in E1/E2: the 17 scored REGISTRY_ENTRIES
    basenames + the nine-site best files + the calibration lattice (matched inside the frozen
    inventory; AMEND-LATTICE-01 applies later at the full scan)."""
    inv = json.loads((ROOT / "registry" / "focus_inventory.json").read_text())
    want = {
        "gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
        "gems24-gvc1-negative-geothermal-lineament-submod-20261025-abe8e51c719d-zeros.tif",
        "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
        "gems25-h66-mgd-flank-sapd3-0-k3p5-20261025-da617550a0e9-zeros.tif",
        "gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
        "gems27-h29-hydrothermal-piedmont-celf-20261025-511898747886-allfinite.tif",
        "gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan.tif",
        "gems28-h32-1-prethin-tip-euler-d2-8-20261003-31e35eee884e-nan.tif",
        "gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif",
        "gems28-h38-1-hf-euler-r30-r1-20261003-56a9f473edc7-nan.tif",
        "gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif",
        "gems30-MSDB1-edge44090-20261025-e7856ec3f14a.tif",
        "gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
        "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
        "GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
        "gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
        "gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca-nanoutside.tif",
    }
    rows = []
    for item in inv["rasters"]:
        base = item["path"].rsplit("/", 1)[-1]
        if base in want or "lattice" in item["path"].lower():
            p = ROOT / item["local"]
            if p.exists():
                rows.append(dict(path=item["path"], file=base, raster=p))
    return rows


def quick_audit(pred_dots: np.ndarray, foot: np.ndarray, family: list[dict],
                sample: int = 400_000, seed: int = 0) -> dict:
    """Per-raster gate values vs the competitive family set (exact dot overlap; sampled rho)."""
    from scipy.stats import spearmanr
    rng = np.random.default_rng(seed)
    fy, fx = np.nonzero(foot)
    sel = rng.choice(fy.size, size=min(sample, fy.size), replace=False)
    mine = np.where(foot, pred_dots.astype(np.float32), 0.0)
    rows = []
    for r in family:
        old = read_band(r["raster"]).astype(np.float32)
        old = np.where(foot, np.nan_to_num(old, nan=0.0), 0.0)
        ov = dot_overlap(mine, old)
        a = mine[fy[sel], fx[sel]]
        b = old[fy[sel], fx[sel]]
        rho = float(spearmanr(a, b).correlation) if np.std(b) > 0 and np.std(a) > 0 else 0.0
        if rho != rho:
            rho = 0.0
        rows.append(dict(path=r["path"], spearman=rho, directed_overlap_within_3px=float(ov),
                         is_lattice="lattice" in r["path"].lower(),
                         registry_dots=int((old > 0).sum())))
    comp = [r for r in rows if not r["is_lattice"]]
    worst = max(comp, key=lambda r: r["directed_overlap_within_3px"], default=None)
    return dict(max_spearman=max((r["spearman"] for r in comp), default=0.0),
                max_overlap=worst["directed_overlap_within_3px"] if worst else 0.0,
                worst_path=worst["path"] if worst else None,
                over_limit=[r["path"] for r in comp
                            if r["directed_overlap_within_3px"] > 0.70 or r["spearman"] > 0.90],
                rows=rows)


def tiered_dots(field: np.ndarray, allowed_t1: np.ndarray, allowed_t2: np.ndarray,
                n_dots: int, min_dist_px: float, seeds: np.ndarray | None = None,
                max_candidates: int = 600_000) -> np.ndarray:
    """Greedy priority Poisson-disk with a preregistered two-tier fallback:
    tier-1 candidates (allowed_t1) are exhausted by field rank first; only then tier-2
    (allowed_t2) fills the remainder. Optional seed dots pre-occupy the spacing map
    (used to keep spacing across a fallback pass)."""
    H, W = field.shape
    v1 = np.where(allowed_t1, field, -np.inf).ravel()
    v2 = np.where(allowed_t2 & ~allowed_t1, field, -np.inf).ravel()
    o1 = np.argsort(-v1, kind="stable")[:max_candidates]
    o1 = o1[np.isfinite(v1[o1])]
    o2 = np.argsort(-v2, kind="stable")[:max_candidates]
    o2 = o2[np.isfinite(v2[o2])]
    order = np.concatenate([o1, o2])
    r = int(np.ceil(min_dist_px))
    occupied = np.zeros((H + 2 * r, W + 2 * r), bool)
    dy, dx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (dy * dy + dx * dx) < (min_dist_px * min_dist_px)
    out = np.zeros(H * W, bool)
    taken = 0
    if seeds is not None:
        for y, x in np.argwhere(seeds):
            occupied[y + r, x + r] = True
            occupied[y:y + 2 * r + 1, x:x + 2 * r + 1] |= disk
            out[y * W + x] = True
            taken += 1
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


def fold_dots(fields, folds, n_dots: int, prune_px: float, spacing: float = SPACING):
    dots = []
    for fl, fd in zip(fields, folds):
        allowed = fd.active & catalogue_exclusion(fd.visible, prune_px) & (fl > 0)
        dots.append(poisson_disk_dots(fl, allowed, n_dots, spacing))
    return dots


# ----------------------------------------------------------------------------- canary
def run_canary():
    t0 = time.time()
    foot, cat = load_footprint(), load_catalogue()
    folds, n_seg = build_folds(cat, foot)
    fidx = np.flatnonzero(foot.ravel())
    flat = load_flat(foot, fidx)
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
               folds=list(range(len(folds))), n_segments=n_seg, n_features=len(agg),
               auc_mean_over_folds=agg, auc_per_fold=rows, flagged_over_0p90=flagged,
               excluded_by_design=["dist_known_fault_px (label-derived column, never loaded)"],
               canary_pass=not flagged, elapsed_s=elapsed)
    save("leakage_canary.json", out)
    budget_add("canary", elapsed)
    for n, v in sorted(agg.items(), key=lambda kv: -kv[1])[:15]:
        print(f"  {n:28s} meanAUC={v:.3f}")
    print("flagged (>0.90):", flagged or "none")
    return not flagged


# ----------------------------------------------------------------------------- E1
def run_e1():
    from sklearn.ensemble import HistGradientBoostingClassifier
    t0 = time.time()
    budget_check()
    foot, cat = load_footprint(), load_catalogue()
    folds, _ = build_folds(cat, foot)
    fidx = np.flatnonzero(foot.ravel())
    flat = load_flat(foot, fidx)
    names = sorted(flat.keys()) + CTX
    rng = np.random.default_rng(7)
    family = quick_family_registry()
    fields, dots_by_fold, rows = [], [], []
    for fd in folds:
        flat_all = add_ctx_flat(fd, foot, fidx, flat)
        guard = ndimage.binary_dilation(fd.test_truth, iterations=3)
        train_region = fd.active & ~guard
        pos = (fd.train_truth & train_region).ravel()[fidx]
        negpool = (train_region & ~ndimage.binary_dilation(fd.train_truth, iterations=2)).ravel()[fidx]
        neg_ids = rng.choice(np.flatnonzero(negpool), size=min(600_000, int(negpool.sum())), replace=False)
        pos_ids = np.flatnonzero(pos)
        X = np.vstack([np.stack([flat_all[n][pos_ids] for n in names], axis=1),
                       np.stack([flat_all[n][neg_ids] for n in names], axis=1)]).astype(np.float32)
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
            prob[ch] = clf.predict_proba(np.stack([flat_all[n][ch] for n in names], axis=1).astype(np.float32))[:, 1]
        field = np.zeros(foot.size, np.float32)
        field[fidx] = prob
        field = field.reshape(foot.shape)
        del flat_all, prob
        fields.append(field.astype(np.float16))
        allowed = fd.active & catalogue_exclusion(fd.visible, PRUNE_COMPARABLE) & (field > 0)
        d = poisson_disk_dots(field, allowed, N_SHIP, SPACING)
        dots_by_fold.append(d)
        qa = quick_audit(d, foot, family)
        rows.append(dict(fold=fd.f, dots=int(d.sum()), quick_overlap=qa))
        print(f"  fold {fd.f}: dots={int(d.sum())} max_ov={qa['max_overlap']:.3f} "
              f"max_rho={qa['max_spearman']:.3f} {time.time()-t0:.0f}s", flush=True)
    s = score_pooled(dots_by_fold, folds)
    ff = score_pooled_farfield(dots_by_fold, folds)
    np.savez_compressed(WORK / "e1_fields.npz", *[f.astype(np.float32) for f in fields])
    out = dict(experiment="E1-H-BSTEP-concordance-learner",
               hypothesis="basement/grav/mag edge-concordance + relay + gouge + strain + quake transforms inside the segment-withheld learner (knowledge/hypotheses_20261031.md)",
               evaluator=EVALUATOR_VERSION, n_withheld_positives=s["n_withheld_positives"],
               holdout_dti=s["holdout_dti"], ci95=s["ci95"], per_fold=s["per_fold"],
               farfield=ff["holdout_dti"], farfield_ci95=ff["ci95"],
               n_dots=N_SHIP, spacing_px=SPACING, prune_px=PRUNE_COMPARABLE,
               beats_bar=s["holdout_dti"] > BAR["holdout_dti"],
               beats_repo_best=s["holdout_dti"] > REPO_BEST["holdout_dti"],
               fold_novelty=rows, bar=BAR, repo_best=REPO_BEST, e2_swgb=E2_SWGB,
               n_features=len(names), new_features=NEW_FEATURES,
               elapsed_s=round(time.time() - t0, 1))
    save("e1_holdout.json", out)
    budget_add("e1", round(time.time() - t0, 1), experiments=1)
    print(json.dumps({k: out[k] for k in ("holdout_dti", "ci95", "farfield",
                                          "beats_bar", "beats_repo_best")}))
    return out


# ----------------------------------------------------------------------------- E2
def run_e2():
    t0 = time.time()
    budget_check()
    foot, cat = load_footprint(), load_catalogue()
    folds, _ = build_folds(cat, foot)
    z = np.load(WORK / "e1_fields.npz")
    fields = [z[f"arr_{i}"].astype(np.float32) for i in range(len(folds))]
    family = quick_family_registry()
    grid = []
    for n_dots in (N_SHIP, 44_090):
        for prune in (2.0, 6.0):
            dots = fold_dots(fields, folds, n_dots, prune)
            s = score_pooled(dots, folds, n_boot=100)
            ff = score_pooled_farfield(dots, folds, n_boot=100)
            qa = max((quick_audit(d, foot, family) for d in dots),
                     key=lambda q: q["max_overlap"])
            grid.append(dict(n_dots=n_dots, prune_px=prune, holdout_dti=s["holdout_dti"],
                             ci95=s["ci95"], farfield=ff["holdout_dti"],
                             quick_max_overlap=qa["max_overlap"], quick_max_rho=qa["max_spearman"],
                             quick_over_limit=qa["over_limit"]))
            print(f"  n={n_dots} prune={prune}: {s['holdout_dti']:.4f} "
                  f"ff {ff['holdout_dti']:.4f} ov {qa['max_overlap']:.3f}", flush=True)
    # preregistered anti-collision variant at the shipped cell (R* = rasters over the limit on the
    # plain shipped cell, measured above; tiered emission, both tiers scored)
    plain_ship = next(g for g in grid if g["n_dots"] == N_SHIP and g["prune_px"] == PRUNE_SHIP)
    offender_paths = set(plain_ship["quick_over_limit"])
    ac_union = None
    if offender_paths:
        ac_union = np.zeros(foot.shape, bool)
        for r in family:
            if r["path"] in offender_paths:
                ac_union |= read_band(r["raster"]) > 0
    ac_dots, ac_notes = [], []
    for fl, fd in zip(fields, folds):
        allowed = fd.active & catalogue_exclusion(fd.visible, PRUNE_SHIP) & (fl > 0)
        if ac_union is not None:
            halo = ndimage.distance_transform_edt(~ac_union) <= 3.0
            t1 = allowed & ~halo
            d = tiered_dots(fl.astype(np.float32), t1, allowed, N_SHIP, SPACING)
        else:
            d = poisson_disk_dots(fl.astype(np.float32), allowed, N_SHIP, SPACING)
        ac_dots.append(d)
        ac_notes.append(int(d.sum()))
    s = score_pooled(ac_dots, folds, n_boot=100)
    ff = score_pooled_farfield(ac_dots, folds, n_boot=100)
    qa = max((quick_audit(d, foot, family) for d in ac_dots), key=lambda q: q["max_overlap"])
    ac_cell = dict(n_dots=N_SHIP, prune_px=PRUNE_SHIP, variant="anti_collision",
                   holdout_dti=s["holdout_dti"], ci95=s["ci95"], farfield=ff["holdout_dti"],
                   quick_max_overlap=qa["max_overlap"], quick_max_rho=qa["max_spearman"],
                   quick_over_limit=qa["over_limit"], offenders_union=sorted(offender_paths),
                   dots_per_fold=ac_notes)
    out = dict(experiment="E2-emission-sensitivity", evaluator=EVALUATOR_VERSION,
               selection_rule=("shipped cell fixed a priori at n=37,654 / 2.8 px / >6 px "
                               "catalogue exclusion (knowledge/hypotheses_20261031.md §2); "
                               "sweep = sensitivity evidence, never selection"),
               grid=grid, anti_collision_cell=ac_cell, bar=BAR, repo_best=REPO_BEST,
               elapsed_s=round(time.time() - t0, 1))
    save("e2_emission.json", out)
    budget_add("e2", round(time.time() - t0, 1), experiments=1)
    print("shipped cell (fixed):", plain_ship)
    print("anti-collision:", {k: ac_cell[k] for k in ("holdout_dti", "quick_max_overlap", "quick_over_limit")})
    return out


# ----------------------------------------------------------------------------- package
def run_package():
    from sklearn.ensemble import HistGradientBoostingClassifier
    t0 = time.time()
    foot, cat = load_footprint(), load_catalogue()
    folds, _ = build_folds(cat, foot)
    fidx = np.flatnonzero(foot.ravel())
    flat = load_flat(foot, fidx)

    # single full-catalogue model: all catalogue pixels positive, full-catalogue context
    full_catf = catalogue_features(cat, foot)
    strike_deg = (flat["lidar_strike"].astype(np.float32) - 1.0) / 254.0 * 180.0
    infer = dict(flat)
    infer["cat_logdist"] = np.log1p(full_catf["dist_vis"].ravel()[fidx]).astype(np.float32)
    infer["cat_logtip"] = np.log1p(full_catf["tip_vis"].ravel()[fidx]).astype(np.float32)
    infer["cat_dens"] = full_catf["dens_vis"].ravel()[fidx].astype(np.float32)
    infer["cat_strike_agree"] = np.cos(2 * (np.deg2rad(strike_deg) - full_catf["strike_vis"].ravel()[fidx])).astype(np.float32)
    del full_catf, strike_deg
    names = sorted(flat.keys()) + CTX
    rng = np.random.default_rng(7)
    pos = cat.ravel()[fidx]
    negpool = (~ndimage.binary_dilation(cat, iterations=2)).ravel()[fidx]
    neg_ids = rng.choice(np.flatnonzero(negpool), size=600_000, replace=False)
    pos_ids = np.flatnonzero(pos)
    X = np.vstack([np.stack([infer[n][pos_ids] for n in names], axis=1),
                   np.stack([infer[n][neg_ids] for n in names], axis=1)]).astype(np.float32)
    y = np.r_[np.ones(len(pos_ids)), np.zeros(len(neg_ids))]
    w = np.r_[np.full(len(pos_ids), len(neg_ids) / max(len(pos_ids), 1)), np.ones(len(neg_ids))]
    clf = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.08, max_leaf_nodes=31,
                                         min_samples_leaf=100, l2_regularization=1.0, random_state=0)
    clf.fit(X, y, sample_weight=w)
    del X
    prob = np.zeros(fidx.size, np.float32)
    for c in range(0, fidx.size, 400_000):
        ch = slice(c, c + 400_000)
        prob[ch] = clf.predict_proba(np.stack([infer[n][ch] for n in names], axis=1).astype(np.float32))[:, 1]
    field = np.zeros(foot.size, np.float32)
    field[fidx] = prob
    field = field.reshape(foot.shape)
    print(f"full-catalogue model done {time.time()-t0:.0f}s", flush=True)

    # ---- novelty: surface BEFORE placement (protocol §1) ----
    from scripts.novelty import audit as novelty_audit, canonical_hash
    inv = json.loads((ROOT / "registry" / "focus_inventory.json").read_text())
    if not inv.get("complete_within_scope") or inv.get("failed"):
        raise SystemExit("registry incomplete; cannot grant novelty clearance")
    local_of = {i["path"]: ROOT / i["local"] for i in inv["rasters"]}

    def cached_audit(prediction, stage, cache_name):
        cache = EVID / cache_name
        digest = canonical_hash(np.asarray(prediction, np.float32)[foot])
        if cache.exists():
            prev = json.loads(cache.read_text())
            if prev.get("candidate_values_sha256") == digest and prev.get("comparisons_complete"):
                print(f"novelty {stage}: reusing complete cached scan", flush=True)
                return prev
        res = novelty_audit(prediction, foot, inv, ROOT, ROOT / "data/bridge/sample_submission.tif",
                            stage=stage, stop_on_duplicate=False)
        res["candidate_values_sha256"] = res.get("candidate_values_sha256", digest)
        cache.write_text(json.dumps(res, default=str))
        return res

    surface = cached_audit(field, "surface", "novelty_surface.json")

    def maxima(rows, exclude_lattice=True):
        sp, ov, worst = [], [], None
        for r in rows:
            if r.get("status") != "compared":
                continue
            if exclude_lattice and "lattice" in r.get("path", "").lower():
                continue
            if r.get("spearman") is not None:
                sp.append(r["spearman"])
            o = r.get("directed_overlap_within_3px")
            if o is not None:
                ov.append(o)
                if worst is None or o > worst[1]:
                    worst = (r.get("path"), o, r.get("spearman"))
        return dict(max_spearman=max(sp) if sp else None, max_overlap=max(ov) if ov else None,
                    worst=worst)
    comp_surface = maxima(surface["comparisons"])
    if (comp_surface["max_spearman"] or 0) > 0.90:
        save("run_card.json", dict(verdict="negative", ok_to_download_and_submit=False,
                                   stage="surface novelty", surface=comp_surface,
                                   hypothesis="H-BSTEP (knowledge/hypotheses_20261031.md)",
                                   evidence_class="HOLDOUT-DTI + REGISTRY-MEASUREMENT"))
        raise SystemExit("surface lane-drift (rho > 0.90); protocol says stop")

    # ---- placement: plain emission at the preregistered shipped cell ----
    allowed = foot & catalogue_exclusion(cat, PRUNE_SHIP) & (field > 0)
    dots_plain = poisson_disk_dots(field, allowed, N_SHIP, SPACING)
    pred_plain = np.where(dots_plain, 1.0, 0.0).astype(np.float32)
    dots_audit_plain = cached_audit(pred_plain, "dots", "novelty_dots_plain.json")
    comp_dots = maxima(dots_audit_plain["comparisons"])

    # exact-duplicate scan vs every prior repo TIFF (learning + released)
    digest = canonical_hash(pred_plain[foot])
    priors = sorted((ROOT / "docs" / "downloads").glob("*.tif")) \
        + sorted((ROOT / "swgb" / "downloads").glob("*.tif")) \
        + sorted((ROOT / "archive").rglob("*.tif"))
    exact_dupes = []
    for p in priors:
        try:
            a = read_band(p).astype(np.float32)
            if a.shape == foot.shape and canonical_hash(np.nan_to_num(a)[foot]) == digest:
                exact_dupes.append(str(p.relative_to(ROOT)))
        except Exception:
            continue

    lane_drift_plain = ((comp_dots["max_spearman"] or 0) > 0.90
                        or (comp_dots["max_overlap"] or 0) > 0.70)
    shipped, dots_audit, comp_shipped, variant, ac_meta = pred_plain, dots_audit_plain, comp_dots, "plain", None
    if lane_drift_plain:
        # preregistered anti-collision replacement (hypotheses_20261031.md §2): R* = union of the
        # offending rasters' dots; tiered emission with deterministic fallback; re-audit.
        offenders = [r for r in dots_audit_plain["comparisons"]
                     if r.get("status") == "compared" and "lattice" not in r.get("path", "").lower()
                     and ((r.get("spearman") or 0) > 0.90
                          or (r.get("directed_overlap_within_3px") or 0) > 0.70)]
        ac_union = np.zeros(foot.shape, bool)
        for r in offenders:
            src = local_of.get(r["path"])
            if src is not None and src.exists():
                ac_union |= np.nan_to_num(read_band(src), nan=0.0) > 0
        halo = ndimage.distance_transform_edt(~ac_union) <= 3.0
        dots_ac = tiered_dots(field, allowed & ~halo, allowed, N_SHIP, SPACING)
        pred_ac = np.where(dots_ac, 1.0, 0.0).astype(np.float32)
        dots_audit_ac = cached_audit(pred_ac, "dots", "novelty_dots_ac.json")
        comp_ac = maxima(dots_audit_ac["comparisons"])
        ac_meta = dict(offenders=[r["path"] for r in offenders],
                       dots_before=int(dots_plain.sum()), dots_after=int(dots_ac.sum()))
        shipped, dots_audit, comp_shipped, variant = pred_ac, dots_audit_ac, comp_ac, "anti_collision"

    lattice_rows = [dict(path=r.get("path"), spearman=r.get("spearman"),
                         overlap=r.get("directed_overlap_within_3px"))
                    for r in dots_audit["comparisons"] if "lattice" in r.get("path", "").lower()]
    full_dots = maxima(dots_audit["comparisons"], exclude_lattice=False)
    unassessable = [r["path"] for r in dots_audit["comparisons"]
                    if r.get("status") not in ("compared",)]
    lane_drift = ((comp_surface["max_spearman"] or 0) > 0.90
                  or (comp_shipped["max_overlap"] or 0) > 0.70
                  or bool(exact_dupes))

    # ---- holdout measurement of the shipped dots on the fold fields (preregistered cell) ----
    z = np.load(WORK / "e1_fields.npz")
    efields = [z[f"arr_{i}"].astype(np.float32) for i in range(len(folds))]
    shipped_dots_by_fold = fold_dots(efields, folds, N_SHIP, PRUNE_SHIP)
    s_cell = score_pooled(shipped_dots_by_fold, folds, n_boot=200)
    ff_cell = score_pooled_farfield(shipped_dots_by_fold, folds, n_boot=100)
    e1 = json.loads((EVID / "e1_holdout.json").read_text())
    e2 = json.loads((EVID / "e2_emission.json").read_text())

    verdict = "promote" if (not lane_drift and s_cell["holdout_dti"] > BAR["holdout_dti"]
                            and not exact_dupes) else "negative"
    ok_to_submit = verdict == "promote"

    n_ship_dots = int((shipped > 0).sum())
    raster_name = f"gemsass1-bstep-concord-{n_ship_dots}-b6-20261031-zeros.tif"
    submission_name = raster_name.replace("-zeros.tif", "")
    note = (f"GEMSASS1 H-BSTEP basement-edge concordance learner {n_ship_dots}d >600m off-cat "
            f"2.8px {variant}; HOLDOUT-DTI evidence/bstep/run_card.json")[:140]

    receipt = format_rep = None
    if ok_to_submit:
        from vendor.gems57.submission_writer import write_submission
        dest = ROOT / "docs" / "downloads"
        tif_path = dest / raster_name
        receipt = write_submission(tif_path, shipped, ROOT / "data/bridge/sample_submission.tif", foot,
                                   note=note, name=submission_name, catalogue=cat,
                                   metadata=dict(hypothesis="H-BSTEP basement-step concordance learner",
                                                 evaluator=EVALUATOR_VERSION, n_dots=int((shipped > 0).sum()),
                                                 spacing_px=SPACING, prune_px=PRUNE_SHIP,
                                                 emission_variant=variant))
        format_rep = format_validate(tif_path, foot, cat)
        sha = sha256_file(tif_path)
    else:
        WORK.mkdir(parents=True, exist_ok=True)
        np.save(WORK / "rejected_pred.npy", shipped)
        sha = None

    card = dict(
        schema="gemsass1.run_card.v2", generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        lane_label="H-BSTEP basement-step concordance learner",
        run_card_href="evidence/bstep/run_card.json",
        hypothesis=("H-BSTEP: basement-rooted faults under basin fill co-locate gradient ridges of "
                    "depth-to-basement, gravity and magnetics; a segment-withheld learner augmented "
                    "with edge-concordance transforms (plus relay-polarity, gouge-conductivity, "
                    "strain-boundary and quake-curvature transforms) recovers hidden fault segments "
                    "that the lidar-openness family misses (knowledge/hypotheses_20261031.md)."),
        mechanism=("single HistGradientBoosting (250 it, lr 0.08, 31 leaves) trained on ALL catalogue "
                   "segments with full-catalogue context; features = 28 static lidar/GeoDAWN layers + "
                   "19 derived bands + 10 concordance transforms + 4 visible-catalogue context; "
                   f"Poisson-disk emission {int((shipped > 0).sum())} dots at {SPACING} px, "
                   f">{int(PRUNE_SHIP * 100)} m catalogue exclusion, variant={variant}."),
        named_non_fault_mimic=("Pluvial shoreline benches and fluvial terrace risers around thermal "
                               "basins (coherent, low-relief, contour-parallel); road/canal embankments; "
                               "basaltic vent rims; dike and intrusive contacts give magnetic-gradient "
                               "maxima without displacement."),
        holdout_dti=dict(label="HOLDOUT-DTI", evaluator=EVALUATOR_VERSION,
                         value=s_cell["holdout_dti"], ci95=s_cell["ci95"],
                         farfield_true_gt500m_from_visible=ff_cell["holdout_dti"],
                         n_withheld_positives=s_cell["n_withheld_positives"],
                         e1_comparable_cell=dict(value=e1["holdout_dti"], ci95=e1["ci95"],
                                                 farfield=e1["farfield"],
                                                 cell="37,654 / 2.8 px / >2 px"),
                         e2_sweep=e2["grid"], e2_anti_collision_cell=e2["anti_collision_cell"],
                         bar=BAR, repo_best=REPO_BEST, e2_swgb=E2_SWGB,
                         label_note="HOLDOUT-DTI is hide-and-recover evidence, never a leaderboard score."),
        correlation_overlap_vs_registry=dict(
            surface=comp_surface, dots_competitive=comp_shipped,
            dots_full_registry_including_lattice_fixture=full_dots,
            lattice_amendment="AMEND-LATTICE-01 (IR-LATTICE-01): the 5 px calibration-lattice fixture "
                              "is measured and reported here but exempted from the 70%/3 px gate; "
                              "without the exemption the 0.2778 champion itself is classified a "
                              "duplicate of a 0.0904 grid. AMEND-N2: nonfinite published priors "
                              "compared with nonfinite = 0 support.",
            lattice_rows=lattice_rows, unassessable_rows=unassessable,
            exact_duplicate_scan=dict(candidate_values_sha256=digest, exact_duplicate_paths=exact_dupes,
                                      repo_priors_scanned=len(priors)),
            anti_collision=ac_meta, emission_variant=variant),
        raster_sha256=sha, raster_name=raster_name,
        validator_output=(format_rep or dict(all_checks_passed=False, reason="not written: gate failed")),
        submission_name=submission_name, note=note, note_length=len(note),
        verdict=verdict, ok_to_download_and_submit=ok_to_submit,
        submission_slots_used=0,
        evidence_class=("HOLDOUT-DTI (GEMSASS1-HR-v2-segment) + REGISTRY-MEASUREMENT; "
                        "owner-reported sibling scores are OWNER-REPORT, not receipts"),
        experiments_run=3, experiment_budget=EXPERIMENT_BUDGET,
        elapsed_s=round(time.time() - t0, 1),
        limitations=[
            "Holdout truth is catalogue-derived (labels.tif is byte-identical to existing_faults.tif "
            "in the owner mirror); holdout-live Spearman is -0.081 across 17 registry rasters, so no "
            "holdout number forecasts a leaderboard score.",
            "Owner-mirror data provenance: integrity-verified against pinned hashes, NOT "
            "organizer-authenticated.",
            "Eligibility (rules §1.3, U.S. persons/entities) is a user decision before any upload; "
            "this workspace never uploads and spends no competition slot.",
            "IR-LATTICE-01 policy item remains open; both the literal and AMEND-LATTICE-01 readings "
            "are printed above.",
        ])
    save("run_card.json", card)

    gates = [
        ["Validator: values in [0,1], no NaN anywhere, exact competition grid",
         bool(format_rep and format_rep["all_checks_passed"])],
        ["Not an exact duplicate of any registry raster or prior repo file", not exact_dupes],
        ["Lane-drift gate vs competitive registry (Spearman ≤ 0.90, 3 px overlap ≤ 70%)",
         not lane_drift],
        [f"HOLDOUT-DTI beats the 0.2600-family bar (0.1011): {s_cell['holdout_dti']:.4f}",
         s_cell["holdout_dti"] > BAR["holdout_dti"]],
        ["Zero positive mass on mapped catalogue faults",
         bool(format_rep and format_rep["checks"].get("zero_mass_on_known_catalogue_pixels"))],
        ["No weekly submission slot used by this workspace", True],
    ]
    estimate = ("ESTIMATE (low confidence, projection — NOT a score): no calibrated local instrument "
                "forecasts live scores (holdout-live Spearman −0.081). Reference distribution only: "
                "the 0.2477–0.2778 OWNER-REPORT family band at 37k–61k dots. "
                f"HOLDOUT-DTI {s_cell['holdout_dti']:.4f} [{s_cell['ci95'][0]:.4f}, "
                f"{s_cell['ci95'][1]:.4f}] vs bar 0.1011.")
    release = dict(card=card, gates=gates, estimate_text=estimate, e2=e2, e3=None,
                   validator=format_rep,
                   novelty=dict(surface=comp_surface, dots=comp_shipped, full_registry=full_dots,
                                lattice_rows=lattice_rows),
                   exact_duplicate_scan=card["correlation_overlap_vs_registry"]["exact_duplicate_scan"],
                   ok_to_download_and_submit=ok_to_submit)
    save("release.json", release)
    budget_add("package", round(time.time() - t0, 1), experiments=1)
    print(json.dumps(dict(verdict=verdict, ok_to_download_and_submit=ok_to_submit,
                          holdout=s_cell["holdout_dti"], max_overlap=comp_shipped["max_overlap"],
                          max_rho=comp_shipped["max_spearman"], raster_name=raster_name)))
    return release


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "canary":
        if not run_canary():
            raise SystemExit("leakage canary failed; lane stops")
    elif stage == "e1":
        run_e1()
    elif stage == "e2":
        run_e2()
    elif stage == "package":
        run_package()
    else:
        if not run_canary():
            raise SystemExit("leakage canary failed; lane stops")
        run_e1()
        run_e2()
        run_package()


if __name__ == "__main__":
    main()
