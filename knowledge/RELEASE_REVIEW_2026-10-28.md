# Release review — 2026-10-28

**Decision: DO NOT SUBMIT either prior candidate.** No new experiment or slot was used. The prior SWGB promotion was based on a partial 17-raster registry, and is revoked. It is not an organizer-confirmed score or a new selector decision.

## Measured contradiction

The archived SWGB TIFF SHA256 is `f98c20df5bc67a482de6debd4abef9d3d104498bda0aacf464d693e271287729`. Its prior receipt reports all format checks passing relative to a mirrored template; this session independently read the candidate as finite with range [0,1] and confirmed its grid matches the lattice, **not an independently authenticated organizer template**. This is not sufficient for competition clearance.

The previously omitted [GEMSDOE24 calibration lattice, pinned revision](https://github.com/buffedlizard55-lab/GEMSDOE24/blob/cf093c8c5e9fa77294ecf4c59b79cdade92cbc06/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif) has SHA256 `b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2`. **REGISTRY-MEASUREMENT:** 44,033 of 44,090 candidate positive pixels (99.8707%) are within three pixels of lattice support. This exceeds the literal 70% threshold. The shared template's `dot_overlap` agrees with an independent Euclidean distance calculation. This is a directed-overlap failure, not proof of byte identity, geological similarity, or a complete comparison against all other sites. The lattice is a calibration raster rather than a confirmed submission; its inclusion follows this repository's existing all-TIFF registry and literal rule, without silently applying a density exception. Changing that policy requires a separate explicit decision, not a workaround in this run.

**Reproduce** with GitHub access and `requirements-lock.txt` installed:

```bash
mkdir -p data/review
gh api 'repos/buffedlizard55-lab/GEMSDOE24/contents/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif?ref=cf093c8c5e9fa77294ecf4c59b79cdade92cbc06' -H 'Accept: application/vnd.github.raw+json' > data/review/lattice.tif
python scripts/audit_swgb_lattice.py
```

The script verifies both hashes, finite candidate values, range, single-band grids and positive support before comparison. Results: [machine-readable audit](../evidence/swgb_lattice_audit.json). It does not train, place dots, modify the candidate, or contact the competition.

## Scientific status and unresolved issues

- BGAC's prior run stopped after its own surface overlap failure; its holdout is exploratory only. See [run card](../evidence/run_card.json) and [corrected surface audit](../evidence/corrected_surface_novelty.json).
- SWGB's recorded holdout is not an organizer score and its earlier audit used a different evaluator and incomplete registry. Its earlier experiments exceeded the specified budget, and no pre-placement comparison against the full registry was recorded. The old `promote` in the immutable historical run card is superseded, not erased.
- The H33 B2 mask was measured as the site-31 base with near-catalogue dots removed. Emission efficiency is a plausible mechanism, not a verified causal account of the reported score. See [analysis](scientific_analysis.md) and [original implementation](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/1398109a23f04a2ace71c1bd2f527cfba87860b5/src/gems32/hypotheses33.py#L313-L331). No submission receipt confirms the supplied 0.2778 report and no calibrated leaderboard forecast is available.
- This sandbox can reach GitHub and package hosts, not the official DrivenData, USGS, NLR, or Dropbox sites. Organizer inputs, current rules, weekly cap and leaderboard cannot be independently verified here. The supplied leaderboard highs conflict. Data mirrors are not organizer authentication.
- No modifications were made to the nine independently owned sites. Local [nine-site summary](../docs/executive-summary.html) and [per-site summaries](../docs/index.html#historical) remain evidence reviews, not new submissions.
- The legacy SWGB builder fails before side effects; the site generator now deterministically produces withdrawal-only pages. Their previous output pages and README are preserved in `archive/2026-10-28-release-review/` as superseded text. The original raster remains available in Git history/checkout strictly for audit, not for submission.

Next steps: obtain official source files and receipts in an authorized environment; resolve the literal lattice obstruction outside this stopped run; establish a comparable holdout incumbent; then preregister a distinct hypothesis and enforce both surface and dot gates over the agreed complete registry. No weekly slot should be used before all gates and a separate selector decision.
