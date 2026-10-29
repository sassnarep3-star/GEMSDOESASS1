# Repository review — 2026-10-29

## Executive decision

**The repository is a research/audit dashboard, not currently a source of an approved competition upload. Do not submit a TIFF from this checkout.** This is the right fail-closed outcome given the current evidence, even though it does not satisfy the original goal of producing a new high-scoring submission.

The strongest user-reported result in the nine-site focus set is GEMSDOE32 at 0.2778. The repository independently reproduces the file's mask relationship to its base raster, but has no organizer submission receipt; therefore this is an unverified historical report, not a verified score or a score forecast. The specific idea is removal of catalogue-proximal dots from a pre-existing raster, not evidence that a new geological predictor will outperform it.

## Verified repository state

- Working tree was clean at review start on `arena/bdfce0a1-gemsdoesass1`.
- `scripts/verify_release.py` passed: strict JSON, nine focus-site summaries, 171 local links, code/vendor hashes, no active submission TIFF, and no slot use.
- After installing the pinned `requirements-lock.txt` into the ignored `.venv`, the full test suite passed: **53 passed**. There were 19 non-failing rasterio warnings (PendingDeprecationWarning and one NotGeoreferencedWarning in test fixtures).
- `git diff --check` passed.
- No experiment, raster generation, upload, or selector action was performed in this review. The active protocol says to stop after the negative/duplicate findings; repeating an experiment would not repair the existing evidence gaps.

## Material risks and blockers

1. **No candidate is cleared.** The documented PBSC holdout is 0.0650 [0.0605, 0.0693], below the documented 0.1011 comparison bar; its registry-lattice dot overlap is 99.48%, above the literal 70% limit. Prior SWGB is also withdrawn after a 99.8707% lattice overlap audit. BGAC stopped at the duplicate gate. These are recorded negative results, not candidates to promote.
2. **The novelty rule has a registry-policy obstruction.** A calibration lattice covers nearly all footprint pixels within 3 px. Under the literal protocol, competitive-size dot rasters are likely to fail. The repository appropriately does not silently exempt it. A versioned policy clarification and agreed registry definition are needed before another experiment can reach a meaningful packaging decision.
3. **Score estimates are correctly unavailable.** Holdout DTI is not calibrated to leaderboard DTI. Current rules, current leaderboard, submission cap, and organizer receipts are not verified in this environment. The score claims in the user-provided ledger must remain labeled unverified owner reports.
4. **Registry freshness is not current.** The review log reports GEMSDOE24 advanced from the frozen commit. The frozen audit is reproducible but does not prove uniqueness against current public heads, other sites, private files, or future submissions. Refresh and rerun the registry audit before making any new uniqueness claim.
5. **Official competition inputs remain an access limitation.** Data/rules and some named official science layers are behind login or outside the sandbox's outbound allowlist. Owner mirrors do not authenticate organizer input provenance. This prevents independent verification of current format authority, some claims and official score information.
6. **No new uploadable TIFF exists.** This is explicit throughout the dashboard and is safer than exposing a format-valid but scientifically/novelty-disqualified raster. A valid GeoTIFF is not equivalent to scientific promotion or portal acceptance.

## Review observations

- The site gives a clear blocked status, explains how to submit in principle, and avoids presenting historical scores as validated forecasts.
- `docs/PROJECT_BRIEF.md` is a deduplicated operational transcription, not verbatim: the original repeated a block and this file says it removed that duplicate. The heading was corrected to avoid claiming otherwise.
- Some content is intentionally historical and may become stale as public repository heads move. The current-head advisory feed is not a substitute for refreshing the pinned experiment registry or checking the official leaderboard.
- There is no justified basis in this checkout to say that a new candidate will beat 0.2778, 0.3195, or 0.4413. Nor is a high score implied by geological plausibility alone.

## Recommended next steps

1. Obtain organizer-authoritative data, submission format, rules and score receipts in an authorized environment; record hashes and provenance.
2. Resolve and document whether calibration/diagnostic rasters are in the novelty registry. Keep the decision explicit and prospective; do not change the threshold retroactively to clear an existing candidate.
3. Refresh all nine public focus-site registries at pinned commits, then rerun surface and final-dot novelty checks.
4. Establish a comparable, spatially blocked holdout incumbent under the shared evaluator. Preregister at most three genuinely distinct hypotheses with per-feature leakage canaries and physical non-fault mimics.
5. Only if a candidate clears the agreed novelty policy and beats the holdout bar with a compatible comparison, use the shared writer and validate the emitted bytes. Keep selection/upload as a separate authorized step.

## Sources within this repository

- [Executive summary](executive-summary.html)
- [Protocol and experiment evidence](evidence.html)
- [Negative run card](../evidence/run_card.json)
- [PBSC run card and lattice audit](../evidence/pbsc/run_card.json) · [audit](../evidence/pbsc/lattice_audit.json)
- [SWGB withdrawal decision](../evidence/swgb/release_decision.json) · [lattice review](../evidence/swgb_lattice_review.json)
- [Ordered next steps](../knowledge/NEXT_STEPS.md)
- [Scientific interpretation of 0.2778](../knowledge/01_why_0p2778_and_what_beats_it.md)
