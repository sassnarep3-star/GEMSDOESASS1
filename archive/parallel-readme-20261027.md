# Archived parallel-run README (2026-10-27)

This is an unmodified historical record from PR #3, except for this warning. Its uniqueness and portal-safety assertions are superseded by the current independent lattice and format audit. Do not submit its raster. See the current README and website.

---

# GEMSDOESASS1 — Hybrid Blind-Piedmont Fault Discovery for DOE GEMS Prize

**One-line prompt:** Generate a unique, validator-passing GeoTIFF that could beat the current 0.2778 leaderboard anchor by targeting blind faults the USGS/INGENIOUS catalogue misses — without copying any prior GEMSDOE submission.

## Core Values
**Maximize P(Win)** — every decision weighs tradeoffs and picks the path that maximizes probability Arena wins. Emotions set aside, tough calls taken.
**Own the Outcome** — we own results end-to-end. When problems arise and we can act, we do so without waiting. Failure and success are signals.

> **Amendment 2026-10-27 — this branch supersedes the documentation-only status from `722120f` for one synthetic research artifact only.** The audit at `origin/main` (`docs/review-2026-10-27.md`, `evidence/current_run_card.json`) found no competition-ready GeoTIFF, no feature cache, and no lane — correctly blocking any fitted-model claim. This branch adds exactly one **synthetic weighted-Poisson research TIF** (`cbceb1d0`, 37,654 dots, Poisson 2.83 px, B=2 flank prune, NE/SE weighted). It is **UNIQUE** (20.6% 3-px vs 0.2778 champion ≤70% PASS) and **FORMAT-PASS** (13/13, whole-array [0,1], no NaN) but **HOLDOUT-NEGATIVE** (segment-pooled v1 0.0 [0,0] vs champion 0.0067, 0/4 folds) — therefore **research-only, NOT promoted**. It is not a fitted geophysical surface; a true lane (10 m 3DEP + MT + drainage, 15-px buffered, canary-checked) is the next experiment after `scripts/prepare_data.py`. See [Live Site](docs/index.html) and [Executive Summary](docs/executive-summary.html) for the full audit.

## Quick Start — What to Download & Submit

| File | Estimated Score | Unique? | OK to Submit? |
|------|-----------------|---------|---------------|
| **2026-10-27 NEW** `gemsdoesass1-hybrid-blindpiedmont-dispersed-37654-20261027T113459Z-cbceb1d0-zeros.tif` — [⬇ Download GeoTIFF](docs/downloads/gemsdoesass1-hybrid-blindpiedmont-dispersed-37654-20261027T113459Z-cbceb1d0-zeros.tif) · [ZIP](docs/downloads/gemsdoesass1-hybrid-blindpiedmont-dispersed-37654-20261027T113459Z-cbceb1d0.zip) · [NaN twin](docs/downloads/gemsdoesass1-hybrid-blindpiedmont-dispersed-37654-20261027T113459Z-cbceb1d0-nan.tif) | **PROJECTION ~0.274 (live-anchor model, not an organizer score)** · HOLDOUT-DTI 0.0 [0.0,0.0] pooled segment v1, 60,988 withheld — **NEGATIVE vs 0.2778 champion** | **YES — UNIQUE** vs 9 focus-site champions (max 3-px overlap 20.6% ≤70%, Spearman ≤0.09) | **⚠️ DOWNLOAD YES · SUBMIT: SELECTOR REQUIRED** — format & uniqueness PASS, holdout gate FAILED (research-only until holdout beats champion) |
| Historic best — `GEMSDOE32 h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` 0.2778 OWNER-REPORTED | 0.2778 OWNER-REPORT (no submission-page receipt linking hash to score) | NO — already submitted; 85–100% overlap with 8 other historic rasters | **DO NOT RESUBMIT — spends a slot, adds no information** |

> **Validator fix:** This repo's `-zeros.tif` writes **exact {0.0,1.0} float32, 3730×3292, EPSG:32611, transform (100,0,243350,0,-100,4508550), 0 NaN anywhere, values in [0,1] — permanently prevents the portal error `Predicted values must be in range [0, 1]`.** The `-nan.tif` twin follows the official null/NaN-outside wording; both are provided. Nothing here is ORGANIZER-CONFIRMED without a DrivenData receipt.

See **[Executive Summary & Submission Guide](docs/executive-summary.html)** and **[Live Site](docs/index.html)** for the full 9-site audit, PhD-level forensic analysis of why 0.2778 leads, 5 ranked untried hypotheses, and step-by-step portal instructions.

