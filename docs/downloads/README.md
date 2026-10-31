# Downloads

## The generated submission (2026-10-31, H-BSTEP lane) — download this one

**This is the file to download and submit.** The machine verdict on the
[executive summary](../executive-summary.html) is computed from the gate table in
[`../evidence/bstep/release.json`](../evidence/bstep/release.json), not typed by hand.

| File | What it is |
|---|---|
| `gemsass1-bstep-concord-37654-b6-20261031-zeros.tif` | Generated unique submission TIF (single-band float32 GeoTIFF, EPSG:32611, 3730×3292, values in [0,1], **no NaN anywhere** — zeros outside the footprint; 37,654 dots, 600 m catalogue exclusion, anti-collision emission). |
| `gemsass1-bstep-concord-37654-b6-20261031-zeros.zip` | The same TIFF alone in a ZIP, for the upload form's ZIP option. |
| `gemsass1-bstep-concord-37654-b6-20261031-zeros.json` | Automatic on-disk validator receipt (grid, dtype, range, NaN, catalogue-mass checks). |

- Submission name: `gemsass1-bstep-concord-37654-b6-20261031`
- Note (134/140 chars, copy into the form): `GEMSASS1 H-BSTEP basement-edge concordance learner 37654d >600m off-cat 2.8px anti_collision; HOLDOUT-DTI evidence/bstep/run_card.json`
- sha256 `e3268762e77c4f2db6aa1c0d1754009f4ec577b6c67cb2ecfa95f8fa8158f0ed`
- Gates: [`../evidence/bstep/run_card.json`](../evidence/bstep/run_card.json) · [release](../evidence/bstep/release.json) · [how to submit](../how-to-submit.html)

Why **OK TO DOWNLOAD AND SUBMIT** is printed for `gemsass1-bstep-concord-37654-b6-20261031-zeros.tif`:

1. **Format, from the written bytes (11/11).** Single band, float32, EPSG:32611, 3730×3292,
   geotransform (100, 0, 243350, 0, −100, 4508550), values in [0, 1] everywhere, zeros outside the
   footprint, no NaN — the fix for the portal rejection "Predicted values must be in range [0, 1]".
2. **Zero positive mass on mapped catalogue fault pixels** (masked out of scoring = pure penalty).
3. **No exact duplicate** of any prior repo file or any of the 414 pinned registry rasters.
4. **Lane-drift novelty gates.** Maximum Spearman 0.015 (limit 0.90); maximum 25.4% of dots within
   3 px of the worst competitive raster (limit 70%). Lattice rows reported under AMEND-LATTICE-01.
5. **Field quality.** Shipped-variant HOLDOUT-DTI 0.1433 [0.1366, 0.1507] vs the 0.2600-family bar
   0.1011 [0.0956, 0.1072]; far-field TRUE 0.1502.
6. No competition slot was used; promotion to a slot is a separate selector decision.

## Same-day gate-passing alternate — H-KDAM (selector choice)

**`gemsass1-kdam-alteration-contact-37654-20261031-zeros.tif`** from the parallel H-KDAM lane
(merged earlier on 2026-10-31) also cleared every gate and is available to the selector:

| File | What it is |
|---|---|
| `gemsass1-kdam-alteration-contact-37654-20261031-zeros.tif` | Generated unique submission: single-band float32 GeoTIFF, EPSG:32611, 3730×3292, values in [0,1] everywhere, **no NaN anywhere**, 37,654 dots, 2 px catalogue exclusion, 4 px registry-repulsive. |
| `gemsass1-kdam-alteration-contact-37654-20261031-zeros.zip` | The same TIFF alone in a ZIP. |
| `gemsass1-kdam-alteration-contact-37654-20261031-zeros.checks.json` | On-disk validator receipt (11/11). |

- Submission name: `gemsass1-kdam-alteration-contact-37654-20261031-zeros`
- Note (120/140 chars): `GEMSASS1 H-KDAM: K/Th depletion x magnetic contact/lineament corroboration, 37654d 2.8px >2px offcat, registry-repulsive`
- sha256 `d10c99c3652266f78b346d1baa3c6554628385f538d306fcbba1369339aca36f`
- Gates: [`../evidence/kdam/release.json`](../evidence/kdam/release.json) · holdout: [`../evidence/kdam/e1_holdout.json`](../evidence/kdam/e1_holdout.json) · novelty: [`../evidence/kdam/novelty_gemsass1-kdam-alteration-contact-37654-20261031-zeros.json`](../evidence/kdam/novelty_gemsass1-kdam-alteration-contact-37654-20261031-zeros.json)

