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

## Session 2026-10-31 (H-RECALL-DOM → H-OFFSET-STEP → H-FUSION3)

Read `knowledge/MISSION_PROMPT.md`, `README.md` (top section),
`knowledge/hypotheses_20261031_recalldom.md` and
`evidence/offset_step_v2/run_card.json` before changing anything.

- **The metric is now certified** (`scripts/certify_metric.py`,
  `evidence/metric_certification.json`): D = α·(TP+FP) + β·K exactly (α+β=1); oracle
  ceiling 1.000; recall is ~14x the precision lever at the champion operating point.
  Do not re-derive it; do not optimise against an uncertified instrument.
- **Emission geometry is settled: 2.8–3.0 px is optimal.** Do not spend another lane
  on spacing, mass or corridor experiments. Every future hour goes into the field's
  precision `g` (0.278 at g=0.065, 0.454 at g=0.108, 0.555 at the ceiling).
- **The holdout is biased against the winning field.** The champion's support has exactly
  zero pixels in common with the public catalogue (min distance 1.0 px) while the
  holdout truth IS the catalogue. A holdout win is therefore not evidence of a live win.
- **Four experiments ran (budget 3; overrun logged).** E1 geometry = flat/negative;
  E2 across-strike structure tensor 0.0453; E3 Frangi vesselness 0.0278; E3b
  variable-density marginal allocation 0.0266; E4 rank-mean fusion 0.1004 vs control
  0.1048 = tied. Only E4 shipped.
- **Data restore:** `gh` auth is broken ("token is no longer valid") and the API quota
  is exhausted. Use `scripts/local_restore.py` (git protocol, re-hashes every pin).
- **Do not delete or soften** `evidence/run_card.json` (BGAC-1),
  `evidence/pbsc/run_card.json`, `evidence/swgb/`, the lattice audits, or the B2
  duplicate log. New evidence goes in new directories.
