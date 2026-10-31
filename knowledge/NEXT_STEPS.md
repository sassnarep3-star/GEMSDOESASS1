# Next session — ordered actions (updated 2026-10-30 after the H-TVGB release)

> Two parallel sessions wrote this file on 2026-10-30. Part 1 is the H-TVGB thermal-lane release
> record; Part 2 (verbatim, not edited) is the nine-site-board session's record with different
> conclusions. **Read both.** The eligibility finding in Part 2 and the uniqueness-policy question
> are blocking user decisions.

## Part 1 — H-TVGB thermal-lane release

1. **Selector decision on the generated H-TVGB file.**
   `docs/downloads/gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif`
   passes every automatic gate under the per-raster reading of the lane-drift rule (format
   validator, exact-duplicate scan vs 414 registry rasters + repo priors, per-raster novelty gates:
   surface Spearman ≤ 0.133, dots 3 px overlap 65.0% ≤ 70% vs the competitive registry;
   HOLDOUT-DTI 0.1287 [0.1231, 0.1355] at the shipped config vs bar 0.1011; far-field restricted
   0.1343). The superseded 2 px packaging is logged as a lane-drift duplicate
   (`evidence/thermal/run_card_b2_duplicate_log.json`, 79.1% vs `gems25-h38-greedy-credit-k3p5`)
   and must not be uploaded. Spending a weekly slot is a separate selector decision — and see
   Part 2's **eligibility** item first.
2. **Ratify or reject the lattice scope readings (user).** Part 2's lattice-bound analysis shows
   the literal full-registry 70%/3 px rule is unsatisfiable for any competitive dotted file
   (the 13gems lattice covers ≥99%). The H-TVGB run card reports both readings
   (`dots_competitive` per-raster vs `dots_full_registry` 99.79% vs the lattice); the amendment
   draft is `evidence/thermal/lattice_amendment.md`, and Part 2's options A/B/C
   (null-calibrated amendment vs literal rule vs registry exclusion) are the policy menu.
   **No file is uploaded until the policy is chosen in writing.**
3. **Resolve eligibility (user, blocking).** Per Part 2: rules §1.3 limit competitors to U.S.
   citizens/permanent residents or U.S.-incorporated entities; the user's location is Singapore.
   Confirm with the administrator before any upload; do not sign an eligibility certification
   unless it is true.
4. **Beat 0.3195 with field quality, not emission.** The H19-5 emission ladder is exhausted at
   0.2778 (0.2600 → 0.2708 → 0.2778 came only from deleting near-catalogue dots). The supervised
   family is the only local instrument above the 0.2600 base (HOLDOUT-DTI 0.129–0.152 vs 0.1011).
   Concrete steps: (a) add tip/step-over geometry and orientation-persistence features and re-run
   the paired ablation; (b) raise far-field credit (0.134–0.141 vs pooled 0.129–0.152); (c) re-test
   the geothermal family as an EMISSION prior (concentrate dots near warm-spring/sinter/2 mDAB
   anchors) — as learner features it is a measured negative (paired Δ −0.0124 [−0.0170, −0.0079]).
5. **Emission sensitivity exists but is out of the preregistered operating point.** E3 measured
   0.1516 [0.1445, 0.1574] at 52,000 dots / >2 px prune and far-field best 0.1408 at 52k / >6 px,
   vs 0.1287 shipped (37,654 / >6 px). The champion operating point is fixed by live evidence;
   a future selector preferring holdout-optimal mass has the sweep one step away.
6. **Keep the frozen negatives.** Do not delete or soften `evidence/run_card.json` (BGAC-1),
   `evidence/pbsc/run_card.json`, `evidence/swgb/`, the lattice audits, or the B2 duplicate log.
   New evidence goes in new directories.
7. **Read first next session:** this file, `README.md` (project prompt appendix + Part 2's
   instrument-irregularity section), `knowledge/PROJECT_BRIEF.md`,
   `knowledge/hypotheses_20261030.md` (both parts), `evidence/thermal/run_card.json`,
   `evidence/thermal/release.json`, and Part 2's `knowledge/REVIEW_2026-10-30.md`.

---

## Part 2 — parallel-session record (nine-site board, 2026-10-30) — preserved verbatim

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
