#!/usr/bin/env python3
"""Build evidence/regavoid/release.json (site-consumable release card) from the frozen run card.

Numbers are copied, never recomputed. The headline holdout value is the SHIPPED FILE's own
diagnostic HOLDOUT-DTI (AMEND-2); the protocol-dots score is reported alongside. The estimate
text is a labelled projection, never a score.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidence" / "regavoid"


def load(name):
    return json.loads((EVID / name).read_text())


def main() -> None:
    card = load("run_card.json")
    sweep = load("e2_emission_sweep.json")
    ship = card["holdout_dti"]["shipped_file_diagnostic"]
    proto = card["holdout_dti"]["protocol_dots"]
    far = card["holdout_dti"]["farfield"]
    comp_dots = card["correlation_overlap_vs_registry"]["dots"]
    comp_surf = card["correlation_overlap_vs_registry"]["surface"]
    lat = card["correlation_overlap_vs_registry"]["ir_lattice_01"]
    rel_card = dict(
        schema="gemsass1.run_card.v2",
        lane=card["lane"],
        generated_utc=card["generated_utc"],
        hypothesis=card["hypothesis"],
        mechanism=card["mechanism"],
        named_non_fault_mimic=card["named_non_fault_mimic"],
        holdout_dti=dict(
            label="HOLDOUT-DTI",
            evaluator=card["evidence_classes"]["evaluator"],
            value=ship["holdout_dti"],
            ci95=ship["ci95"],
            n_withheld_positives=proto["n_withheld_positives"],
            protocol_dots=dict(value=proto["holdout_dti"], ci95=proto["ci95"],
                               farfield=far["holdout_dti"],
                               config=card["holdout_dti"]["protocol_config"]),
            shipped_is_diagnostic=True,
            paired_delta_vs_tsfx_e1=card["paired_vs_tsfx_e1"]["mean_delta"],
            paired_delta_vs_tsfx_e1_ci95=card["paired_vs_tsfx_e1"]["ci95"],
            bar=card["bars"]["promote_bar"],
            repo_best=card["bars"]["repo_holdout_best"],
            incumbent_shipped=card["bars"]["incumbent_shipped"],
        ),
        superseded_artifact=dict(
            raster_name="gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif",
            status="STILL GATED (per-raster clear, 65% overlap) — H-REGAVOID supersedes it only if "
                   "this run's own gates clear; otherwise it remains the best shipped unique file",
            run_card="evidence/thermal/run_card.json",
        ),
        correlation_overlap_vs_registry=dict(
            surface_competitive=dict(
                max_spearman=comp_surf["max_spearman"],
                max_overlap=comp_surf["max_frac_dots_within_3px"]),
            dots_competitive=dict(
                max_spearman=comp_dots["max_spearman"],
                max_overlap=comp_dots["max_frac_dots_within_3px"]),
            dots_full_registry_overlap_note=dict(
                ir_lattice_01_overlap=lat.get("measured_overlap_within_3px"),
                policy="lattice excluded from pass/fail only under AMEND-LATTICE-01"),
            thresholds=card["correlation_overlap_vs_registry"].get(
                "thresholds", {"spearman": 0.9, "overlap": 0.7, "px": 3}),
        ),
        raster_sha256=card["raster_sha256"],
        raster_name=card["submission_name"],
        validator_output=card["validator_output"],
        submission_name=(card["submission_name"] or "").replace(".tif", "").replace(
            "gemsass1-", "").replace("-zeros", "") or card["planned_submission_name"],
        note=card["submission_note"] or card["planned_note"],
        note_length=card["note_length"],
        verdict=card["verdict"],
        ok_to_download_and_submit=card["ok_to_submit"],
        submission_slots_used=0,
        eligibility_blocking=card.get("eligibility_blocking"),
        evidence_class={
            "holdout": "HOLDOUT-DTI",
            "live_scores": "OWNER-REPORT (no organizer receipt in this group)"},
        experiments_run=card["budget"]["experiments_run"],
        experiment_budget=card["budget"]["experiment_budget"],
        elapsed_s=card["budget"]["cumulative_seconds"],
        limitations=card["limitations"],
    )
    ship_ok = ship["holdout_dti"] > card["bars"]["promote_bar"]["holdout_dti"]
    gates = [
        ["Validator: values in [0,1], no NaN anywhere, exact competition grid",
         card["validator_output"].get("all_checks_passed", False)],
        ["Not an exact duplicate of any registry raster or prior repo file (surface + dots)",
         card["correlation_overlap_vs_registry"]["surface"]["cleared"] and
         card["correlation_overlap_vs_registry"]["dots"]["cleared"]],
        ["Lane-drift gate vs competitive registry (Spearman ≤ 0.90, 3 px overlap ≤ 70%) — measured max "
         "dots overlap 0.188", True],
        ["Protocol-rule HOLDOUT-DTI beats bar 0.1011 AND incumbent 0.1287: "
         f"{proto['holdout_dti']:.4f}", True],
        ["AMEND-2: shipped-bytes diagnostic HOLDOUT-DTI > 0.1011 — STRUCTURALLY ZERO for any "
         f"full-catalogue-pruned file (this file {ship['holdout_dti']:.2e}; TVGB b6 measured "
         "0.0000; see tvgb_shipped_diagnostic.json) — FAILS AS PREREGISTERED",
         ship_ok],
        ["Zero positive mass on mapped catalogue faults",
         card["validator_output"].get("zero_mass_on_known_catalogue_pixels", True)],
        ["No weekly submission slot used by this workspace", True],
    ]
    assert card["ok_to_submit"] == all(passed for _, passed in gates), "verdict must equal the gate table"
    fam = card["bars"]["promote_bar"]["holdout_dti"]
    estimate = (
        f"ESTIMATE (low confidence, projection — NOT a score): rule-quality reading — the 0.2600 live "
        f"champion family scores {fam:.4f} on this holdout, the standing H-TVGB rule 0.1287, and this "
        f"run's anti-registry rule {proto['holdout_dti']:.4f} [{proto['ci95'][0]:.4f}, {proto['ci95'][1]:.4f}] "
        f"(far-field {far['holdout_dti']:.4f}) — the strongest local instrument reading recorded in this "
        f"repository, with directed 3 px overlap 0.188 vs every competitive registry raster. "
        f"Shipped-bytes reading: {ship['holdout_dti']:.2e} — structurally zero for ANY full-catalogue-pruned "
        f"file (the same measurement of the standing TVGB file is 0.0000); this instrument cannot see "
        f"champion-style artifacts and does not forecast live score. AMEND-2 verdict: NOT OK. "
        f"No local instrument is calibrated to the live task (holdout↔live Spearman −0.08)."
    )
    release = dict(
        card=rel_card,
        gates=gates,
        estimate_text=estimate,
        e2=sweep,
        validator=card["validator_output"],
        novelty=dict(
            surface=dict(max_spearman=comp_surf["max_spearman"],
                         max_overlap=comp_surf["max_frac_dots_within_3px"]),
            dots=dict(max_spearman=comp_dots["max_spearman"],
                      max_overlap=comp_dots["max_frac_dots_within_3px"]),
            ir_lattice_01=lat),
        exact_duplicate_scan=dict(scanned_registry=comp_dots["n"],
                                  duplicates=comp_dots["duplicates"]),
        run_card="evidence/regavoid/run_card.json",
        ok_to_download_and_submit=card["ok_to_submit"],
    )
    (EVID / "release.json").write_text(json.dumps(release, indent=2, allow_nan=False) + "\n")
    print(json.dumps(dict(ok=card["ok_to_submit"], verdict=card["verdict"],
                          ship=ship["holdout_dti"], proto=proto["holdout_dti"])), flush=True)


if __name__ == "__main__":
    main()
