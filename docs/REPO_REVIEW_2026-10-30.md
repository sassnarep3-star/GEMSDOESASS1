# Repository review — 2026-10-30

## Decision

**No TIFF is approved for DrivenData upload, and none was generated in this review.** Do not submit any file from this checkout.

- The two existing negative research TIFFs still fail the literal duplicate rule against a refreshed registry of 489 TIFF blobs from the nine focus repositories. **H-PBSC** is **99.48%** within 3 px of the GEMSDOE24 calibration lattice. **SWGB** is **99.87%**. Both are flagged as duplicates by the shared, unmodified audit on the overlap rule (70%). Their rank correlations are low (maximum 0.071 and 0.044, below the 0.90 limit), so the failure is the overlap rule alone. These are negative results, not candidates.
- A second, independent fail-closed blocker: one registry file, `GEMSDOE31 docs/downloads/gemsdoe31-csdu-stepover-8cf9dc27-nan.tif`, has 2,610,312 non-finite cells inside the footprint. The audit therefore can never be comparison-complete, and by its code it can never set `cleared: true` for any candidate, whatever the lattice decision. This file was already in the frozen registry. The README had noted it only as "One prior has nonfinite footprint values".
- A new unique competition TIFF **cannot be cleared under the current written rules** on the evidence so far. The two competitive-size dot rasters measured against the lattice (H-PBSC, 37,654 dots; SWGB, 44,090 dots) both land within 3 px of it, and the earlier BGAC run reported 100% directed overlap with a registry lattice. The obstruction is a *policy* question (whether calibration rasters belong in the novelty registry), not a missing file. The protocol forbids silently changing that threshold or exempting the lattice. A decision by the project owner is needed. See [Limitations](#limitations-and-access-needed).
- **Scores:** The highest reported score for the nine focus sites is **GEMSDOE32 0.2778**, an owner report with bytes verified but no submission receipt. The highest leaderboard figure with a dated official-snapshot is **0.4413 (2026-10-25)**. The owner ledger also contains **0.4544 (2026-10-28)**, which this repo cannot confirm. The brief's 0.3195 is out of date. See [`knowledge/leaderboard_evidence_20261030.md`](../knowledge/leaderboard_evidence_20261030.md).

## What was run today

All commands ran in `/home/user/GEMSDOESASS1` on branch `arena/0262b24e-gemsdoesass1`, Python 3.11.2, with the pinned `requirements-lock.txt` installed in the git-ignored `.venv`.

| Check | Command | Result |
|---|---|---|
| Test suite, before this review's additions | `pytest -q` | 54 passed |
| Test suite, final tree | `pytest -q` | **59 passed**, 20 warnings (rasterio deprecation and georeference warnings in test fixtures). Includes the five new tests in `tests/test_registry_refresh.py` |
| Feed tests | `node --test tests/test_feed.mjs` | 5 pass, 0 fail |
| Site build + docs diff | `python scripts/build_site.py`, `python scripts/swgb_build_site.py`, `git diff --check` | Build deterministic; only new evidence JSON copies added under `docs/evidence/` |
| Release verification | `python scripts/verify_release.py` | **PASS** (final tree): strict JSON, nine site summaries, 182 local links, vendor/code hashes, no submission TIFF, no slots |
| Entry points | `python scripts/check_release_entrypoints.py` | **PASS**: 5 entry points blocked |
| SWGB correction | `python scripts/verify_swgb_correction.py` | **PASS**: negative release, artifact hash intact |
| Network reachability | `curl` to each official host | `github.com`, `api.github.com`, `codeload.github.com`: responded. DrivenData leaderboard and competition pages, USGS, GDR (`gdr.openei.org`), NLR (`docs.nlr.gov`), EPSG.io and the owner `github.io` pages: **no HTTP response (code 000)** |

Measured results, with the artifacts that hold them:

1. **Frozen registry is intact.** `registry/focus_inventory.json` sha256 is `0e52bd80bc93ab9610c35d5f47818da4f86dfdd340689ad6b7522c25bfe74e09`, the same as the committed bytes. The release pin for `scripts/registry_snapshot.py` also holds (`48127b25…`).
2. **Owner repos have moved since the pins.** All nine focus repositories have a newer `main` head than the 2026-10-27 snapshot, with commit dates 2026-10-29. Evidence: [`evidence/owner_head_drift_20261030.json`](../evidence/owner_head_drift_20261030.json).
3. **Refreshed registry is complete and additive.** A new manifest, [`registry/focus_inventory_20261030.json`](../registry/focus_inventory_20261030.json), lists 489 TIFF blobs outside `data/`, every one verified by Git blob SHA1 and size, with zero failures. Every frozen (repo, blob) entry is still present, so no frozen file disappeared.
4. **Literal novelty audit against the refreshed registry.** [`evidence/registry_refresh_20261030.json`](../evidence/registry_refresh_20261030.json). Rules: rank correlation above 0.90, or more than 70% of dots within 3 px, is a duplicate. Footprint is `isfinite(sample_submission)`, 5,167,373 cells.
   - H-PBSC (`2f3bd24e…`, 37,654 dots): duplicate, directed overlap **0.994848** (matches the 99.48% in the earlier audit), max rank correlation 0.071.
   - SWGB (`f98c20df…`, 44,090 dots): duplicate, directed overlap **0.998707** (matches 99.87%), max rank correlation 0.044.
   - The audit is **not comparison-complete** (the GEMSDOE31 csdu `nan` file is non-finite inside the footprint, see irregularity 8), so both results are fail-closed: `cleared: false`, which is correct.
5. **Positive control.** Registry raster `GEMSDOE24/…-zero.tif` audited against itself gives directed overlap **1.0** and rank correlation **1.0**, so the detector does fire on a true self-match. The audit-level first hit was a different file, its `-nan` sibling (see irregularity 3).
6. **0.2778 bytes.** The owner's GEMSDOE32 zeros file has sha256 `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9`, matching the owner ledger. Its format: float32, EPSG:32611, 3730 × 3292, 100 m cells, transform origin (243350, 4508550), values {0, 1}, no NaN, 37,654 positive cells. This verifies the **file**, not the score.
7. **Sample submission.** `data/bridge/sample_submission.tif` has the same grid, float32 with NaN outside the footprint (7,111,787 NaN cells), 60,988 positive cells. The 0.2778 zeros file has 0 NaN and zeros outside. Two valid-looking grids, different fill.

## Irregularities for manual review

1. **Leaderboard figures conflict.** The brief says 0.3195 is "the highest score right now" and also cites 0.4413 as the current GEMSDOE high. The owner ledger has 0.4413 (2026-10-25) and 0.4544 (2026-10-28, labelled "ORGANIZER-CONFIRMED" by the owner). A leaderboard read is not a submission receipt, so this repo does **not** adopt that label. Re-read the official page with a dated capture.
2. **Two reads disagree on rank-3** (0.3904 on 2026-10-25, 0.3911 on 2026-10-28), and 0.3195 moves from rank 1 (2026-10-03) to rank 26 (2026-10-28).
3. **The same prediction exists under two nodata fills.** The GEMSDOE24 files `24GEMSDOE-ventrad-blind-geothermal-20261028-34b558b554fb-zero.tif` and `…-nan.tif` have identical values inside the footprint and differ only outside it (0 vs NaN). Both are in the registry, so they count as one prediction for uniqueness. The owner ledger does not list this pair.
4. **Owner reports of NaN-outside files conflict with the "[0,1]" explanation.** Several owner files that the owner reports as scored carry NaN outside the footprint (for example GEMSDOE31 `h27-4-solo-d28-…-nan`, reported 0.2708, which has 7,111,787 NaN cells outside the footprint and none inside; the same holds for the other `-nan` files that match user-reported names). If those reports are accurate, NaN outside the footprint is not the portal's cause. The cause of the user's "Predicted values must be in range [0, 1]" error is **unknown**. Neither NaN, a sentinel, nor out-of-range values is diagnosed. The writer's stricter rule (no NaN anywhere) is a conservative choice, not proof of the cause.
5. **Stale uniqueness registry.** The frozen registry was pinned on 2026-10-27. Since then 74 TIFF blob identities (67 distinct byte contents) have appeared across the nine repos. The frozen registry therefore cannot support any new uniqueness claim. The refreshed manifest is the current reference, but it is still a snapshot and must be re-measured again before any upload.
6. **The 0.2778 file has no receipt.** It is an owner report, not an organizer receipt. The owner ledger cites "DrivenData submission page 2026-10-25", but no capture is stored here.
7. **Two counts for the same refresh.** 74 is the number of (repo, blob) identities; 67 is the number of distinct file contents across repos, since some new files are byte-identical in two repos. Both are reported.
8. **Two pre-existing registry files cannot be compared.** `GEMSDOE31 …csdu-stepover-8cf9dc27-nan.tif` has non-finite values inside the footprint, so it is recorded as unassessable and blocks clearance (see Decision). `GEMSDOE36 docs/downloads/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif` is a format fixture with an incompatible grid; the audit records it as not compared and it does not block completeness. Both are kept, not removed.
9. **Closest new file is below the limit for H-PBSC.** The closest post-freeze registry file to H-PBSC is 61.7% directed overlap (GEMSDOE24 `geo1-concealed-conduit`, `-nan` and `-zeros` variants, identical in-footprint values). That is below 70%, so H-PBSC's duplicate status comes from the lattice alone. The closest new file to SWGB is 54.1%.

## Tooling added (additive, no frozen file changed)

| File | Purpose |
|---|---|
| `scripts/registry_refresh.py` | Writes a **new** registry manifest and blob cache. Refuses to overwrite an existing manifest. Reuses `api`, `fetch` and `SITES` from `scripts/registry_snapshot.py`, which stays byte-identical because its hash is pinned in `evidence/release_checks.json`. |
| `scripts/audit_registry_refresh.py` | Runs the shared `novelty.audit` (literal rules, no exemption) for the negative candidates against the refreshed manifest, plus a self-match positive control. Refuses to overwrite its receipt. |
| `scripts/owner_head_drift.py` | Read-only. Compares frozen pins, refreshed pins and live heads, and counts new TIFF blobs. Writes evidence only. |
| `tests/test_registry_refresh.py` | Pins the frozen manifest hash, tests that the refresh tool refuses to overwrite, checks the refreshed manifest is complete and additive, and checks the receipt is fail-closed. |
| `knowledge/leaderboard_evidence_20261030.md` | Every leaderboard and score figure, its evidence class, and the irregularities above. |
| `evidence/run_card_20261030_review.json` | Protocol run card. Null where an artifact or score does not exist, with the reason. Verdict: negative. |

No experiment, raster generation, upload, or weekly-slot action was taken.

## Limitations and access needed

- **Official data and rules are not reachable.** DrivenData data, rules and leaderboard, USGS GeoDAWN, GDR, NLR and EPSG.io returned no response from this sandbox. To authenticate the format or the leaderboard, a session with access to those hosts is needed, and the capture must be stored with its hash.
- **No submission receipt exists.** Organizer acceptance, the weekly cap and the exact validator behaviour are unknown. A local format pass is not organizer acceptance.
- **Policy decisions required (two).** (a) Whether calibration and lattice rasters (for example `GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif`) belong in the novelty registry. If yes, competitive dot rasters cannot clear 70% at 3 px. (b) How to treat an unassessable registry file (the GEMSDOE31 `nan` file). Under the current fail-closed code it blocks every candidate. Either a dated amendment, or a corrected re-measurement of that file, is needed. The protocol forbids making either change silently or retroactively.
- **Owner mirrors are not organizer data.** Hash-pinned mirrors prove byte integrity against the owner repo, not origin, licence, or eligibility.
- **Holdout DTI is not a leaderboard forecast.** No calibration to the official DTI exists, so no leaderboard estimate is given.

## Hypotheses

No new hypothesis slate was written. The 2026-10-29 slate, [`knowledge/hypotheses_20261029.md`](../knowledge/hypotheses_20261029.md), already ranks candidates with their layers, signatures and differences from implemented work. It states that every candidate faces the same measured lattice gate. That still holds: no candidate can be emitted as a competitive-size dot raster until the policy in the previous section is decided.

## Next steps (ordered)

1. **Owner decision:** decide (a) whether the calibration/lattice rasters are in the novelty registry, and (b) how the unassessable GEMSDOE31 `nan` file is treated. Write each decision, its date and its reason into `knowledge/NEXT_STEPS.md`. Do not change the threshold retroactively.
2. **Re-read the official leaderboard** from an environment with access, with a dated capture and hash. Resolve the 0.3195 / 0.4413 / 0.4544 conflict and the rank-3 disagreement.
3. **Obtain a submission-page receipt** for any figure to be called ORGANIZER-CONFIRMED. Until then every score here is OWNER-REPORT or USER-REPORTED.
4. **Diagnose the "[0,1]" error** only with the exact uploaded file and a portal receipt. Until then, keep the stricter writer rule and say the cause is unknown.
5. **Re-run `scripts/registry_refresh.py` and `scripts/audit_registry_refresh.py`** immediately before any future candidate. The registry moves; a 2026-10-30 result is not a 2026-11 result.
6. **Only if a candidate clears** the agreed policy and beats the holdout bar with a compatible comparison: use the shared writer, validate the bytes, and keep selection and upload as a separate authorised step.

## Sources within this repository

- [Previous review, 2026-10-29](REPO_REVIEW_2026-10-29.md) · [executive summary](executive-summary.html) · [next steps](../knowledge/NEXT_STEPS.md)
- [Registry refresh receipt](../evidence/registry_refresh_20261030.json) · [owner head drift](../evidence/owner_head_drift_20261030.json) · [refreshed manifest](../registry/focus_inventory_20261030.json)
- [Leaderboard evidence ledger](../knowledge/leaderboard_evidence_20261030.md) · [run card](../evidence/run_card_20261030_review.json)
- [Frozen registry](../registry/focus_inventory.json) · [release hashes](../evidence/release_checks.json)

## Sources outside this repository (reachable from this sandbox)

- Owner score ledger: https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/score-ledger.csv
- GEMSDOE32 repository metadata: https://api.github.com/repos/buffedlizard55-lab/GEMSDOE32
- DrivenData reference solution (reachable, not re-audited here): https://github.com/drivendataorg/gems-prize-reference-solution

## Sources the sandbox could not reach

- DrivenData competition, data and leaderboard pages: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ · https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- GDR submission: https://gdr.openei.org/submissions/1391 · NLR format PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf · EPSG:32611: https://epsg.io/32611
