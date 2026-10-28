# Release reconciliation — 2026-10-28

## Pass 1: inventory

The root page, SWGB pages and README previously presented an old TIFF as ready to submit. The SWGB run card tests 17 selected registry rasters, whereas the frozen BGAC inventory lists 414 TIFF blobs outside `data/` in the nine repositories. A selected-file test cannot prove a pass against **any registry raster**. The BGAC corrected audit found a near-saturating calibration lattice and stopped before placement; that result is for BGAC, not a measured overlap for SWGB. No SWGB full-registry result is claimed here. Current heads may differ from the frozen snapshot.

The SWGB TIFF and historical run card are retained unmodified for provenance. Its local format receipt is not an official acceptance receipt, and its `promote` verdict was based on a narrower experiment and registry. Its claimed holdout improvement is not a reliable leaderboard forecast; catalogue-informed frozen prior rasters are not necessarily a fair hide-and-recover control. The active BGAC run's holdout is disqualified as promotion evidence because the first-pass gate was wrong. See [review](review.md) and [next steps](../knowledge/NEXT_STEPS.md).

## Pass 2: correction

Root landing and SWGB pages now fail closed and point to the reviewed executive summary. The old SWGB site generator is disabled so a rebuild cannot restore the unsupported promotion. Historical raw evidence was not changed and the old website remains recoverable in Git history. No TIFF was generated, re-evaluated or selected, and no weekly slot was spent in this review.

## Pass 3: remaining work

Complete the full, current registry audit at surface and dot stages under a clearly authorized future lane and resolve the literal lattice obstruction before placement. Obtain official template provenance, rules and organizer receipts via an authorized environment; evaluate a visible-only incumbent on the same buffered holdout. Do not convert a holdout to a leaderboard prediction. A repository merge is not a submission approval.

Evidence: [SWGB run card](swgb/run_card.json), [BGAC run card](run_card.json), [surface audit](corrected_surface_novelty.json), [nine-site inventory](../registry/focus_inventory.json). [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [competition data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) and [competition rules](https://www.drivendata.org/competitions/306/competition-doe-gems/) are provided for review; pages outside the sandbox allowlist were not independently verified this session.

## Subsequent witness measurement

A later review directly measured the historical SWGB TIFF against the lattice, finding a duplicate under the literal overlap rule. See [witness audit](swgb_witness_audit.json) and [review](review_2026-10-28.md). This does not change the historic account above.
