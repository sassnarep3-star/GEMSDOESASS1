# GEMSDOESASS1 — GEMS fault-detection research

**Read first, every session:** this README, [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md), [`knowledge/PROJECT_BRIEF.md`](knowledge/PROJECT_BRIEF.md), [`AGENTS.md`](AGENTS.md), and [`knowledge/NEXT_STEPS.md`](knowledge/NEXT_STEPS.md). The full persistent transcription of the user’s project prompt and constraints is in `knowledge/PROJECT_BRIEF.md` (also linked here); repeated duplicate passages are consolidated. Core values: **Maximize P(Win)** · **Own the Outcome**.

**This session’s review (2026-10-29):** [`knowledge/hypotheses_20261029.md`](knowledge/hypotheses_20261029.md) is a ranked, untested slate only. The prior lane’s negative result and novelty stop remain in force; no experiment, submission TIFF, score estimate, or slot approval was produced.

**Do not submit any TIFF from this repository.** SWGB’s advertised uniqueness used a 17-file subset and is disproved against the calibration lattice (99.87%). H-PBSC is unique vs those 17 competitive rasters (25.3%) but fails the same lattice (99.48%) and lost the holdout bar. BGAC never packaged a file. [Home](index.html) · [executive summary](executive-summary.html) · [SWGB lattice review](evidence/swgb_lattice_review.json) · [H-PBSC run card](evidence/pbsc/run_card.json) · [next steps](knowledge/NEXT_STEPS.md).

# Part 0 — H-PBSC lane (session 2026-10-28)

**Is the new GeoTIFF OK to submit?** **NO.**

| | |
|---|---|
| **Research file (DO NOT SUBMIT)** | [`docs/downloads/gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif`](docs/downloads/gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif) |
| **sha256** | `2f3bd24e7be6edb58df011482622075a72e08beb5eab772d50c4d6aa80247fd9` |
| **Note (107/140)** | `GEMSASS1 PBSC: playa-bounding step×coh×low-relief 37654d 2.8px >600m offcat; HOLDOUT-DTI 0.065 vs bar 0.101` |
| **HOLDOUT-DTI** | **0.0650 [0.0605, 0.0693]** (`GEMSASS1-HR-v2-segment`, 60,988 withheld positives) vs bar **0.1011 [0.0956, 0.1072]** |
| **vs 17 competitive rasters** | max Spearman 0.029; max 3 px **25.3%** (under 70%) |
| **vs 13gems lattice** | **99.48%** (37,460 / 37,654) — duplicate if the lattice counts |
| **Validator** | 11/11 from bytes: float32, EPSG:32611, 3730×3292, values {0,1}, no NaN |
| **Verdict** | `negative` · `ok_to_submit = false` |

Lane: playa-bounding scarp corridor. E1 (+mag) 0.0621; E2 (no mag, shipped) 0.0650. E3 not run. Canary max AUC 0.573. GEMSDOE32 0.2778 is H19-5 dotted minus catalogue-proximal dots — copying it cannot beat it.

---

Read the [project brief](knowledge/PROJECT_BRIEF.md) at the beginning of every session. It is a deduplicated transcription of the user prompt, not a claim of a byte-exact archive. Focus on evidence, Maximize P(Win), and Own the Outcome.

# Part B — BGAC lane (`vendor/gems57` pipeline)

> **Submission status: NO SUBMISSION APPROVED.** BGAC stopped on novelty. The prior SWGB "promote" decision is superseded: a post-hoc audit against a pinned registry lattice found 99.8707% candidate-directed overlap within 3 pixels, exceeding the 70% protocol limit. Its pre-placement surface was not cleared. The artifact is retained for audit only. See [review receipt](evidence/swgb_lattice_review.json) and [reproducible audit](scripts/audit_swgb_lattice_witness.py). No weekly slot was used in this review.

**Start every session here**, then read [the persistent project brief](knowledge/PROJECT_BRIEF.md), [hypotheses](knowledge/hypotheses.md), [three-pass review](evidence/review.md) and [run card](evidence/run_card.json). The brief is a deduplicated transcription of the user's repeated prompt, not a verbatim archive. It preserves the mission, Core Values / Own the Outcome, strict protocol, sources, validation, download and release requirements.

## Executive result

| Item | Evidence / decision |
|---|---|
| BGAC-1 | **Exploratory HOLDOUT-DTI 0.0390**, 95% CI **[0.0283, 0.0501]**, 56,454 withheld positive pixels; evaluator `gems57-pooled-hide-v2`. Pass-2 review disqualified the first-pass execution: it should have stopped before placement. |
| Strongest same-run ablation | **HOLDOUT-DTI 0.0730**, 95% CI **[0.0569, 0.0892]**, same positives/evaluator |
| Paired difference | **HOLDOUT-DTI −0.0340**, 95% CI **[−0.0466, −0.0220]**, same positives/evaluator |
| New unique TIFF | **None.** Final dots have 100% directed overlap within 3 px of a registry lattice. The experiment stopped, without packaging. |
| Best historical result in supplied nine-site list | GEMSDOE32, **0.2778 — UNVERIFIED owner/user report, not ORGANIZER-CONFIRMED**. Exact mask mechanism and bytes verified; no submission-page receipt. |
| Estimated leaderboard score | **Unavailable.** Catalogue hide/recover is not a calibrated leaderboard forecast. |
| Competition slots used | None. No upload or slot selection code. |

