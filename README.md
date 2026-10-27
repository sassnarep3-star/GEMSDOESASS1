# GEMS · evidence before submission

> **Submission status: BLOCKED — no new TIFF is cleared for download or submission.**
> The single preregistered BGAC-1 experiment failed both the improvement and literal dot-overlap gates. The protocol requires stopping on a duplicate; creating a disguised replacement TIFF would violate the request.

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

The initial commit had only `# GEMSDOESASS1`. This change builds the first pipeline/site here. It does not inherit the training/GPU verification asserted in the chat. The CPU experiment reuses pinned shared tools from [GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32/tree/1398109a23f04a2ace71c1bd2f527cfba87860b5/vendor/gems57), including the cached-band builder, whole-component spatial folds, evaluator, and fail-closed submission writer. [Vendor provenance](vendor/PROVENANCE.json) identifies exact hashes; no shared metric was forked or changed.

The restored feature stack is approximately 419 MB. Raw data, caches, historical TIFFs and the Python environment are ignored by Git; only receipts, code and the static site are tracked. The complete frozen registry has 414 TIFF blobs in the nine public priority repos (outside `data/`). Other sites/private submissions are not covered. One prior has nonfinite footprint values and one is an incompatible format fixture; these are explicitly recorded, never silently normalized into clearance.

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
