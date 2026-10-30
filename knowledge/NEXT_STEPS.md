# Next session — ordered actions (updated 2026-10-30)

## Added on branch arena/0262b24e-gemsdoesass1 (registry refresh, 2026-10-30)

- **Blocking: GEMSDOE31 `-nan` registry file is unassessable.** `gemsdoe31-csdu-stepover-8cf9dc27-nan.tif` has 2,610,312 non-finite cells inside the sample footprint. The fail-closed audit therefore reports `comparisons_complete = false` and blocks clearance for every candidate. This is independent of the lattice policy. Owner decision needed on how to treat the file (see the review's policy section); no silent exemption.
- **Refreshed registry: 489 rasters, two independent builds agree.** The API build is `registry/focus_inventory_20261030_api.json`. The local-git build is `registry/focus_inventory_20261030.json` (staged from main). Both match on (repo, path, blob) sets and head refs. The frozen pin `registry/focus_inventory.json` is unchanged and must not be overwritten.
- **Owner heads moved for all nine focus repos since the pin** (74 new TIF blobs). Refs are in [`docs/REPO_REVIEW_2026-10-30-registry-audit.md`](../docs/REPO_REVIEW_2026-10-30-registry-audit.md).
- **Leaderboard read confirmed 2026-10-30 (fetch tool):** #1 xiaofanhu 0.4544 (35 submissions), #2 cfld__ 0.3916, #3 Batik Shirt Brothers 0.3915, #48 kpomazi 0.3195. Class is OFFICIAL-LEADERBOARD-READ, not ORGANIZER-CONFIRMED (no submission receipt). The 0.4413 figure is older. Evidence: [`knowledge/leaderboard_evidence_20261030.md`](leaderboard_evidence_20261030.md).
- **Access note:** DrivenData, NLR, GDR and EPSG.io were reachable through the fetch tool on 2026-10-30. The bash sandbox cannot reach them (curl returned 000). Earlier "unreachable" statements apply to bash only.
- **Eligibility is still open** (rules §1.3, see the first item above). The NLR rules say individuals must be U.S. citizens or permanent residents. Private entities must be incorporated in and keep a primary place of business in the U.S. Do not upload until the administrator confirms.

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