See the [executive summary](docs/executive-summary.html), [nine-site pages](docs/index.html#historical), [scientific analysis](knowledge/scientific_analysis.md), [sources](knowledge/sources.json), [history audit](evidence/nine_site_audit.json), and [next actions](knowledge/NEXT_STEPS.md).

## What this checkout actually contains

The initial commit had only `# GEMSDOESASS1`. The prior sessions built the pipelines and sites described here. It does not inherit the training/GPU verification asserted in the chat. The CPU experiment reuses pinned shared tools from [GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32/tree/1398109a23f04a2ace71c1bd2f527cfba87860b5/vendor/gems57), including the cached-band builder, whole-component spatial folds, evaluator, and fail-closed submission writer. [Vendor provenance](vendor/PROVENANCE.json) identifies exact hashes; no shared metric was forked or changed.

The core mirrored feature stack is approximately 419 MB when restored. Raw feature stacks, caches and the Python environment are ignored by Git. The mirrored reference rasters and historical SWGB TIFF are tracked for audit; they are not organizer-authenticated. The complete frozen registry has 414 TIFF blobs in the nine public priority repos (outside `data/`). Other sites/private submissions are not covered. One prior has nonfinite footprint values and one is an incompatible format fixture; these are explicitly recorded, never silently normalized into clearance.

## Reproduce / verify

Python 3.11+, `gh`, and network access to GitHub and PyPI are sufficient for the measured CPU run. Arena already configures GitHub; never put credentials in files.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-lock.txt
.venv/bin/python scripts/prepare_data.py           # ~419 MB source + ignored band caches
.venv/bin/python scripts/registry_snapshot.py      # restore frozen 414-file registry, verify blobs
.venv/bin/python scripts/audit_history.py          # analysis only, no experiment
.venv/bin/python scripts/verify_release.py         # evidence + site checks, no data needed
.venv/bin/pytest -q
python scripts/build_site.py
python scripts/swgb_build_site.py
.venv/bin/python scripts/audit_swgb_lattice_witness.py  # pinned witness; needs gh if not cached
python -m http.server 8000 --bind 0.0.0.0 --directory docs
```

The completed experiment is immutable: `scripts/evaluate_holdout.py` refuses to overwrite its run card. To reproduce scientifically, use a separate copy of the checkout with an empty evidence output directory after archiving the frozen evidence; never remove failed evidence to conceal a trial. Its one experimental command was:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/evaluate_holdout.py
```

No GPU was needed. All catalogue-derived information is limited to split construction, visible-fault masking, and the final known-fault exclusion—not the BGAC surface. Splits hide whole original components, including cross-quadrant tails; 80 px training buffer, fixed label-blind quadrants. DTI uses the user's protocol formula, independently unit-tested against the shared brute-force implementation; the official metric page was not reachable to authenticate its current definition. The official reference notebook confirms fault detection and asymmetric Tversky **training loss**, not the 300 m evaluation formula.

## Submission gate, not a promise

`vendor/gems57/submission_writer.py` refuses nonfinite, out-of-range, misaligned or outside-footprint positive output; it validates the on-disk TIFF/ZIP and never silently clips or fills model errors. It does **not** approve a scientific result. `scripts/evaluate_holdout.py` only calls it after novelty and canary clearance. The current run never reached it.

An eventual release requires: verified input provenance/rules; leakage clearance; strict surface + dot novelty; compatible incumbent holdout improvement with a paired CI; correct single-band CRS/shape/transform/range; a separately authorized selector within the official weekly cap. Portal acceptance and ORGANIZER-CONFIRMED score require an organizer receipt. No automatic submission is implemented.

## Site and refresh feed

GitHub Pages uses the existing legacy `main` / root configuration, with root links into `docs/`. There is a landing page, executive-summary/how-to page, research/source page, and one executive page per focus site. These are local comparative pages; the nine upstream websites have not been edited. The evidence page automatically checks current public GitHub heads in the browser with a one-hour cache and explicit timeout/rate-limit failures; a scheduled workflow also preserves advisory snapshots as Actions artifacts. Neither changes scores, experiments, novelty clearance or promotion. The experimental snapshot remains pinned. The GitHub connection returned HTTP 403 when asked to switch Pages to Actions deployment; the existing legacy deployment is retained, not misreported as reconfigured.

## Limitations that matter

- No verified DrivenData submission receipt, current leaderboard, weekly cap, rules PDF or current official data hashes. The provided high-score claims conflict. We cannot truthfully promise a higher leaderboard score.
- Outbound access is limited to GitHub/npm/PyPI hosts; USGS, GDR, NLR, DrivenData and Dropbox are outside that allowlist. Official GitHub reference code was inspected; owner mirrors are explicitly weaker evidence.
- The literal 70%/3 px rule is obstructed by a lattice covering 99.87% of the footprint within 3 px. No density exemption was applied. A policy decision outside this stopped run is needed before another method can realistically clear that registry.
- No new competition TIFF was produced because the required gates failed. This is a verified negative deliverable, not a completed high-scoring submission.

## Concurrent main integration

Another parallel session merged a separately negative synthetic research artifact into `main` while this branch ran. It is preserved, not deleted or treated as this lane's output: [parallel-main research archive](archive/parallel-main-f620a70/README.md). All 14 files are byte-hashed; old HTML is inert `.txt`, and TIFFs/ZIP remain learning-only in the archive, outside active downloads. Its limited uniqueness comparison and unvalidated projection are not adopted. The current BGAC-1 decision remains **negative / no approved TIFF**.

A second concurrent audit (PR #4, main `2f67fac`) is also [fully preserved](archive/parallel-main-2f67fac/README.md), including its independent negative lattice-witness read-back, tooling and tests. Its [broader user-provided historical ledger](knowledge/user-provided-submission-ledger.md) is retained additively; unreceipted reports remain unverified. Only the current pipeline/site is active, and pytest scopes execution to tests/, not archived source snapshots.