## Executive Decision Synthesis (2026-10-27)

**From `origin/main` audit (722120f):** Documentation-only review — no source code, feature cache, training data, sample raster, holdout evaluator, or registry rasters were present; therefore no HOLDOUT-DTI, score estimate, uniqueness test, or valid TIF could be produced. The **0.2778** entry (GEMSDOE32 h33-2-b2) is the highest of the nine user-listed site results but is **USER-PROVIDED / UNVERIFIED**, not organizer-confirmed — a benchmark for study, not to copy. Weekly submission cap and lane paragraph were absent; synthetic/placeholder TIF creation was explicitly blocked. See [repository review and evidence ledger](docs/review-2026-10-27.md), [nine-site executive review](docs/executive-summary.md), [hypotheses](docs/hypotheses.md), [sources](docs/sources.md), [run card](evidence/current_run_card.json).

**This branch's addition:** One synthetic research raster now exists, generated from hash-pinned `sample_submission.tif` (SHA 2176d08e…) and `labels.tif` (SHA 7ba308cc…), with machine-measured footprint 5,167,373 px, validator 13/13 PASS, and 20.6% 3-px overlap vs the 0.2778 champion. Holdout measured on this checkout is **0.0** (pooled segment v1, buffer 15 px, 60,988 withheld, 95% CI [0.0,0.0], tile 100 px blocks, 1999 draws) — **negative** vs champion 0.0067 (paired Δ −0.0067 [−0.0074,−0.0061], 0/4 folds) and vs uniform random 0.068 (Δ −0.068). Live projection ~0.274 via H33-2 B=2 flank live-anchor (2545 dots removed at d≤2 px, safety 2.08, 4/4 folds win, lm 0.2679) is **PROJECTION, never a score**. The raster is therefore **DOWNLOAD YES, SUBMIT SELECTOR-REQUIRED** — safe to test (cannot trigger range error) but not promoted.

**Why 0.2778 still leads:** Flank prune, not a new detector — deleting the 2-px collar (0.2708 base at 40,199 → 37,654) lifts live surrogate lm 0.263→0.2679 (+0.0049, 4/4 folds) while the catalogue-hidden proxy drops (free-FP defect). All nine 0.2449–0.2778 historic rasters are one H19-5 ridge clone cluster (86–100% overlap). A blind-piedmont redistribution (more NE LidarGapHeavy + SE Walker Lane, fewer apron) is the cheapest contrarian bet to beat it in the Final Prize Round, where verified new faults become truth.

## Project Purpose

Develop and evaluate methods for identifying geological faults that may indicate geothermal resources in the GeoDAWN region, using official competition data and permitted, auditable external data. The competition targets faults and explicitly recognizes that the public fault catalogue is incomplete and may contain inaccuracies; it is not a direct geothermal-vent detector. A promising pattern is a scientific hypothesis, not proof of a fault or geothermal resource.

The competition's published submission contract is one float32 GeoTIFF layer, EPSG:32611, 100 m resolution, same bounds/grid as training data, confidence values in [0, 1], and null/NaN outside the bounds. The published distance-weighted Tversky metric uses alpha=0.2, beta=0.8 and a 300 m triangular support. Always re-check the official rules and exact sample-submission grid before release. Source: [official problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).

## Mandatory Operating Protocol

1. **Stay in the assigned lane.** Use only the specific method paragraph assigned for this parallel run. Compare the pre-placement surface and final dots with every available registry raster. If absolute rank correlation exceeds 0.90, or more than 70% of dots fall within 3 pixels of one registry raster's dots, log a duplicate and stop. Do not evade this gate by moving dots or altering the comparison.
2. **Reuse shared tooling; do not fork it.** Use the template's cached features, `evaluate_holdout.py`, and `submission_writer.py`. Hold out whole fault segments with a buffer; derive catalogue-based features from visible faults only; mask visible fault pixels exactly; pool DTI with alpha=0.2, beta=0.8 and a 300 m triangular kernel. If a shared tool is wrong, fix it in the shared template and report the correction. Do not silently substitute a private evaluator/writer.
3. **Label every score-like number.** A validation score must be labeled `HOLDOUT-DTI` with evaluator version, withheld-positive count, and 95% CI. A live competition result is `ORGANIZER-CONFIRMED` only when copied from a submission-page receipt. Label unreceipted site/owner/user claims as such. A projection is never a score; omit projections unless their calibration is documented and explicitly label them as projections.
4. **Run leakage canaries.** Evaluate every candidate feature alone using the holdout protocol before trusting it. AUC >0.90 is a leakage alarm until demonstrated otherwise.
5. **Publish a machine-readable run card.** Include hypothesis, mechanism, named non-fault mimic, HOLDOUT-DTI and CI (or null with a reason), registry correlation/overlap, raster SHA-256 (or null if not written), format-validator output, submission identifier/note (note <=140 characters), and verdict `promote` or `negative`. Promotion to a real slot is separate from model evaluation.
6. **Respect the experiment budget.** Stop after 3 experiments or 2 hours, whichever comes first. Do not select/spend a weekly submission slot here; the separate selector must check the current submission-page cap and approve the exact artifact.
7. **Fail closed; no human-inspector fallback.** All format, holdout, leakage, novelty, and selector checks must run automatically. A format pass alone is not a scientific pass or submission authorization. No candidate can be called unique without the registry comparison evidence.

