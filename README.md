# GEMSDOESASS1 — DOE GEMS research and submission audit

> **Start every session here.** Read this charter and the linked current review before inspecting, changing, or claiming results for this project. Work toward the user's goal—reliable, scientifically defensible fault predictions for the DOE GEMS competition—while prioritizing **Maximize P(Win)** and **Own the Outcome**. A negative result is a deliverable; an unsupported score or unsafe upload is not.

## Executive decision (2026-10-27)

**There is no competition-ready GeoTIFF in this checkout. Do not download or submit any file from this repository.** This checkout contains only this README at the reviewed commit: no source code, feature cache, training data, sample-submission raster, holdout evaluator, submission writer, registry rasters, generated TIFFs, validation receipts, or website. Consequently this repository cannot calculate a HOLDOUT-DTI, estimate a leaderboard score, test uniqueness, or create a valid competition file. No experiment was run and no submission slot was used.

The historical **0.2778** entry attributed to GEMSDOE32 is the highest of the nine user-listed site results, but it is a **user/owner-reported historical score, not organizer-confirmed here**. It is a benchmark for analysis, not an artifact to copy or re-submit. No numerical leaderboard projection is defensible from this checkout. The user-provided values **0.3195** and **0.4413** are inconsistent as “current highest”; neither has a dated leaderboard capture or submission receipt in this repository. Do not call either verified or current without checking the live official leaderboard.

**Immediate stop/blocker:** the parallel-run lane's specific assigned method paragraph is not present in this checkout or request. The required shared template/tools/data are also absent. Do not invent a method lane, rebuild the evaluator/writer privately, or create a synthetic/placeholder TIFF. See [the repository review and evidence ledger](docs/review-2026-10-27.md).

## Project purpose

Develop and evaluate methods for identifying geological faults that may indicate geothermal resources in the GeoDAWN region, using official competition data and permitted, auditable external data. The competition targets faults and explicitly recognizes that the public fault catalogue is incomplete and may contain inaccuracies; it is not a direct geothermal-vent detector. A promising pattern is a scientific hypothesis, not proof of a fault or geothermal resource.

The competition's published submission contract is one float32 GeoTIFF layer, EPSG:32611, 100 m resolution, same bounds/grid as training data, confidence values in [0, 1], and null/NaN outside the bounds. The published distance-weighted Tversky metric uses alpha=0.2, beta=0.8 and a 300 m triangular support. Always re-check the official rules and exact sample-submission grid before release. Source: [official problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).

## Mandatory operating protocol

1. **Stay in the assigned lane.** Use only the specific method paragraph assigned for this parallel run. Compare the pre-placement surface and final dots with every available registry raster. If absolute rank correlation exceeds 0.90, or more than 70% of dots fall within 3 pixels of one registry raster's dots, log a duplicate and stop. Do not evade this gate by moving dots or altering the comparison.
2. **Reuse shared tooling; do not fork it.** Use the template's cached features, `evaluate_holdout.py`, and `submission_writer.py`. Hold out whole fault segments with a buffer; derive catalogue-based features from visible faults only; mask visible fault pixels exactly; pool DTI with alpha=0.2, beta=0.8 and a 300 m triangular kernel. If a shared tool is wrong, fix it in the shared template and report the correction. Do not silently substitute a private evaluator/writer.
3. **Label every score-like number.** A validation score must be labeled `HOLDOUT-DTI` with evaluator version, withheld-positive count, and 95% CI. A live competition result is `ORGANIZER-CONFIRMED` only when copied from a submission-page receipt. Label unreceipted site/owner/user claims as such. A projection is never a score; omit projections unless their calibration is documented and explicitly label them as projections.
4. **Run leakage canaries.** Evaluate every candidate feature alone using the holdout protocol before trusting it. AUC >0.90 is a leakage alarm until demonstrated otherwise.
5. **Publish a machine-readable run card.** Include hypothesis, mechanism, named non-fault mimic, HOLDOUT-DTI and CI (or null with a reason), registry correlation/overlap, raster SHA-256 (or null if not written), format-validator output, submission identifier/note (note <=140 characters), and verdict `promote` or `negative`. Promotion to a real slot is separate from model evaluation.
6. **Respect the experiment budget.** Stop after 3 experiments or 2 hours, whichever comes first. Do not select/spend a weekly submission slot here; the separate selector must check the current submission-page cap and approve the exact artifact.
7. **Fail closed; no human-inspector fallback.** All format, holdout, leakage, novelty, and selector checks must run automatically. A format pass alone is not a scientific pass or submission authorization. No candidate can be called unique without the registry comparison evidence.

## Nine-site historical benchmark (reported, not confirmed)

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

## Before any future release

- Read this file and the [latest review/evidence ledger](docs/review-2026-10-27.md).
- Confirm the assigned lane, shared-template revision, data/cache manifest, and full registry manifest are present and pinned.
- Preregister the scientific hypothesis, controls, folds, leakage canaries, unique-raster gates, and 3-experiment budget before fitting.
- Run the prescribed fold-local holdout; compare to the current same-evaluator best with paired uncertainty. Do not convert HOLDOUT-DTI into a leaderboard estimate without a validated calibration model.
- Write through the shared submission writer; reopen the exact bytes and automatically validate single-band float32, [0,1], footprint/null handling, CRS, dimensions, transform, and SHA-256 against the competition template.
- Check correlation/overlap on the surface before placement and on final dots against the complete registry; halt on any threshold breach.
- Publish a JSON run card and a clear front-page decision: `DO NOT SUBMIT` unless every gate passes and the separate selector authorizes the exact named/hash-pinned file. A TIF that merely exists is not an eligible TIF.
- Provide an executive submission guide with the exact filename, download link, unique portal name, <=140-character note, validation receipt, and no ambiguity about whether upload is approved.

## Data and access limitations

The official competition data download requires an authenticated competition account; no authenticated data, feature-cache, sample template, or training labels are present in this checkout. See the official [competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/). The official problem description lists USGS/INGENIOUS source data and feature families; external data usage must comply with competition licensing/rules. Do not treat third-party site reports as verified training data or submission receipts.

## Official review links

- [Competition overview and rules entry point](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem description, data families, metric, and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official competition data download (login may be required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [EPSG:32611](https://epsg.io/32611)

---

**Current status:** documentation-only repository review. No model, experiment, score estimate, TIF, website, or submission was produced. This status changes only with reproducible, pinned evidence.

## This review session's additional artifacts

The detailed [nine-site executive review](docs/executive-summary.md), [ranked hypothesis shortlist](docs/hypotheses.md), and [source register](docs/sources.md) supplement the [repository review and evidence ledger](docs/review-2026-10-27.md). A machine-readable blocked/negative run card is at [`evidence/current_run_card.json`](evidence/current_run_card.json). Read the executive review for the current page-by-page status, conflicts, and evidence labels. No TIFF was created or approved.
