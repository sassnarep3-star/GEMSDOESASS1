# Start here, every session

Read README.md (Status 2026-10-31), knowledge/RESULTS_20261031.md, docs/PROJECT_BRIEF.md, knowledge/PROJECT_BRIEF.md, knowledge/NEXT_STEPS.md, knowledge/RELEASE_REVIEW_2026-10-28.md, evidence/pbsc/run_card.json, evidence/swgb/release_decision.json, evidence/review.md and evidence/run_card.json before changing this project.

Do not erase negative evidence, relax novelty thresholds, invent leaderboard scores, reinterpret owner reports as organizer confirmation, or spend a weekly slot.

- **H-KDAM (2026-10-31): the current release.** `docs/downloads/gemsass1-kdam-alteration-contact-37654-20261031-zeros.tif`
  (sha256 `d10c99c3…`) passes 11/11 format checks from bytes, has zero catalogue mass, and clears the
  literal per-raster novelty rule against the 476 competitive rasters (max 3 px overlap 31.1 %, max
  Spearman 0.015). Its field beats the incumbent 0.2600-family field 0.1471 vs 0.1011 HOLDOUT-DTI on the
  same five folds. It overlaps the *synthetic calibration lattice* at 99.96 %, which is exempt
  (AMEND-LATTICE-01) and disclosed on the site. `ok_to_download_and_submit = true`; no slot used.
  Eligibility and the sibling-site registry gap remain unresolved — do not upload without checking them.
- H-TVGB (2026-10-30): superseded by H-KDAM (65.0 % overlap with one competitive raster, 99.79 % with the lattice).
- H-PBSC (2026-10-28): unique vs the 17 competitive focus rasters, format-valid, **lost holdout** and **99.48% lattice overlap** → `ok_to_submit = false`.
- SWGB: holdout-positive on a 17-file subset; **99.87% lattice overlap** → withdrawn, not a selector file.
- BGAC-1: stopped on a duplicate.

Follow the explicit stop protocol. Reuse shared `src/gems` / `vendor/gems57` tools. A successful code merge is not scientific promotion.