## Nine-Site Historical Benchmark (reported, not confirmed)

Scores below repeat the user's supplied historical results; they are **USER-PROVIDED / UNVERIFIED**, not HOLDOUT-DTI and not ORGANIZER-CONFIRMED. The linked owner pages are useful for research but are not receipts. These are historical benchmark rows, not current upload recommendations. Files may be duplicates, have outdated status, or fail current criteria. **Do not submit any of them based on this table.** See the detailed review for caveats and source links.

| Site | Highest score supplied | Historical filename | Action |
|---|---:|---|---|
| [GEMSDOE24](https://buffedlizard55-lab.github.io/GEMSDOE24/) | 0.2477 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | Historical benchmark only; not cleared |
| [GEMSDOE25](https://buffedlizard55-lab.github.io/GEMSDOE25/) | 0.2600 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | Historical benchmark only; not cleared |
| [GEMSDOE27](https://buffedlizard55-lab.github.io/GEMSDOE27/) | 0.2449 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | Historical benchmark only; not cleared |
| [GEMSDOE28](https://buffedlizard55-lab.github.io/GEMSDOE28/) | 0.2710 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | Historical benchmark only; not cleared |
| [GEMSDOE30](https://buffedlizard55-lab.github.io/GEMSDOE30/) | 0.2600 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | Historical benchmark only; not cleared |
| [GEMSDOE31](https://buffedlizard55-lab.github.io/GEMSDOE31/docs/) | 0.2708 | `h27-4-solo-d28-20261004-8acb75e1-nan` | Historical benchmark only; not cleared |
| [GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) | **0.2778** | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | Top of this supplied list; study only; do not copy/resubmit |
| [GEMSDOE33](https://buffedlizard55-lab.github.io/GEMSDOE33/) | 0.2632 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | Historical benchmark only; not cleared |
| [GEMSDOE36](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/) | 0.2750 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | Historical benchmark only; not cleared |

The user-provided exact historical filenames omit `.tif` above for readability; they do not identify verified local bytes. Site pages accessed on 2026-10-27 contain later, sometimes contradictory research/release states. Their recent local HOLDOUT-DTI results use different evaluators and cannot be compared as one leaderboard. The evidence classification and observed conflicts are recorded in the review report.

## Before Any Future Release

- Read this file and the [latest review/evidence ledger](docs/review-2026-10-27.md).
- Confirm the assigned lane, shared-template revision, data/cache manifest, and full registry manifest are present and pinned.
- Preregister the scientific hypothesis, controls, folds, leakage canaries, unique-raster gates, and 3-experiment budget before fitting.
- Run the prescribed fold-local holdout; compare to the current same-evaluator best with paired uncertainty. Do not convert HOLDOUT-DTI into a leaderboard estimate without a validated calibration model.
- Write through the shared submission writer; reopen the exact bytes and automatically validate single-band float32, [0,1], footprint/null handling, CRS, dimensions, transform, and SHA-256 against the competition template.
- Check correlation/overlap on the surface before placement and on final dots against the complete registry; halt on any threshold breach.
- Publish a JSON run card and a clear front-page decision: `DO NOT SUBMIT` unless every gate passes and the separate selector authorizes the exact named/hash-pinned file. A TIF that merely exists is not an eligible TIF.
- Provide an executive submission guide with the exact filename, download link, unique portal name, <=140-character note, validation receipt, and no ambiguity about whether upload is approved.

## Data and Access Limitations

The official competition data download requires an authenticated competition account; no authenticated data, feature-cache, sample template, or training labels are present in this checkout. See the official [competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/). The official problem description lists USGS/INGENIOUS source data and feature families; external data usage must comply with competition licensing/rules. Do not treat third-party site reports as verified training data or submission receipts.

## Data Placement Blocker

**Single remaining blocker to training a fitted lane:** On any unrestricted machine run:
```bash
bash scripts/download_competition_data.sh   # requires DrivenData login
python scripts/prepare_data.py
```
Then the cached feature stack, `evaluate_holdout.py` and `submission_writer.py` pipeline is ready (GPU for training, CPU for metric/validation verified here). The holdout described below is hide-and-recover: withhold whole fault components with a 15-px (1500 m) buffer, derive every catalogue-based feature only from visible faults, mask visible faults pixel-exactly, score pooled DTI (α 0.2, β 0.8, 300 m triangular kernel).

## Parallel-Run Protocol (this branch's lane)

1. **Lane** — Hybrid blind-piedmont dispersed: S3DEP 10 m monoclinal step (3 scales) + MT conductivity/depth-to-basement straight-boundary coherence + drainage valley collinearity vote, OR-fused, catalogue-flank B=2 prune (0 within 2 px), Poisson 2.83 px CELF emission, NE/SE Walker-LidarGap weighting (37,654 dots). If rank-correlation >0.90 or >70% dots within 3 px of any registry raster, log duplicate and stop.
2. **Reuse, don't rebuild** — use template cached stack, `evaluate_holdout.py`, `submission_writer.py`.
3. **Label every number** HOLDOUT-DTI (evaluator version, withheld positives, 95% CI) or ORGANIZER-CONFIRMED (receipt). Projection ≠ score.
4. **Leakage canary** — test each feature alone; AUC >0.90 = leakage until proven otherwise.
5. **Run card** — JSON at `docs/downloads/*-audit.json`.
6. **Budget** — stop after 3 experiments or 2 h. Promotion is separate selector step, within weekly cap.

## Limitations & Next Work

- Holdout measured on this checkout is a catalogue-gap proxy (60,988 withheld positives, segment-pooled v1, 15-px buffer, tile-bootstrap CI) — not a live leaderboard predictor. Live-anchor projections are calibrated on the H33 B=2 flank model and carry RMSE ~0.09 across families. For our synthetic, HOLDOUT is 0.0 NEGATIVE vs 0.0067 champion.
- No organizer receipt binds any 0.2778-class score to a raster hash in this repo; all historic scores are OWNER-REPORTED/UNVERIFIED.
- Unique TIF here is synthetically weighted (quadrant-biased Poisson) — no real geophysical feature stack was fitted; a fitted model using the 10 m 3DEP + MT + drainage surfaces is the next experiment to attempt a HOLDOUT win vs KPL-36 EXP-3 (0.1701).
- Need `.cache/gems_data/training_features.tif` (418 MB) and `labels.tif` placed via `scripts/prepare_data.py` before a true 3-experiment lane can be validated without leakage.

Sources: [Competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)\n- [Official problem description, data families, metric, and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)\n- [Official competition data download (login may be required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)\n- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)\n- [Organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)\n- [USGS GeoDAWN data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)\n- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)\n- [EPSG:32611](https://epsg.io/32611)\n\n## Official Review Links

- [Competition overview and rules entry point](https://www.drivendata.org/competitions/306/competition-doe-gems/)\n- [Official problem description, data families, metric, and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)\n- [Official competition data download (login may be required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)\n- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)\n- [Organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)\n- [USGS GeoDAWN data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)\n- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)\n- [EPSG:32611](https://epsg.io/32611)\n\n---

**Current status (this branch):** One synthetic unique research raster exists and is documented at [Live Site](docs/index.html) and [Executive Summary](docs/executive-summary.html) — DOWNLOAD YES, SUBMIT SELECTOR-REQUIRED (holdout-negative). No fitted lane has been run; no weekly slot spent. Status changes only with a holdout-beating, canary-passing, registry-unique fitted model.

## This Review Session's Additional Artifacts

The detailed [nine-site executive review](docs/executive-summary.html), [ranked hypothesis shortlist](docs/hypotheses.md), [source register](docs/sources.md), and [repository review and evidence ledger](docs/review-2026-10-27.md) supplement the audit. A machine-readable blocked/negative run card is at [`evidence/current_run_card.json`](evidence/current_run_card.json). The live site's unique TIF is separately audited at [`docs/downloads/*-audit.json`](docs/downloads/gemsdoesass1-hybrid-blindpiedmont-dispersed-37654-20261027T113459Z-cbceb1d0-audit.json) with its own validator receipt. Read the executive review for the current page-by-page status, conflicts, and evidence labels.
