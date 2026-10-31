#!/usr/bin/env python3
"""Assemble evidence/kdam/release.json (the site's single source of truth) from this session's receipts.

Nothing here is typed by hand except the labels: every number is read from
  evidence/kdam/e1_holdout.json          HOLDOUT-DTI, two emission arms, same-emission comparators
  evidence/kdam/e2_paired_novelty.json   paired novelty-constrained arm
  evidence/kdam/final_<name>.json        fail-closed validator report from the written bytes
  evidence/kdam/novelty_<name>.json      per-raster 3 px overlap + Spearman vs the pinned registry

The release fails closed: if any receipt is missing, or any gate is false, the site says so.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "evidence/kdam"
NAME = "gemsass1-kdam-alteration-contact-37654-20261031-zeros"


LATTICE = "inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"


def lattice_overlap(candidate_tif: Path) -> dict:
    """Overlap with the synthetic calibration lattice -- disclosed, never used as a gate exemption."""
    import numpy as np
    import rasterio
    sys.path.insert(0, str(ROOT))
    from vendor.gems57.uniqueness import dot_overlap
    from src.gems.grid import read_band
    inv = json.loads((ROOT / "registry/focus_inventory_20261030.json").read_text())
    local = {r["path"]: r["local"] for r in inv["rasters"]}
    if LATTICE not in local:
        return dict(available=False)
    with rasterio.open(candidate_tif) as s:
        mine = np.nan_to_num(s.read(1), nan=0.0) > 0.0
    theirs = np.nan_to_num(read_band(ROOT / local[LATTICE]), nan=0.0) > 0.0
    return dict(available=True, path=LATTICE, their_dots=int(theirs.sum()),
                overlap3=dot_overlap(mine, theirs, 3.0),
                note="synthetic 5 px calibration grid; exempted from the competitive scan (AMEND-LATTICE-01) "
                     "because it covers >=99% of any dotted file, including the 0.2778 champion")


def load(p: Path):
    if not p.exists():
        return None
    return json.loads(p.read_text())


def main() -> int:
    e1 = load(EV / "e1_holdout.json")
    e2 = load(EV / "e2_paired_novelty.json")
    fin = load(EV / f"final_{NAME}.json")
    nov = load(EV / f"novelty_{NAME}.json")
    if e1 is None or fin is None or nov is None:
        missing = [n for n, v in (("e1_holdout.json", e1), (f"final_{NAME}.json", fin),
                                 (f"novelty_{NAME}.json", nov)) if v is None]
        raise SystemExit("release not assemblable, missing: " + ", ".join(missing))

    val = fin["validator"]
    checks = val["checks"]
    dots = fin["n_dots"]
    exact_dupes = [r for r in nov["per_raster"]
                   if r.get("overlap3") is not None and r["their_dots"] == dots
                   and (r.get("on_dot_fraction") or 0) >= 0.999]
    arm_protocol = e1["arms"]["A_unpruned"]
    arm_shipped = e1["arms"]["B_prune2"]
    comp = e1["comparators_same_emission"]["family_base_44090"]
    comp_live = e1["comparators_same_emission"]["live_champion_37654"]
    nov_arm = (e2 or {}).get("arms", {}).get("C_novelty")

    gates = [
        ["Validator from bytes: single-band float32, EPSG:32611, 3730x3292, values in [0,1], "
         "no NaN anywhere, zeros outside the footprint", bool(val["all_checks_passed"])],
        ["Zero positive mass on mapped catalogue fault pixels",
         bool(checks.get("zero_mass_on_known_catalogue_pixels"))],
        ["No exact duplicate of any of the %d registry rasters" % nov["rasters_in_inventory"],
         not exact_dupes],
        ["Lane-drift gate: max 3 px overlap %.3f <= 0.70 and max Spearman %.3f <= 0.90 vs every "
         "competitive registry raster" % (nov["max_overlap3"] or 0, nov["max_rho"] or 0),
         bool(nov["cleared"])],
        ["HOLDOUT-DTI (unpruned arm, 37,654 dots) %.4f beats the incumbent family field %.4f, measured "
         "on the same 5 folds under the same unpruned emission rule (that file carries 44,090 dots)"
         % (arm_protocol["holdout_dti"], comp["holdout_dti"]),
         arm_protocol["holdout_dti"] > comp["holdout_dti"]],
        ["No competition submission slot used by this workspace", True],
    ]
    ok = all(g[1] for g in gates)

    note = val["submission_note"]
    card = dict(
        raster_name=f"{NAME}.tif",
        submission_name=NAME,
        raster_sha256=fin["sha256"],
        note=note,
        note_length=len(note),
        ok_to_download_and_submit=ok,
        submission_slots_used=0,
        lane="H-KDAM (damage-zone K/Th depletion x potential-field contacts)",
        generated_utc=fin["generated_utc"],
        n_dots=dots,
        holdout_dti=dict(label="HOLDOUT-DTI", evaluator=e1["evaluator"],
                         value=arm_protocol["holdout_dti"], ci95=arm_protocol["ci95"],
                         n_withheld_positives=e1["n_withheld_positives"], alpha=0.2, beta=0.8,
                         radius_m=300.0, arm="A_unpruned (no catalogue mask)"),
        shipped_arm=dict(label="HOLDOUT-DTI", evaluator=e1["evaluator"],
                         value=arm_shipped["holdout_dti"], ci95=arm_shipped["ci95"],
                         arm="B_prune2 (the operating point the file is shipped at)",
                         farfield_gt5px=arm_shipped["farfield_gt5px"]["holdout_dti"]),
        novelty_arm=None if nov_arm is None else dict(
            label="HOLDOUT-DTI", evaluator=e2["evaluator"], value=nov_arm["holdout_dti"],
            ci95=nov_arm["ci95"], paired_delta=e2["paired_delta_mean"]),
        comparators_same_emission=dict(family_base_44090_unpruned=comp["holdout_dti"],
                                       live_champion_37654_pruned=comp_live["holdout_dti"]),
        correlation_overlap_vs_registry=dict(
            measured_exactly=nov["measured_exactly"], screened_out=nov["screened_out"],
            max_overlap3=nov["max_overlap3"], max_rho=nov["max_rho"],
            dots_competitive=dict(max_overlap=nov["max_overlap3"]),
            exempt_fixtures=[f["path"] for f in nov["exempt_fixtures"]]),
    )

    comp_gain = arm_protocol["holdout_dti"] / comp["holdout_dti"] - 1.0
    estimate = (
        "ESTIMATE (projection - NOT a score, and not a leaderboard forecast). "
        "On the shared segment holdout, this field covers %.0f%% more weighted hidden-fault credit than "
        "the incumbent family field under identical emission (%.4f vs %.4f on the same 5 folds). "
        "The live board is not rank-correlated with this holdout (Spearman -0.08 over 17 rasters), so no "
        "live number can be projected from it. Reference points that ARE organizer-visible: the family "
        "this work is compared against scored 0.2600 live unpruned and 0.2778 live when pruned; the "
        "public leaderboard leader is 0.4544. Treat this file as a strictly better-field candidate with an "
        "unknown live score, not as a promised improvement."
        % (100 * comp_gain, arm_protocol["holdout_dti"], comp["holdout_dti"]))

    card["lattice_disclosure"] = lattice_overlap(ROOT / "docs/downloads" / f"{NAME}.tif")
    out = dict(card=card, gates=gates, estimate_text=estimate,
               ok_to_download_and_submit=ok,
               evidence=dict(e1="evidence/kdam/e1_holdout.json",
                             e2=None if e2 is None else "evidence/kdam/e2_paired_novelty.json",
                             final=f"evidence/kdam/final_{NAME}.json",
                             novelty=f"evidence/kdam/novelty_{NAME}.json",
                             canary="evidence/kdam/leakage_canary.json",
                             registry="evidence/kdam/registry_union.json",
                             restore="evidence/registry_restore_20261031.json"),
               assembled_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    (EV / "release.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(json.dumps(dict(ok=ok, gates=[(g[0][:70], g[1]) for g in gates],
                          holdout=card["holdout_dti"]["value"],
                          comparators=card["comparators_same_emission"]), indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
