# Repository review — 2026-10-29

## Scope and decision

This was a code/site/evidence review of the clean Arena branch at `d9f42ccea69c58cd8052b9b1fa0802771b1e7fb5`, the same commit as `origin/main` at review time. No new geological experiment, submission file, portal upload, or weekly slot was authorized or used. The existing negative scientific decisions remain unchanged.

## Finding fixed

**High severity — contradictory submission approval in the generated site.** The executive summary, landing page, and nine site pages simultaneously said “no TIFF cleared” and that the old SWGB raster was “selector-cleared.” The download index also labeled that withdrawn SWGB TIFF “OK TO SUBMIT.” This contradicted the later registry-lattice audit, which measured 44,033/44,090 (99.8707%) of SWGB positive pixels within 3 px of the pinned lattice, exceeding the stated 70% rule.

Updated the static-site generator's decision banner and the downloads README to state explicitly that no repository TIFF is approved. Added a regression test across the generated landing page, executive summary, all nine site pages, and downloads index. Rebuilt generated Pages files.

## Verification

- Python suite: **54 passed**; remaining output is dependency/test-fixture warnings (Rasterio affine `PendingDeprecationWarning` and one expected `NotGeoreferencedWarning`).
- JavaScript source-feed suite: **5 passed**; `node --check` passed.
- `scripts/verify_release.py`: passed; 9 summaries and 182 internal links checked, negative card preserved, no false approval, no slot use.
- `scripts/check_release_entrypoints.py`: passed.
- `scripts/verify_swgb_correction.py`: passed; revoked artifact hash remains intact and pages block submission.
- `git diff --check`: passed.

## Remaining limits

- No new TIF is approved or offered for competition submission. Historical score reports, including GEMSDOE32's 0.2778, are not backed here by organizer receipts and do not support a calibrated forecast.
- The literal novelty policy remains obstructed by the calibration lattice. Do not start another experiment or reinterpret the rule without an explicit, versioned policy decision.
- Official competition data/rules/leaderboard access and organizer receipts were not available to this review. The pinned public mirrors are not organizer authentication.
- The exact current upstream registry may have changed since its frozen snapshot; no global or current uniqueness claim is made.

The update corrects user-facing release status only. It does not change holdout results, the negative decision, or any scientific evidence.
