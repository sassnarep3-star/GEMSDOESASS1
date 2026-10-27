> **Historical snapshot:** Some availability and status statements in this earlier report are superseded. See the current [executive summary](executive-summary.html) and [independent recheck](data/claimed_candidates_audit.json). The parallel synthetic TIFF is research-only and **must not be submitted**.

# Executive summary — nine focus sites and submission decision

**Review date:** 2026-10-27 UTC. **Decision from this repository:** no submission is approved; no GeoTIFF was generated. The checkout contains only a 14-byte README at baseline. It has no code, data, cached features, holdout evaluator, submission writer, registry, or tests. The official competition data page redirected this review to the DrivenData login page. The protocol's required single assigned-method paragraph was not present. A placeholder TIFF would not satisfy the scientific or technical requirements, and copying an existing site's TIFF would violate the uniqueness requirement.

## Direct answer

The GEMSDOE32 H33-H33-2-B2 historical file is the top reported score among the nine named focus sites: **OWNER-REPORTED / USER-SUPPLIED historical score: 0.2778**. The target page currently describes it as already submitted and explicitly says there is no submission-page receipt in that repository tying the score to its raster hash. It therefore is not an organizer-confirmed result under the run protocol, and must not be resubmitted. The score does not establish what geological mechanism caused success. We cannot assert that a new method will beat it or estimate an expected leaderboard score from the evidence in this checkout.

The competition defines the target as faults not present in the current public USGS fault database and uses a distance-weighted Tversky metric with a 300 m triangular kernel, alpha 0.2 and beta 0.8; the official problem description explains why accurate off-catalogue discoveries matter. The method’s plausible success mechanism must be established from its actual implementation and organizer feedback—not inferred from the score alone. The site reports a 37,654-dot raster and shortened SHA-256 beginning `c55bafc470054e82`, but this review did not download/recompute that raster or audit its code. (The site page is evidence of what its owner reports, not organizer verification.)

The supplied prompt also contains conflicting **USER-SUPPLIED / OWNER-REPORTED leaderboard claims: 0.3195 and 0.4413** and names a leaderboard high of 0.3195. During this review, the official live leaderboard rendered **LIVE PUBLIC LEADERBOARD OBSERVATION (not HOLDOUT-DTI and not a submission-page receipt): 0.4544** in its top row. It is recorded only as a dated live-page observation and not used as a target or projection. Rankings change, so consult the live official page. The contradiction is flagged, not silently reconciled.

## Nine-site decision table

Every number in this table is explicitly an **OWNER-REPORTED / USER-SUPPLIED historical competition-score claim**, not HOLDOUT-DTI, not an organizer-confirmed receipt, and not an estimate. The filename, value, and site URL below came from the request; the public site pages are linked for cross-check. Independent file/hash/score verification was not possible here. The GEMSDOE28 site reports that these nine historical leader rasters have at least 86.72% directional 3-pixel dot overlap pairwise in its audit; this is an owner-reported registry comparison, not a calculation by this checkout. On that published result and the protocol's 70% cutoff, none of the historical files should be treated as an eligible unique candidate pending independent reproduction.

