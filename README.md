# GEMSDOESASS1 — GEMS Prize research and submission readiness

> **Canonical project charter — read before every change.** This README normalizes the long, repeated session request into durable operating requirements; it does not discard its scientific, submission, review, or safety goals. **Maximize P(Win)** means choosing evidence-led actions that improve the chance of a strong, scientifically defensible entry—not maximizing the number of experiments or uploads. **Own the Outcome:** carry claims through implementation, validation, disclosure of failures, and follow-up; do not shift unresolved defects to a human inspector. The objective is to find previously unmapped geological faults relevant to geothermal systems, validate hypotheses using leakage-safe spatial holdouts, and only then produce a downloadable competition-format GeoTIFF. A new filename or different bytes do **not** make a scientifically duplicated raster unique.
>
> **Parallel-run rules:** work only in an explicitly assigned method lane; compare the pre-placement score surface and final detections with the complete raster registry; stop if absolute rank correlation exceeds 0.90 or more than 70% of detections fall within 3 pixels of a registry raster. Use shared cached features/evaluator/writer, not private forks. Hold out whole fault segments plus buffer; derive catalogue features from visible faults only; mask visible labels pixel-exactly; use pooled distance-weighted Tversky (alpha 0.2, beta 0.8, triangular 300 m kernel); report evaluator version, withheld-positive count and 95% CI. Run each feature alone as a leakage canary; AUC > 0.90 is presumed leakage until explained. Preserve a JSON run card. Stop at 3 experiments or 2 hours. A leaderboard slot is a separate selector decision, not an experiment.
>
> **Evidence labels:** every performance number must be explicitly identified as `HOLDOUT-DTI` (evaluator version, withheld positives, 95% CI) or `ORGANIZER-CONFIRMED` copied from a submission-page receipt. A projection is never a score. Historical site-reported scores below are retained only as `OWNER-REPORTED / USER-SUPPLIED` context, not validated score evidence. Do not claim a score estimate when calibration is absent.
>
> **Submission safety:** a TIFF is not approved merely because it downloads or passes a format check. The fail-closed selector must validate single-band float32, CRS, dimensions, transform, footprint nodata, and all values in [0,1], then independently pass efficacy, leakage, uniqueness, and slot checks. No human-inspector fallback. Do not upload, select, or spend a weekly slot without explicit automated approval and current quota evidence.
>
> **Working rule for this checkout:** this repository currently contains no training data, feature cache, registry, evaluator, writer, experiment code, or TIFF. The competition data endpoint redirects to DrivenData login. The assigned single-method paragraph referred to by the parallel protocol is not present in the request. Therefore no candidate can be run safely here; do not copy another site's raster or manufacture a placeholder TIFF. Record negative/blocked outcomes honestly and continue only when the required authorized artifacts and lane are available.

## Current decision (reviewed 2026-10-27 UTC)

**NO submission TIFF was created. No file is OK to download or submit from this checkout.** There is nothing to validate against the official sample grid. This is the scientifically correct fail-closed outcome, not a missed TIFF generation: the checkout is an empty README-only repository, the competition-data page redirects to login, and the mandatory assigned method lane and shared tools are absent. See the [nine-site executive review](docs/executive-summary.md), [ranked hypotheses and blocked test plan](docs/hypotheses.md), [source register](docs/sources.md), and [negative run card](evidence/current_run_card.json).

### Focus-site history (not a recommendation to resubmit)

The following scores and names were supplied in the request and appear in public project-page reports. They are **OWNER-REPORTED / USER-SUPPLIED historical values**, not independently recomputed holdout results and not organizer-confirmed receipts. Historical exact files are not cleared for upload. The published GEMSDOE28 cross-site audit reports that the nine historical leaders are highly overlapping (all 72 directional pairwise comparisons exceeded 86.72% within-3-pixel overlap); treat that as a stop signal pending a byte-level independent re-audit, not as our own measurement.

