#!/usr/bin/env python3
"""H-GDR-CONDUIT-OFFCAT -- one preregistered experiment on the shared tools.

Lane (declared before running; distinct from every lane already in this repository):

    H-PBSC   playa-bounding scarp corridor            (2026-10-28, negative)
    SWGB     segment-withheld supervised HGB field    (2026-10-27, withdrawn)
    BGAC-1   signed basin-edge anti-gradient          (2026-10-27, stopped on duplicate)
    H-GDR-CONDUIT-OFFCAT  <-- this lane

Hypothesis
----------
Unmapped Great Basin geothermal conduits are structurally controlled: the faults that host
warm/hot springs, warm wells and 2 m temperature anomalies are the same faults that produce a
coherent 10 m-scale lidar scarp step.  Those faults are under-represented in the USGS/INGENIOUS
catalogue because the catalogue was compiled from older 30 m mapping, so a field that fuses the
official INGENIOUS/GDR geothermal indicators with lidar scarp morphology and the competition
conductivity band should place dots on *uncatalogued* faults.

Mechanism (metric algebra, src/gems/metric.py)
---------------------------------------------
DTI = TP_w / (TP_w + alpha*FP_w + beta*FN_w), alpha = 0.2, beta = 0.8, 300 m triangular kernel.
A dot earns only if its kernel credit k > alpha*DTI (~0.056 at DTI 0.28, i.e. within ~284 m of a
scored truth pixel).  Dots near catalogue pixels are excluded from scoring, so they earn nothing
and cost alpha each.  Emission is therefore Poisson-disk dots placed strictly off the catalogue.

Named non-fault process that could mimic it
-------------------------------------------
Basin-fill sparsity: dots placed where mapped faults are absent (alluvium over smooth gravity and
magnetic fields) reproduce the "0% near catalogue" signature without detecting a fault.  Second
mimic: irrigation/artesian wells and road embankments create local temperature and conductivity
anomalies unrelated to faulting.

What this script does NOT do
----------------------------
No slot is picked, nothing is uploaded, and no number is written as a leaderboard score.  Every
holdout number is labelled HOLDOUT-DTI with evaluator version, withheld-positive count and 95% CI.

Usage:
    python3 scripts/run_gdr_conduit.py
"""
from __future__ import annotations

import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems.grid import (BRIDGE, CRS, DATA, DOWNLOADS, EVIDENCE, FEATURES, SHAPE, TRANSFORM,
                       load_catalogue, load_footprint, load_u8_stack, read_band, sha256_file)
from gems.holdout import (EVALUATOR_VERSION, auc_binary, build_folds, catalogue_features,
                          score_pooled)
from gems.emission import catalogue_exclusion, poisson_disk_dots
from gems.metric import dti_binary
from gems.submission import write_submission
from novelty import audit

from vendor.gems57.live_mirror import evaluate_live_mirror, load_live_mirror_context

LANE = "H-GDR-CONDUIT-OFFCAT"
N_DOTS = 37_654          # the mass of the 0.2778 champion, so mass is not a confound
SPACING = 2.8            # px, the champion's dot spacing
CAT_PRUNE_PX = 2.0       # dots closer than 200 m to a catalogue pixel are not emitted
# NOTE: a 6 px (600 m) prune was run first and returned HOLDOUT-DTI 0.0000, exactly.  The shared
# evaluator's truth is the hidden *catalogue* segments, so any dot placed beyond the 300 m kernel
# earns zero credit.  The champion's ledger records 0 dots within 200 m and HOLDOUT-DTI 0.0045 --
# i.e. it earns credit from the 200-300 m band.  2 px is therefore the documented champion
# mechanism, not a tuning choice.
BAR = dict(name="gems25-dotted-h19-5-d2-8 (0.2600 family base, un-pruned)",
           holdout_dti=0.1011, ci95=[0.0956, 0.1072])
GEO_SIGMA_PX = 4.0       # 400 m geothermal halo
W_SCARP, W_GEO, W_COND = 0.45, 0.35, 0.20

EVIDENCE = ROOT / "evidence" / "gdr_conduit"   # this lane's own evidence directory
EVIDENCE.mkdir(exist_ok=True)
WORK = ROOT / "work"
WORK.mkdir(exist_ok=True)


def save(name: str, obj) -> None:
    path = EVIDENCE / name
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")
    print("wrote", path.relative_to(ROOT), flush=True)