| Site | Historical best entry in the supplied list | Score evidence | Independent uniqueness result here | Download / submission decision |
|---|---|---|---|---|
| [GEMSDOE24](https://buffedlizard55-lab.github.io/GEMSDOE24/) | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | OWNER-REPORTED / USER-SUPPLIED: 0.2477; no holdout metadata or receipt | NOT TESTED in this checkout; owner audit says historic cohort is above the overlap limit | Do not copy or resubmit; no TIFF validated here |
| [GEMSDOE25](https://buffedlizard55-lab.github.io/GEMSDOE25/) | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | OWNER-REPORTED / USER-SUPPLIED: 0.2600; no holdout metadata or receipt | NOT TESTED here; owner audit says historic cohort is above the overlap limit | Do not copy or resubmit; no TIFF validated here |
| [GEMSDOE27](https://buffedlizard55-lab.github.io/GEMSDOE27/) | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | OWNER-REPORTED / USER-SUPPLIED: 0.2449; no holdout metadata or receipt | NOT TESTED here; owner audit says historic cohort is above the overlap limit | Do not copy or resubmit; no TIFF validated here |
| [GEMSDOE28](https://buffedlizard55-lab.github.io/GEMSDOE28/) | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | OWNER-REPORTED / USER-SUPPLIED: 0.2710; no holdout metadata or receipt | NOT TESTED here; owner audit reports 86.72%+ for all pairwise historical comparisons | Do not copy or resubmit; no TIFF validated here |
| [GEMSDOE30](https://buffedlizard55-lab.github.io/GEMSDOE30/) | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | OWNER-REPORTED / USER-SUPPLIED: 0.2600; no holdout metadata or receipt | NOT TESTED here; owner audit says historic cohort is above the overlap limit | Do not copy or resubmit; no TIFF validated here |
| [GEMSDOE31](https://buffedlizard55-lab.github.io/GEMSDOE31/docs/) | `h27-4-solo-d28-20261004-8acb75e1-nan` | OWNER-REPORTED / USER-SUPPLIED: 0.2708; no holdout metadata or receipt | NOT TESTED here; owner audit says historic cohort is above the overlap limit | Do not copy or resubmit; no TIFF validated here |
| [GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | OWNER-REPORTED / USER-SUPPLIED: 0.2778; target page reports already submitted; no score-to-hash receipt | NOT TESTED here; owner audit says historic cohort is above the overlap limit | Highest reported focus-site history, but already used; do not resubmit |
| [GEMSDOE33](https://buffedlizard55-lab.github.io/GEMSDOE33/) | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | OWNER-REPORTED / USER-SUPPLIED: 0.2632; no holdout metadata or receipt | NOT TESTED here; owner audit says historic cohort is above the overlap limit | Do not copy or resubmit; no TIFF validated here |
| [GEMSDOE36](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/) | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | OWNER-REPORTED / USER-SUPPLIED: 0.2750; no holdout metadata or receipt | NOT TESTED here; owner audit says historic cohort is above the overlap limit | Do not copy or resubmit; no TIFF validated here |

**No leaderboard estimate:** `NOT ESTIMATED`. There is no defensible mapping from the proposed holdout metric to a private/public organizer score in this checkout. A public site that offers a projection is not enough without out-of-family calibration and uncertainty. The run protocol explicitly prohibits writing projections as scores.

## What explains the reported 0.2778?

The only verified statements available here are the official problem definition/metric and what the project page says about its own artifact. The owner's page calls this the champion-family H33-H33-2-B2 raster and reports the historical value; it also discusses dotted/limited-budget predictions and duplicate overlap across a lineage. Those facts make the following explanations plausible, but **not proven for the 0.2778 submission**:

- The metric is distance tolerant, so a high-confidence line near an expert-labelled fault can receive useful credit even when pixels do not coincide exactly.
- The metric weights missed positives more heavily than false positives (beta 0.8 versus alpha 0.2), so recall-oriented, spatially distributed coverage can be advantageous, subject to the denominator and prediction budget.
- A coherent family of fault-like structures may generalize better than noisy isolated detections; however, the similarity of related files is not independent evidence of geological accuracy.
- Selection among many experimental variants may cause winner's curse. A historical best from a large search can overstate expected out-of-sample performance.
- Incomplete ground truth makes ordinary random pixel holdouts optimistic. Whole-fault-segment withholding, buffers, fold-local catalogue features, and pixel-exact masking are needed to avoid spatial leakage.

To state *why this particular raster* earned its displayed value, obtain and archive the exact source, feature/configuration hashes, official receipt, and a faithful organizer-metric reproduction. This repo has none of those artifacts. Do not infer causation from ranking.

## Current external-site status and irregularities

This is a read-only review of the pages as they rendered on 2026-10-27 UTC. These owner pages are mutable and not immutable release receipts.

- GEMSDOE24 page: recent candidates are marked research-only/DO NOT SUBMIT; the page says it did zero new geological experiments because the assigned method paragraph was missing.
- GEMSDOE25 page: latest H74 artifact is marked testing-only/DO NOT SUBMIT; its page also reports unavailable caches for another planned diagnostic.
- GEMSDOE27 page: H31-1 is described as evidence-pass but selector-required; page explicitly says evidence pass is not slot approval.
- GEMSDOE28 page: content contains a historical S22C promotion-style banner but also a more current “NOT READY TO SUBMIT” read-only audit. Use the later fail-closed status; flag this internal inconsistency for review.
- GEMSDOE30 page: CSR-1 is explicitly “OK to download: YES / OK to submit: NO”; its own pooled holdout comparison trails the listed incumbent. Do not infer an entry approval from novelty or format pass.
- GEMSDOE31 page: current release audit says literal-registry STOP and no current artifact is approved; historical lane permissions are withdrawn.
- GEMSDOE32 page: no new file authorized; current H47 artifact is marked DO NOT SUBMIT due to missing paired-bootstrap evidence and a literal lattice-overlap failure. The 0.2778 historical submission is reported as already submitted.
- GEMSDOE33 page: latest FSML2-CC is marked negative/DO NOT SUBMIT after failing its holdout gate. Its page says the corresponding public-score estimate is not estimable.
- GEMSDOE36 page: the page begins with a “promote” KPL-36 banner and a download/submit instruction, but later presents a registry pigeonhole argument and calls current artifacts research-only/DO NOT SUBMIT. This is a material internal conflict; fail closed and do not upload based on the banner alone.

These are findings about page text, not independent reproduction of their computations. They do not authorize a file from this repository.

## Highest-value next steps

1. Provide the assigned single method paragraph, since the protocol explicitly forbids crossing lanes or inventing one.
2. Supply the licensed competition data locally (including the exact sample submission grid); data page access currently redirects to login. Do not place credentials in this repository.
3. Pin and archive the full registry manifest and artifacts used by all nine sites, including pre-placement surfaces, to enable both novelty stages and independent reproduction.
4. Reuse a common evaluator and writer from the upstream reference solution/template; this checkout presently has no implementation. Pin versions/hashes and add tests before any experiment.
5. Select exactly one preregistered candidate from [the ranked hypothesis page](hypotheses.md); start with read-only preflight, then run feature canaries and at most the protocol budget. Do not submit if any required evidence is missing.
6. Add a CI-tested submission validator and automatic summary site only after the data/tools exist. Every download link must show the file hash, evidence class, machine validation receipt, and a prominent `OK TO SUBMIT` or `DO NOT SUBMIT` state.

**Run card:** see [`evidence/current_run_card.json`](../evidence/current_run_card.json). It records a negative/blocked review with no experiment, no score, no file, and no submission authorization.
