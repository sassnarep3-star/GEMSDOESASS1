# Next session — ordered actions (updated 2026-10-30)

## Added on branch arena/6c40af2c-gemsdoesass1 (nine-site board, 2026-10-30)

- **Eligibility is a blocking item main does not list.** Official rules §1.3 limit competitors to U.S. citizens or permanent residents, or U.S.-incorporated entities. The user's location is Singapore. Confirm with the administrator before any upload, and do not sign the eligibility certification unless it is true. This also blocks any selector slot, including under an amended uniqueness test.
- **SWGB has two holdout numbers, both above the bar.** E2 (2 px prune, the run-card headline) is 0.1586 [0.1519, 0.1649]. The shipped 6 px prune is 0.1401 [0.1329, 0.1452]. Both beat the 0.1011 [0.0956, 0.1072] bar. Both are withdrawn by the lattice gate.
- **Nine-site board:** `evidence/nine_site_board.json` (byte-verified best files, registry-wide overlap, exact dot-set duplicates). Arithmetic bound under the literal rule: a file above **22,163** positive pixels cannot pass. `evidence/format_validation_nine_best.json`: 9/9 best files pass the official format text. Run card: `evidence/run_card_20261030_nine_site.json`.
- **Verified sources and irregularities:** `knowledge/sources_verified_20261030.md`. Ranked hypotheses, none run: `knowledge/hypotheses_20261030.md`.

**No file in this repository is cleared to download or submit.** Latest decision and measurements: [`knowledge/REVIEW_2026-10-30.md`](REVIEW_2026-10-30.md), [`evidence/gate_null_audit.json`](../evidence/gate_null_audit.json), [`evidence/run_card_20261030.json`](../evidence/run_card_20261030.json).

1. **Decide the uniqueness policy (user).** The 70%/3 px rule is saturated by the 13gems 5 px lattice: uniform-random dots score 99.88%. Options A (null-calibrated amendment, recommended), B (keep literal rule, nothing submittable), C (exclude the lattice; rejected for now). Write any chosen amendment and its thresholds down **before** running anything.
2. **If A is chosen:** re-run `scripts/gate_null_audit.py` under the amended rule and record the outcome in a new run card. SWGB 6 px prune (`0.1401`, HOLDOUT-DTI, 60,988 withheld positives) is the only shipped candidate with a holdout above the 0.1011 bar. It still needs one selector decision and a receipt-backed rules check. It is not a leaderboard forecast.
3. **Verify `labels.tif`.** It is byte-identical to `existing_faults.tif` (sha256 `7ba308cc…`). Confirm against the organizer's labels, which are login-walled. Until then, treat local "labels" results as catalogue-only.
4. **Read the live leaderboard in a browser** and record the timestamp. The cached page shows #1 0.4544; the request cites 0.4413 and 0.3195.
5. **Resolve the portal error.** The official text permits NaN outside the bounds. Whether NaN caused "Predicted values must be in range [0, 1]" is unverified. Get a receipt before changing the writer.
6. **Fix `scripts/fetch_reference_assets.sh`** (sparse clone misses `data/bridge/*`) or retire it in favour of `scripts/prepare_data.py` + `scripts/registry_snapshot.py`, which are verified working.
7. **Use `SWGB` run card's shipped-variant number** (0.1401) in any new page. The headline 0.1586 is the 2 px prune variant.
8. **Only then** run a new lane: 3–5 hypotheses ranked in `knowledge/hypotheses_20261029.md` or newer, single-feature canaries (AUC > 0.90 = leakage), HOLDOUT-DTI with CI, the repaired gate, validator, run card. Budget: 3 experiments or 2 hours.
9. Limitation to keep in view: holdout→live calibration is Spearman −0.081 over 17 rasters. A better holdout number does not guarantee a better leaderboard score.

## Added on branch arena/5ab44a21-gemsdoesass1 (H-TSFX, 2026-10-30)

- **H-TSFX holdout passed but the shipped dots are a duplicate.** HOLDOUT-DTI 0.1587 [0.1522, 0.1658]; sweep best 0.1674 is selected on the same holdout. Shipped dots are 70.2–72.3 % within 3 px of 11 GEMSDOE25 rasters, so the protocol stops placement. No TIFF written. Record: [`RESULTS_20261030.md`](RESULTS_20261030.md), [`../evidence/tsfx/run_card.json`](../evidence/tsfx/run_card.json), pre-registration [`hypotheses_20261030_tsfx.md`](hypotheses_20261030_tsfx.md).
- **Shipped-file diagnostic (0.0015) is structural**, not a live estimate: the full-catalogue 2 px prune removes dots near withheld faults. Any future holdout of a full-catalogue-pruned file must be scored that way explicitly.
- **`scripts/fetch_reference_assets.sh` is fixed** (item 6 above): sparse patterns and checksum paths corrected; verified 23/23 assets.
- **Eligibility (§1.3) stays a blocking item** as listed above; this branch does not resolve it.