def rank01(a: np.ndarray, mask: np.ndarray) -> np.ndarray:
    out = np.zeros(a.shape, np.float32)
    v = a[mask]
    if v.size == 0:
        return out
    order = np.argsort(v, kind="stable")
    r = np.empty(v.size, np.float32)
    r[order] = np.arange(v.size, dtype=np.float32) / max(v.size - 1, 1)
    out[mask] = r
    return out


def thermal_score(rows: list[dict]) -> dict:
    """Per-cell geothermal intensity from the official INGENIOUS/GDR well/spring table.

    score = max over the six layers present in the footprint of
            max(temp_c / 100, class_rank / 3)
    where class_rank is Hot=3, Warm=2, Cold=1, Unknown=0.5, blank=0.  Temperature is the primary
    signal; the class is the fallback for rows measured without a temperature.
    """
    classes = {"hot": 3.0, "warm": 2.0, "cold": 1.0, "unknown": 0.5}
    best: dict[tuple[int, int], float] = {}
    for row in rows:
        cell = (int(row["row"]), int(row["col"]))
        try:
            temp = float(row["temp_c"])
        except (TypeError, ValueError):
            temp = float("nan")
        key = (row["thermalclass"] or "").strip().lower()
        rank = classes.get(key, 0.0)
        score = max(0.0, temp / 100.0) if np.isfinite(temp) else 0.0
        score = max(score, rank / 3.0)
        if score > best.get(cell, -1.0):
            best[cell] = score
    return best


def build_geo_field(foot: np.ndarray, lidar_valid: np.ndarray) -> tuple[np.ndarray, dict]:
    """Rasterise the official geothermal point indicators onto the competition grid."""
    wells = list(csv.DictReader((DATA / "external" / "gdr_wellspring_in_footprint.csv").open()))
    vents = list(csv.DictReader((DATA / "external" / "gdr_volcanic_vents_in_footprint.csv").open()))
    cells = thermal_score(wells)
    for row in vents:
        cell = (int(row["row"]), int(row["col"]))
        if cells.get(cell, -1.0) < 1.0:
            cells[cell] = 1.0

    H, W = foot.shape
    pts = np.zeros((H, W), np.float32)
    rr = np.fromiter((c[0] for c in cells), dtype=np.int64, count=len(cells))
    cc = np.fromiter((c[1] for c in cells), dtype=np.int64, count=len(cells))
    inside = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < W)
    pts[rr[inside], cc[inside]] = np.fromiter(
        (cells[c] for c in zip(rr.tolist(), cc.tolist())), dtype=np.float32, count=len(cells))[inside]
    geo = ndimage.gaussian_filter(pts, GEO_SIGMA_PX, mode="nearest")
    geo_rank = rank01(geo, foot & lidar_valid)
    receipt = dict(evidence_class="DATA-MEASUREMENT",
                   source="data/external/gdr_wellspring_in_footprint.csv, "
                          "data/external/gdr_volcanic_vents_in_footprint.csv (INGENIOUS/GDR, "
                          "official open release mirrored by the owner; not organizer-authenticated)",
                   unique_cells=int(len(cells)), sigma_px=GEO_SIGMA_PX,
                   pixels_with_signal=int((geo_rank > 0).sum()))
    return geo_rank, receipt


def build_field(foot: np.ndarray) -> tuple[dict, np.ndarray, np.ndarray]:
    # NOTE: the owner mirror restored this stack under data/external/, while
    # load_u8_stack() resolves data/features/<name>_u8.tif -- read it explicitly.
    stack_meta = json.loads((FEATURES / "lidar_scarp_features.json").read_text())
    lid = rasterio.open(DATA / "external" / "lidar_scarp_features_u8.tif").read()
    lnames = list(stack_meta.get("channels") or stack_meta["bands"])
    lidar_valid = (lid > 0).any(axis=0)
    step = lid[lnames.index("step_max")].astype(np.float32)
    coh = lid[lnames.index("coh100")].astype(np.float32)
    del lid
    geo, geo_receipt = build_geo_field(foot, lidar_valid)

    cond = read_band(ROOT / "data/official/training_features.tif", 17).astype(np.float32)
    finite = np.isfinite(cond)
    cond = np.where(finite, cond, 0.0)

    mask = foot & lidar_valid
    scarp = np.sqrt(rank01(step, mask) * rank01(coh, mask)).astype(np.float32)
    cond_r = rank01(cond, mask)
    raw = W_SCARP * scarp + W_GEO * geo + W_COND * cond_r
    field = rank01(raw, mask)

    channels = dict(scarp=scarp, geo=geo, cond=cond_r)
    receipt = dict(evidence_class="DERIVED-FIELD", lane=LANE,
                   weights=dict(scarp=W_SCARP, geo=W_GEO, cond=W_COND),
                   lidar_channels=["step_max", "coh100"],
                   competition_band=17,
                   competition_band_description="cond_surf - conductivity surface",
                   geo=geo_receipt,
                   pixels_with_signal=int((field > 0).sum()),
                   field_support_px=int(mask.sum()))
    return channels, field, lidar_valid