| Site | Highest historical submission in the supplied record | Historical value | Project page | Download/submit decision here |
|---|---|---:|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | OWNER-REPORTED / USER-SUPPLIED: 0.2477 | [GEMSDOE24](https://buffedlizard55-lab.github.io/GEMSDOE24/) | Do not copy/resubmit; no file validated in this checkout |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | OWNER-REPORTED / USER-SUPPLIED: 0.2600 | [GEMSDOE25](https://buffedlizard55-lab.github.io/GEMSDOE25/) | Do not copy/resubmit; no file validated in this checkout |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | OWNER-REPORTED / USER-SUPPLIED: 0.2449 | [GEMSDOE27](https://buffedlizard55-lab.github.io/GEMSDOE27/) | Do not copy/resubmit; no file validated in this checkout |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | OWNER-REPORTED / USER-SUPPLIED: 0.2710 | [GEMSDOE28](https://buffedlizard55-lab.github.io/GEMSDOE28/) | Do not copy/resubmit; no file validated in this checkout |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | OWNER-REPORTED / USER-SUPPLIED: 0.2600 | [GEMSDOE30](https://buffedlizard55-lab.github.io/GEMSDOE30/) | Do not copy/resubmit; no file validated in this checkout |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | OWNER-REPORTED / USER-SUPPLIED: 0.2708 | [GEMSDOE31](https://buffedlizard55-lab.github.io/GEMSDOE31/docs/) | Do not copy/resubmit; no file validated in this checkout |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | OWNER-REPORTED / USER-SUPPLIED: 0.2778 | [GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) | Best reported historical focus-site value; already submitted per its page; do not resubmit |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | OWNER-REPORTED / USER-SUPPLIED: 0.2632 | [GEMSDOE33](https://buffedlizard55-lab.github.io/GEMSDOE33/) | Do not copy/resubmit; no file validated in this checkout |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | OWNER-REPORTED / USER-SUPPLIED: 0.2750 | [GEMSDOE36](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/) | Do not copy/resubmit; no file validated in this checkout |

**Historical benchmark interpretation:** the 0.2778 GEMSDOE32 value is a user/owner-reported public submission result, and its own page says no submission-page receipt binds the value to the raster hash. It is not a HOLDOUT-DTI value. The observed score alone does not establish why that raster scored well; attribution requires its exact code, input hash, and organizer feedback. Plausible general factors include spatially useful fault-probability ranking, a suitable density/threshold tradeoff under the distance-weighted metric, and broad coverage of newly mapped faults—but these are hypotheses, not verified explanations. The current official public leaderboard is live and can differ from the historical values in the prompt; do not treat any historical number as current.

## Submission workflow target

1. Start from authorized competition data, including the exact sample-submission grid and label/feature rasters.
2. Pre-register one geological mechanism and one named non-fault mimic; state expected failure modes before fitting.
3. Run the frozen segment-and-buffer holdout and feature-alone leakage canaries using shared tools.
4. Inspect candidate surfaces against a complete, versioned registry **before** point selection; stop on a lane collision. Then repeat the literal uniqueness checks on the final raster.
5. Compare paired fold/block-bootstrap HOLDOUT-DTI against the same-evaluator incumbent; promote only with a positive paired 95% CI and predeclared gates.
6. Write using the shared submission writer. Re-open the exact output bytes and validate values, footprint, CRS, shape, transform, datatype and band count. Preserve SHA-256 and validator receipt.
7. The selector—not this review—checks the live weekly allowance and authorizes a slot. Only then is the download marked **OK TO SUBMIT**.

## Official and project references

See the [auditable source register](docs/sources.md). Key official references:

- [DrivenData problem description, data layers, metric and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (review on 2026-10-27 UTC redirected to login)
- [Live official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DrivenData GEMS reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [Submission guidance PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

## Limitations and next steps

- Competition training data and exact `sample_submission.tif` are needed; the data page requires authentication. Public USGS GeoDAWN data are useful, but cannot be assumed to recreate the competition's exact aligned stack.
- The single assigned method paragraph and complete registry are absent. Until supplied, the parallel-run protocol forbids selecting an experimental lane or claiming novelty.
- The repo has no implementation or test suite. The reference solution is a separate upstream repository, not code present here.
- Public leaderboard scores cannot be inferred from internal holdout scores without validated calibration; no score projection is made.
- Public site narratives are owner-published, can be updated or internally contradictory, and are not organizer receipts. Validate the immutable artifact and evidence before relying on them.
- No GitHub Pages configuration, deployment workflow, or working site exists in this checkout yet.

**Next authorized step:** stage the competition files through the official account into ignored `data/`, pin a complete registry snapshot, add the assigned lane paragraph, and import/reuse the upstream evaluator/writer through a shared auditable integration. First run preflight only. No weekly slot should be spent until the evidence gates pass.