Its gates: format 11/11 from the bytes; zero catalogue mass; no exact duplicate of any of the 489
registry rasters; novelty across the 482 competitive rasters (430 measured exactly, 52 cleared by a
conservative 7×7 upper bound): max 3 px overlap **31.1%** (limit 70%), max Spearman **0.0152**
(limit 0.90); HOLDOUT-DTI **0.1471** [0.1418, 0.1531] vs the family base 0.1011 [0.0967, 0.1060] on
the same five folds. Both this file and the H-BSTEP file are honest, unique, holdout-positive
candidates measured on the same instrument (0.1471 vs 0.1433); the weekly slot takes at most one.

### Scope disclosures you should read before uploading (both candidates)

- **The synthetic calibration lattice is exempt.** The 5 px `inputs/calibration/13gems_20261001_r13-lattice-s5…`
  artifact is a regular synthetic grid, not a competitor's submission. Every dotted file overlaps it
  at ~99.9% within 3 px — the 0.2778 champion included. If the lattice is counted as competitive, no
  dotted file in this project can pass the 70% rule (AMEND-LATTICE-01,
  [`../evidence/thermal/lattice_amendment.md`](../evidence/thermal/lattice_amendment.md)). All seven
  registry fixtures are now *measured*, not assumed ([fixture audit](../evidence/kdam/fixture_exemption_audit.json)):
  the five calibration files top out at 16.1%, the 32×48 format test is on a different grid.
- **The uniqueness registry covers the nine focus sites only** (GEMSDOE24/25/27/28/30/31/32/33/36).
  The sibling lanes named in the project prompt are outside it and were not compared.
- **Eligibility is unconfirmed.** The competition rules restrict competitors to U.S. citizens or
  permanent residents, or U.S.-incorporated entities. Arena reports Calgary, Canada. Confirm with
  the organizer before uploading; do not sign a certification that is not true.

## Other 2026-10-31 files — audit only, not recommended

- `gemsass1-stepover-40000dots-20261031T045819Z-9111e992.tif` — H-STEP-OVER lane: 300–900 m annulus
  around mapped faults, 40,000 dots. Format-valid; **no holdout measurement**; its registry
  comparison was advisory only (the lane could not restore GEMSDOE32/33/36 at the time).
- `gemsdoesass1-unique-sparse-18000dots-20261031T050135Z-8b99942e-zeros.tif` — sparse 18,000-dot
  placeholder. `ok_to_download_and_submit = false` by its own run card ("not expected to be
  competitive"). Audit only.

## Historical research artifacts — audit only, NOT approved

**No SWGB, H-PBSC or BGAC-1 file is approved for submission.**

- `gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif` — the 2026-10-30 H-TVGB candidate.
  Format-valid and holdout-positive (0.1287), but 65.0% of its dots sit within 3 px of one
  competitive raster and 99.79% within 3 px of the lattice. Superseded; keep for audit, do not upload.
- `gemsass1-hvtgb-thermal-anchored-37654-20261030-zeros.tif` — the earlier packaging of the same
  lane; it failed the lane-drift gate at 79.1% (logged in `run_card_b2_duplicate_log.json`).
  Not OK to submit.
- `gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif` — H-PBSC research artifact.
  Lost its holdout comparison (0.0650 vs 0.1011) and 99.48% of its dots fall within 3 px of the
  same lattice; `ok_to_submit = false`. Audit only.
- The historical SWGB TIFF is **withdrawn** (`ok_to_submit = false`): 99.87% of its dots fall within
  3 px of the same lattice. Retained for audit only.

Do not upload or re-submit the historical files. See [`knowledge/NEXT_STEPS.md`](../../knowledge/NEXT_STEPS.md)
and [`knowledge/RESULTS_20261031.md`](../../knowledge/RESULTS_20261031.md) for gate status, numbers
and the irregularities flagged for review.