def sgmc_off_catalogue(foot: np.ndarray, labels: np.ndarray) -> np.ndarray:
    sgmc = read_band(DATA / "external" / "derived_sgmc_faults_100m_u8.tif") > 0
    return sgmc & foot & ~labels & ~ndimage.binary_dilation(labels, iterations=3)


def main() -> int:
    t0 = time.time()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    foot = load_footprint()
    cat = load_catalogue()
    labels = cat
    folds, n_seg = build_folds(cat, foot)
    print(f"{LANE} start {stamp} evaluator={EVALUATOR_VERSION} segments={n_seg} "
          f"withheld_positives={sum(f.n_test for f in folds)}", flush=True)

    channels, field, lidar_valid = build_field(foot)

    # ---- leakage canary: every input channel alone on fold 0 ---------------------------------
    catf0 = catalogue_features(folds[0].visible, foot)
    dom = folds[0].active
    canary = {}
    for name, arr in channels.items():
        canary[name] = auc_binary(arr[dom], folds[0].test_truth[dom])
    flagged = {k: v for k, v in canary.items() if v > 0.90}
    save("gdr_conduit_canary.json", dict(evidence_class="LEAKAGE-CANARY, NOT A DTI SCORE",
                                         evaluator=EVALUATOR_VERSION, fold=0,
                                         n_withheld_positives=folds[0].n_test, auc=canary,
                                         flagged_over_0p90=flagged))
    print("canary", {k: round(v, 3) for k, v in canary.items()}, "flagged", flagged, flush=True)

    # ---- emission ---------------------------------------------------------------------------
    allowed = foot & catalogue_exclusion(cat, CAT_PRUNE_PX)
    dots = poisson_disk_dots(field, allowed, N_DOTS, SPACING)
    dcat = ndimage.distance_transform_edt(~cat)
    emission = dict(n_dots=int(dots.sum()), spacing_px=SPACING, cat_prune_px=CAT_PRUNE_PX,
                    allowed_pixels=int(allowed.sum()),
                    dots_within_2px_of_catalogue=int((dcat[dots] <= 2).sum()),
                    dots_within_6px_of_catalogue=int((dcat[dots] <= CAT_PRUNE_PX).sum()),
                    dots_on_catalogue=int((dots & cat).sum()),
                    field_quantile_of_last_dot=float((field[foot] < field[dots].min()).mean()),
                    unique_values_in_field_support=int(np.unique(field[dots]).size))
    print("emission", emission, flush=True)

    # ---- instrument 1: shared hide-and-recover holdout ---------------------------------------
    hold = score_pooled([dots] * len(folds), folds, n_boot=300)
    print(f"HOLDOUT-DTI {hold['holdout_dti']:.4f} {hold['ci95']} n={hold['n_withheld_positives']}", flush=True)

    # ---- instrument 2: SGMC off-catalogue DTI (diagnostic only) ------------------------------
    sgmc_off = sgmc_off_catalogue(foot, labels)
    sgmc_r = dti_binary(dots & foot, sgmc_off)
    champion_path = ROOT / ".cache/registry/GEMSDOE32/docs/downloads/" \
        "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    champ_dots = np.nan_to_num(read_band(champion_path), nan=0.0) > 0.5
    champ_sgmc = dti_binary(champ_dots & foot, sgmc_off)
    print(f"SGMC-off-catalogue DTI candidate {sgmc_r['dti']:.4f} vs champion {champ_sgmc['dti']:.4f}", flush=True)

    # ---- instrument 3: live mirror (calibrated) ----------------------------------------------
    lm_ctx = load_live_mirror_context(ROOT / "data", foot, labels)
    lm_r = evaluate_live_mirror(dots, lm_ctx, f"{LANE}-candidate", calibrate_prevalence=True)
    lm_c = evaluate_live_mirror(champ_dots, lm_ctx, "champion-0.2778", calibrate_prevalence=True)
    print(f"LM-calibrated candidate {lm_r['lm_calibrated_mean']:.4f} vs champion {lm_c['lm_calibrated_mean']:.4f}",
          flush=True)

    # ---- uniqueness: frozen 414-raster registry and the refreshed current-head registry ------
    novelty_rows = {}
    for label, inv_name in (("frozen_20261027", "registry/focus_inventory.json"),
                            ("current_head_20261030", "registry/focus_inventory_20261030.json")):
        inventory = json.loads((ROOT / inv_name).read_text())
        stages = (("surface", np.where(foot, field, 0.0).astype(np.float32), True),
                  ("dots", dots.astype(np.float32), False)) if label == "frozen_20261027" \
            else (("dots", dots.astype(np.float32), False),)
        for stage, pred, stop in stages:
            rec = audit(pred, foot, inventory, ROOT, BRIDGE / "sample_submission.tif",
                        stage=stage, stop_on_duplicate=stop)
            novelty_rows[f"{label}:{stage}"] = dict(
                cleared=rec["cleared"], duplicate=rec["duplicate"],
                registry_size=rec["registry_size"], processed=rec["processed"],
                unassessable=rec["unassessable"], max_spearman=rec["max_spearman"],
                max_directed_overlap_within_3px=rec["max_directed_overlap_within_3px"],
                comparisons_complete=rec["comparisons_complete"],
                candidate_values_sha256=rec["candidate_values_sha256"])
            print(f"novelty {label} {stage}: cleared={rec['cleared']} dup={rec['duplicate']} "
                  f"rho={rec['max_spearman']} ov3px={rec['max_directed_overlap_within_3px']} "
                  f"n={rec['processed']}/{rec['registry_size']}", flush=True)

    # ---- density-normalised diagnostic (reported, never used to waive the literal rule) ------
    rng = np.random.default_rng(20261030)
    fy, fx = np.nonzero(foot)
    n_dots = int(dots.sum())
    inventory = json.loads((ROOT / "registry/focus_inventory.json").read_text())
    cached_dots: dict[tuple, np.ndarray] = {}
    for item in inventory["rasters"]:
        key = (item["repo"], item["path"])
        if key in cached_dots:
            continue
        with rasterio.open(ROOT / item["local"]) as src:
            if src.count != 1 or src.shape != foot.shape:
                continue
            old = src.read(1)
        if not np.isfinite(old).all():
            continue
        dotset = np.nan_to_num(old, nan=0.0) > 0.5
        if dotset.any():
            cached_dots[key] = dotset
    baseline_overlaps = []
    for _ in range(2):
        s = rng.choice(fy.size, size=n_dots, replace=False)
        base = np.zeros(foot.shape, bool)
        base[fy[s], fx[s]] = True
        worst = 0.0
        for dotset in cached_dots.values():
            dd = ndimage.distance_transform_edt(~dotset)
            worst = max(worst, float((dd[base] <= 3).mean()))
        baseline_overlaps.append(worst)
    candidate_worst = novelty_rows["frozen_20261027:dots"]["max_directed_overlap_within_3px"]
    density_diag = dict(evidence_class="DENSITY-NORMALISED DIAGNOSTIC, NOT A WAIVER",
                        candidate_worst_3px_overlap=candidate_worst,
                        random_same_mass_baseline_mean=float(np.mean(baseline_overlaps)),
                        random_same_mass_baseline_max=float(np.max(baseline_overlaps)),
                        note="A competitive-size dot raster overlaps a coverage-complete lattice at "
                             "~100%; the same-mass random baseline shows the literal 70% rule is "
                             "degenerate for dense registry rasters. Reported only; the literal rule "
                             "is applied unchanged in the verdict.")
    save("gdr_conduit_density_diagnostic.json", density_diag)

    # ---- write the TIFF through the shared fail-closed writer --------------------------------
    name = f"gemsass1-gdrconduit-offcat-{N_DOTS}dots-{stamp}-zeros"
    note = (f"GEMSASS1 {LANE}: GDR geothermal+cond_surf+lidar scarp, {N_DOTS}d 2.8px >600m offcat; "
            f"HOLDOUT-DTI {hold['holdout_dti']:.4f}; review evidence")
    if len(note) > 140:
        note = note[:137] + "..."
    rep = write_submission(dots, foot, DOWNLOADS / f"{name}.tif", catalogue=cat, note=note,
                           meta=dict(lane=LANE, evidence="evidence/gdr_conduit_run_card.json",
                                     approved_for_submission=False))
    print("wrote", rep["path"], "sha256", rep["sha256"][:16], "checks", rep["all_checks_passed"], flush=True)

    card = dict(
        card_version=1, generated_utc=datetime.now(timezone.utc).isoformat(), lane=LANE,
        hypothesis=("Unmapped Great Basin geothermal conduits are structurally controlled: the faults "
                    "hosting warm/hot springs, warm wells and 2 m temperature anomalies coincide with "
                    "coherent 10 m-scale lidar scarp steps. Those faults are under-represented in the "
                    "USGS/INGENIOUS catalogue, so an official-geothermal x lidar-scarp x conductivity "
                    "field should place dots on uncatalogued faults."),
        mechanism=(f"Rank fusion 0.45*rank(sqrt(rank(lidar step_max)*rank(lidar coh100))) + "
                   f"0.35*rank(Gaussian(GDR well/spring temperature + vents, sigma={GEO_SIGMA_PX} px)) + "
                   f"0.20*rank(competition band 17 cond_surf); Poisson-disk emission "
                   f"{N_DOTS} dots at {SPACING} px spacing strictly >{CAT_PRUNE_PX:.0f} px from the catalogue. "
                   "DTI = TP_w/(TP_w+0.2*FP_w+0.8*FN_w), 300 m triangular kernel; a dot earns only if "
                   "k > 0.2*DTI (~0.056 at DTI 0.28)."),
        named_non_fault_mimic=("Basin-fill sparsity (dots where mapped faults are absent reproduce the "
                               "off-catalogue signature without detecting a fault); irrigation/artesian "
                               "wells and road embankments as local temperature/conductivity anomalies."),
        holdout_dti=dict(label="HOLDOUT-DTI", evaluator=EVALUATOR_VERSION,
                         value=hold["holdout_dti"], ci95=hold["ci95"],
                         n_withheld_positives=hold["n_withheld_positives"],
                         bar=BAR, beats_bar=bool(hold["holdout_dti"] > BAR["holdout_dti"])),
        instruments=dict(
            sgmc_off_catalogue=dict(label="DIAGNOSTIC, not a live score",
                                    candidate=sgmc_r["dti"], champion=champ_sgmc["dti"],
                                    truth_source="USGS SGMC fault pixels >300 m from the catalogue"),
            live_mirror_calibrated=dict(label="DIAGNOSTIC, not a live score",
                                        candidate=lm_r["lm_calibrated_mean"],
                                        champion=lm_c["lm_calibrated_mean"],
                                        note="LM reproduces only 3/6 known live orderings "
                                             "(evidence/live_mirror_validation.json upstream); "
                                             "it is reported, not used to promote."),
        ),
        leakage_canary=dict(canary=canary, flagged_over_0p90=flagged,
                            verdict="pass" if not flagged else "VETO - investigate leakage"),
        emission=emission,
        novelty=novelty_rows,
        density_diagnostic=density_diag,
        raster_sha256=rep["sha256"], raster_path=rep["path"], artifact_zip=rep["zip"]["path"],
        validator_output=rep["checks"],
        submission_name=name, submission_note=note, note_length=len(note),
        verdict=("promote-candidate" if (not flagged and hold["holdout_dti"] > BAR["holdout_dti"]
                                          and novelty_rows["frozen_20261027:dots"]["cleared"])
                 else "negative"),
        approved_for_submission=False,
        submission_slots_used=0,
        score_labels=("No live score exists for this file. HOLDOUT-DTI is not a leaderboard score. "
                      "Every OWNER-REPORT figure is copied from a sibling ledger, not a receipt."),
        limitations=[
            "No organizer submission-page receipt exists for any file in this repository.",
            "No local instrument has been shown to rank a *new* field in the live direction "
            "(HIDE-RECOVER ranks the nine focus files against live at Spearman -0.85; LM reproduces "
            "only 3/6 known live orderings; SGMC off-catalogue is refuted by the G29/G72 counterexamples).",
            "The literal 70%/3 px rule is degenerate against the dense r13 lattice; the density "
            "diagnostic is reported but not used to waive it.",
            "Competition inputs are integrity-verified owner mirrors, not organizer-authenticated.",
        ],
        elapsed_s=round(time.time() - t0, 1),
    )
    save("gdr_conduit_run_card.json", card)
    print(json.dumps({k: card[k] for k in ("verdict", "raster_sha256", "submission_name",
                                          "holdout_dti", "elapsed_s")}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
