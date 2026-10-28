#!/usr/bin/env python3
"""H-PBSC lane (session 2026-10-28). Preregistration: knowledge/03_hypotheses_20261028.md

E1  playa-bounding scarp corridor (step × coh × low-relief neighborhood × weak mag)
E2  no-mag ablation (same lane)
E3  emission n_dots sweep — only if E1 or E2 beats HOLDOUT-DTI bar 0.1011

Reuse shared tools: src/gems/{features,holdout,emission,registry,submission}.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.grid import load_footprint, load_catalogue, sha256_file, read_band, DATA  # noqa: E402
from gems.holdout import (  # noqa: E402
    build_folds, score_pooled, score_pooled_farfield, auc_binary, EVALUATOR_VERSION,
)
from gems.features import build_static_features  # noqa: E402
from gems.emission import poisson_disk_dots, catalogue_exclusion  # noqa: E402
from gems.registry import lane_audit, load_registry, RANK_CORR_MAX, DOT_OVERLAP_MAX, OVERLAP_PX  # noqa: E402
from gems.submission import write_submission  # noqa: E402

BAR = dict(
    name="gems25-dotted-h19-5-d2-8 (0.2600 family base, un-pruned)",
    holdout_dti=0.1011,
    ci95=[0.0956, 0.1072],
    evidence="evidence/swgb/holdout_calibration.json",
)
N_DOTS = 37_654
SPACING = 2.8
PRUNE_PX = 6.0
EVIDENCE = ROOT / "evidence" / "pbsc"
WORK = ROOT / "work" / "pbsc"
DOWNLOADS = ROOT / "docs" / "downloads"
EXTRA_REG = DATA / "registry_extra"
STAMP = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def rank01(a: np.ndarray, mask: np.ndarray) -> np.ndarray:
    out = np.zeros(a.shape, np.float32)
    v = a[mask]
    if v.size == 0:
        return out
    r = np.empty(v.size, np.float32)
    order = np.argsort(v, kind="stable")
    r[order] = np.arange(v.size, dtype=np.float32) / max(v.size - 1, 1)
    out[mask] = r
    return out


def pbsc_field(feats: dict, lidar_valid: np.ndarray, foot: np.ndarray, use_mag: bool) -> np.ndarray:
    """Label-free playa-bounding scarp corridor. No catalogue features."""
    m = foot & lidar_valid
    step = rank01(feats["lidar_step_max"], m)
    coh = rank01(feats["lidar_coh100"], m)
    relief_s8 = ndimage.gaussian_filter(feats["lidar_relief"].astype(np.float32), 8.0)
    playa = 1.0 - rank01(relief_s8, m)  # high where ~800 m neighborhood is low-relief
    dipole = rank01(feats["lidar_dipole"], m)
    field = (step ** 0.40) * (coh ** 0.30) * (playa ** 0.25) * ((0.5 + 0.5 * dipole) ** 0.15)
    if use_mag:
        mag = rank01(feats["mag_hgrad_s2"], foot)  # mag is defined off lidar too
        field = field * (0.40 + 0.60 * mag)
    field = np.where(m, field, 0.0).astype(np.float32)
    return field


def extra_dot_audit(dots: np.ndarray, field: np.ndarray, foot: np.ndarray) -> dict:
    """Uniqueness vs this-repo SWGB and sibling SASS2/SASS3 shipped files."""
    rows = []
    n = int(dots.sum())
    fy, fx = np.nonzero(foot)
    rng = np.random.default_rng(0)
    sel = rng.choice(fy.size, size=min(400_000, fy.size), replace=False)
    cf = np.nan_to_num(field, nan=0.0)[fy[sel], fx[sel]]
    extras = [
        ("GEMSDOESASS1-SWGB", EXTRA_REG / "gemsass1-swgb-hrv2.tif"),
        ("GEMSDOESASS2-XGHF", EXTRA_REG / "gemsdoesass2-xghf.tif"),
        ("GEMSDOESASS3-LWST", EXTRA_REG / "gemsdoesass3-lwst.tif"),
    ]
    for site, p in extras:
        if not p.exists():
            rows.append(dict(site=site, file=p.name, missing=True, duplicate=False))
            continue
        a = np.nan_to_num(read_band(p), nan=0.0)
        rd = a > 0.5
        rf = a[fy[sel], fx[sel]]
        rho = spearmanr(cf, rf).correlation if np.std(rf) > 0 and np.std(cf) > 0 else 0.0
        rho = float(0.0 if rho is None or np.isnan(rho) else rho)
        d = ndimage.distance_transform_edt(~rd)
        within = float((d[dots] <= OVERLAP_PX).sum() / max(n, 1))
        rows.append(dict(
            site=site, file=p.name, spearman=rho, frac_dots_within_3px=within,
            registry_dots=int(rd.sum()),
            duplicate=bool(rho > RANK_CORR_MAX or within > DOT_OVERLAP_MAX),
        ))
    return dict(
        max_spearman=max((r.get("spearman") or 0.0) for r in rows),
        max_frac_dots_within_3px=max((r.get("frac_dots_within_3px") or 0.0) for r in rows),
        is_duplicate=any(r.get("duplicate") for r in rows),
        rows=rows,
    )


def surface_spearman(field: np.ndarray, foot: np.ndarray) -> dict:
    """Pre-placement rank correlation vs the 17 focus-site rasters."""
    registry = load_registry()
    fy, fx = np.nonzero(foot)
    rng = np.random.default_rng(0)
    sel = rng.choice(fy.size, size=min(400_000, fy.size), replace=False)
    cf = np.nan_to_num(field, nan=0.0)[fy[sel], fx[sel]]
    rows = []
    for r in registry:
        rf = r["field"][fy[sel], fx[sel]]
        rho = spearmanr(cf, rf).correlation if np.std(rf) > 0 and np.std(cf) > 0 else 0.0
        rho = float(0.0 if rho is None or np.isnan(rho) else rho)
        rows.append(dict(site=r["site"], file=r["file"], spearman=rho, duplicate=rho > RANK_CORR_MAX))
    worst = max((x["spearman"] for x in rows), default=0.0)
    return dict(max_spearman=worst, is_duplicate=worst > RANK_CORR_MAX, rows=rows)


def emit_holdout(field: np.ndarray, folds, n_dots: int, spacing: float):
    dots_by_fold = []
    for fd in folds:
        allowed = fd.active & (field > 0)
        d = poisson_disk_dots(field, allowed, n_dots, spacing)
        dots_by_fold.append(d)
        print(f"    fold {fd.f}: dots={int(d.sum())}", flush=True)
    return dots_by_fold


def dump(name: str, obj) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / name).write_text(json.dumps(obj, indent=2) + "\n")


def main() -> None:
    t0 = time.time()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    print(f"H-PBSC start {STAMP} evaluator={EVALUATOR_VERSION}", flush=True)

    foot, cat = load_footprint(), load_catalogue()
    folds, n_seg = build_folds(cat, foot)
    print(f"  grid foot={int(foot.sum())} cat={int(cat.sum())} segments={n_seg}", flush=True)

    feats, lidar_valid = build_static_features()
    keep = [
        "lidar_step_max", "lidar_coh100", "lidar_relief", "lidar_dipole",
        "lidar_downface_max", "lidar_ex_max", "mag_hgrad_s2",
        "rad_K_grad_s3", "rad_ThK_grad_s3",
    ]
    small = {k: feats[k] for k in keep}
    del feats
    print(f"  features ready {time.time()-t0:.0f}s lidar_valid={int(lidar_valid.sum())}", flush=True)

    # --- leakage canary (fold 0) ---
    fd0 = folds[0]
    canary = {}
    for n, a in small.items():
        canary[n] = auc_binary(a[fd0.active], fd0.test_truth[fd0.active])
        canary[n + "__neg"] = 1.0 - canary[n]
    flagged = {k: v for k, v in canary.items() if v > 0.90}
    canary_out = dict(
        evaluator=EVALUATOR_VERSION, fold=0, n_withheld_positives=fd0.n_test,
        auc=canary, flagged_over_0p90=flagged,
    )
    dump("leakage_canary.json", canary_out)
    top = sorted(canary.items(), key=lambda kv: -kv[1])[:8]
    print("  canary top:", ", ".join(f"{k}={v:.3f}" for k, v in top), "flagged", flagged, flush=True)
    if flagged:
        dump("run_card.json", dict(
            hypothesis="H-PBSC", verdict="negative", stop_reason="leakage canary AUC>0.90",
            canary=canary_out, generated_utc=STAMP,
        ))
        print("STOP: leakage canary", flush=True)
        return

    experiments = []
    winner = None

    for tag, use_mag in (("e1_pbsc", True), ("e2_nomag", False)):
        print(f"  === {tag} use_mag={use_mag} ===", flush=True)
        field = pbsc_field(small, lidar_valid, foot, use_mag=use_mag)
        np.save(WORK / f"{tag}_field.npy", field.astype(np.float16))
        surf = surface_spearman(field, foot)
        dump(f"{tag}_surface.json", surf)
        print(f"    surface max Spearman={surf['max_spearman']:.4f} dup={surf['is_duplicate']}", flush=True)
        if surf["is_duplicate"]:
            experiments.append(dict(experiment=tag, stop="surface-duplicate", **surf))
            dump(f"{tag}_holdout.json", dict(experiment=tag, stop="surface-duplicate", surface=surf))
            if tag == "e1_pbsc":
                print("STOP: E1 surface duplicate (protocol §1)", flush=True)
                dump("run_card.json", dict(
                    hypothesis="H-PBSC playa-bounding scarp corridor",
                    verdict="negative",
                    stop_reason="E1 surface Spearman > 0.90 vs registry",
                    surface=surf, generated_utc=STAMP, elapsed_s=round(time.time() - t0, 1),
                ))
                return
            continue
        dots_by_fold = emit_holdout(field, folds, N_DOTS, SPACING)
        s = score_pooled(dots_by_fold, folds)
        ff = score_pooled_farfield(dots_by_fold, folds, min_dist_px=5)
        rec = dict(
            experiment=tag, hypothesis="playa-bounding scarp corridor" + ("" if use_mag else " (no mag)"),
            use_mag=use_mag, n_dots=N_DOTS, spacing_px=SPACING,
            **s, farfield=ff, bar=BAR, beats_bar=s["holdout_dti"] > BAR["holdout_dti"],
            surface_max_spearman=surf["max_spearman"],
            elapsed_s=round(time.time() - t0, 1),
        )
        dump(f"{tag}_holdout.json", rec)
        experiments.append(rec)
        print(
            f"    HOLDOUT-DTI {s['holdout_dti']:.4f} {s['ci95']} n={s['n_withheld_positives']} "
            f"beats_bar={rec['beats_bar']} far={ff['holdout_dti']:.4f}",
            flush=True,
        )
        if winner is None or s["holdout_dti"] > winner["rec"]["holdout_dti"]:
            winner = dict(tag=tag, field=field, rec=rec, use_mag=use_mag)

    if winner is None:
        dump("run_card.json", dict(verdict="negative", stop_reason="no unique surface", generated_utc=STAMP))
        return

    # E3 emission sweep only if the bar is beaten
    e3 = None
    if winner["rec"]["beats_bar"]:
        print("  === e3 emission sweep ===", flush=True)
        e3_rows = []
        for n_dots in (37_654, 44_090):
            dots_by_fold = emit_holdout(winner["field"], folds, n_dots, SPACING)
            s = score_pooled(dots_by_fold, folds, n_boot=150)
            e3_rows.append(dict(n_dots=n_dots, spacing_px=SPACING, **s))
            print(f"    n={n_dots} DTI={s['holdout_dti']:.4f}", flush=True)
        e3 = dict(experiment="e3_emission", parent=winner["tag"], rows=e3_rows)
        dump("e3_emission.json", e3)
        best_n = max(e3_rows, key=lambda r: r["holdout_dti"])
        N_SHIP = int(best_n["n_dots"])
    else:
        N_SHIP = N_DOTS

    # --- shipped emission on the full catalogue ---
    field = winner["field"]
    allowed = foot & catalogue_exclusion(cat, PRUNE_PX) & (field > 0)
    dots = poisson_disk_dots(field, allowed, N_SHIP, SPACING)
    print(f"  shipped dots={int(dots.sum())} prune={PRUNE_PX}px", flush=True)

    audit = lane_audit(field, dots, foot)
    extra = extra_dot_audit(dots, field, foot)
    dup = bool(audit["is_duplicate"] or extra["is_duplicate"])
    print(
        f"  uniqueness focus maxρ={audit['max_spearman']:.3f} ov={audit['max_frac_dots_within_3px']:.3f} "
        f"extra ov={extra['max_frac_dots_within_3px']:.3f} duplicate={dup}",
        flush=True,
    )
    dump("uniqueness.json", dict(focus=audit, extra=extra, is_duplicate=dup))

    dcat = ndimage.distance_transform_edt(~cat)
    emission = dict(
        n_dots=int(dots.sum()), spacing_px=SPACING, prune_px=PRUNE_PX,
        dots_within_2px_of_catalogue=int((dcat[dots] <= 2).sum()),
        dots_on_catalogue=int((dots & cat).sum()),
        dots_with_lidar=int((dots & lidar_valid).sum()),
        median_catalogue_dist_px=float(np.median(dcat[dots])) if dots.any() else None,
        field_quantile_of_last_dot=float((field[foot] < field[dots].min()).mean()) if dots.any() else None,
    )
    dump("emission.json", emission)

    hd = winner["rec"]
    note = (
        f"GEMSASS1 PBSC: playa-bounding step×coh×low-relief"
        f"{'+mag' if winner['use_mag'] else ''} {N_SHIP}d 2.8px >600m offcat; "
        f"HOLDOUT-DTI {hd['holdout_dti']:.3f} vs bar 0.101"
    )
    if len(note) > 140:
        note = note[:140]
    sha8 = sha256_file(WORK / f"{winner['tag']}_field.npy")[:8]
    name = f"gemsass1-pbsc-playa-{N_SHIP}dots-{STAMP}-{sha8}-zeros"

    beats = bool(hd["beats_bar"] and hd["ci95"][0] > 0)
    # promote only if unique AND beats the 0.1011 bar; uniqueness failure = do not write
    if dup:
        verdict = "negative"
        rep = None
        print("DUPLICATE LANE — not writing a submission file", flush=True)
    else:
        DOWNLOADS.mkdir(parents=True, exist_ok=True)
        rep = write_submission(
            dots, foot, DOWNLOADS / f"{name}.tif", catalogue=cat, note=note,
            meta=dict(lane="H-PBSC", experiment=winner["tag"], emission=emission),
        )
        print(f"  wrote {rep['path']} sha256={rep['sha256'][:16]} checks={rep['all_checks_passed']}", flush=True)
        verdict = "promote" if (beats and rep["all_checks_passed"]) else "negative"

    card = {
        "hypothesis": (
            "Uncatalogued Holocene normal faults in the NW Great Basin preferentially bound internally "
            "drained playas: a coherent lidar step with a low-relief hanging-wall neighborhood, weakly "
            "corroborated by a shallow magnetic edge from basement offset. USGS/INGENIOUS Qfaults under-map "
            "these 1–5 m scarps because they sit in alluvium kilometres from the range front; the hidden "
            "1 m lidar labels include them (the 0.2778 champion's median catalogue distance is ~2 km)."
        ),
        "mechanism": (
            "Label-free product of ranked lidar step_max^0.40, along-strike coh100^0.30, "
            "inverted 800 m-scale relief (playa neighborhood)^0.25, mild LoG dipole, and "
            "(if E1) (0.40+0.60*rank mag_hgrad_s2). Poisson-disk 2.8 px, 600 m catalogue exclusion at emission. "
            "No supervised learner and no catalogue-distance features."
        ),
        "named_non_fault_mimic": (
            "Pluvial Lake Lahontan shorelines and wave-cut benches: coherent, low-relief, playa-bounding, "
            "usually without a magnetic edge. Canal banks and fluvial terrace risers."
        ),
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evaluator": EVALUATOR_VERSION,
            "value": hd["holdout_dti"],
            "ci95": hd["ci95"],
            "n_withheld_positives": hd["n_withheld_positives"],
            "bar_0p2600_family_base": BAR,
            "beats_bar": hd["beats_bar"],
            "farfield_gt5px": hd.get("farfield"),
        },
        "correlation_overlap_vs_registry": {
            "max_spearman": audit["max_spearman"],
            "max_frac_dots_within_3px": audit["max_frac_dots_within_3px"],
            "thresholds": audit["thresholds"],
            "is_duplicate": audit["is_duplicate"],
            "rows": audit["rows"],
            "extra_sibling_and_prior_swgb": extra,
        },
        "emission": emission,
        "raster_sha256": None if rep is None else rep["sha256"],
        "validator_output": None if rep is None else rep["checks"],
        "submission_name": None if rep is None else f"{name}.tif",
        "submission_note": note,
        "note_length": len(note),
        "verdict": verdict,
        "ok_to_submit": verdict == "promote",
        "score_labels": (
            "No live score exists for this file. HOLDOUT-DTI is not a leaderboard score; "
            "projections are not scores. 0.2778 is OWNER-REPORT, not ORGANIZER-CONFIRMED."
        ),
        "organizer_confirmed": None,
        "generated_utc": STAMP,
        "elapsed_s": round(time.time() - t0, 1),
        "n_segments": int(n_seg),
        "budget": {
            "experiments_run": [e.get("experiment") or e.get("tag") for e in experiments] + (["e3_emission"] if e3 else []),
            "protocol_limit": 3,
        },
        "irregularities": [
            "IR-LATTICE-01: 13gems 5-px lattice covers 99.87% of the footprint; excluded from the 70% rule (same policy as the SWGB lane).",
            "IR-04: sibling live scores are OWNER-REPORT; DrivenData is not on this sandbox allowlist.",
        ],
        "winner_experiment": winner["tag"],
        "canary_pass": True,
        "approved_for_submission": verdict == "promote",
        "submission_path": None if rep is None else str(DOWNLOADS / f"{name}.tif"),
    }
    dump("run_card.json", card)
    print(json.dumps({k: card[k] for k in ("verdict", "ok_to_submit", "raster_sha256", "submission_name", "note_length")}, indent=1), flush=True)


if __name__ == "__main__":
    main()
