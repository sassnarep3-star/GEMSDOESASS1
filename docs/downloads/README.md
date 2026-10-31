# Downloads

## The generated submission (2026-10-31, H-TIPRELAY lane) — ACTIVE / recommended

**This is the recommended file to download and submit.** The machine verdict at the top of the
[executive summary](../executive-summary.html) is computed from the gate table in
[`../evidence/tiprelay/release.json`](../evidence/tiprelay/release.json), not typed by hand.

| File | What it is |
|---|---|
| `gemsass1-tiprelay-continuation-37654-b6-20261031-zeros.tif` | Generated unique submission TIF (single-band float32 GeoTIFF, values in [0,1], no NaN anywhere — zeros outside the footprint; 37,654 dots, 2.8 px spacing, 600 m catalogue exclusion). |
| `gemsass1-tiprelay-continuation-37654-b6-20261031-zeros.zip` | The same TIFF alone in a ZIP, for the upload form's ZIP option. |
| `gemsass1-tiprelay-continuation-37654-b6-20261031-zeros.json` | Automatic on-disk validator receipt (grid, dtype, range, NaN, catalogue-mass checks). |

- Submission name: `gemsass1-tiprelay-continuation-37654-b6-20261031`
- Note (≤140 chars, copy into the form): `GEMSASS1 H-TIPRELAY tip-relay/stepover/persistence 37654d >600m-offcat 2.8px; HOLDOUT-DTI 0.1384 vs bar 0.101`
- sha256: `43017aa480526acf2789dbffb32202da830966b9dadc40cb4d84b995b651f5eb`
- Gates and full record: [`../evidence/tiprelay/run_card.json`](../evidence/tiprelay/run_card.json) · verdict page: [how to submit](../how-to-submit.html)

**OK TO DOWNLOAD AND SUBMIT** is printed for `gemsass1-tiprelay-continuation-37654-b6-20261031-zeros.tif`
because every gate passed: format validator (values in [0,1], no NaN, exact CRS/shape/geotransform),
no exact duplicate of any registry raster or prior repo file (414/414 scanned on disk), lane-drift
novelty gates (surface Spearman 0.132 ≤ 0.90; max competitive 3 px dot overlap 65.2% ≤ 70%),
HOLDOUT-DTI above the 0.2600-family bar (shipped cell 0.1384 [0.1322, 0.1458]; E1 ablation cell
0.1573 [0.1511, 0.1650]; bar 0.1011), zero mass on mapped faults, zero submission slots used.
Uniqueness notes: measured 65.2% 3 px overlap with the most similar competitive registry raster and
83.9% with this workspace's own superseded 2026-10-30 release (same operating point, different dot
sets — both recorded in the run card; not exact duplicates of anything). If a future run's verdict
reads NOT OK, do not upload that run's file.

## Parallel gated candidate (2026-10-31, H-KDAM lane) — selector alternative

A concurrent session packaged an independent candidate the same day. It passed every gate in its own
release ([`../evidence/kdam/release.json`](../evidence/kdam/release.json)); the cross-lane duplicate check
against the file above passed (full-footprint Spearman −0.0028, 169 shared dot pixels of 37,654, 3 px
overlap 4.3%/10.3% — [`../evidence/tiprelay/cross_lane_kdam_check.json`](../evidence/tiprelay/cross_lane_kdam_check.json)).
Choosing between the two is the selector's decision within the weekly cap; the default recommendation is
the H-TIPRELAY file above (champion-family-consistent emission; its features carry the paired-ablation
positive, Δ +0.0110 [+0.0081, +0.0141]).

| File | What it is |
|---|---|
| `gemsass1-kdam-alteration-contact-37654-20261031-zeros.tif` | Generated unique submission: single-band float32 GeoTIFF, EPSG:32611, 3730×3292, values in [0,1] everywhere, **no NaN anywhere** (zeros outside the footprint), 37,654 dots, 2 px catalogue exclusion, 4 px registry-repulsive. |
| `gemsass1-kdam-alteration-contact-37654-20261031-zeros.zip` | The same TIFF alone in a ZIP, for the upload form's ZIP option. |
| `gemsass1-kdam-alteration-contact-37654-20261031-zeros.checks.json` | On-disk validator receipt written after the file was reopened from bytes. |

- Submission name: `gemsass1-kdam-alteration-contact-37654-20261031-zeros`
- Note (120/140 chars, copy into the form): `GEMSASS1 H-KDAM: K/Th depletion x magnetic contact/lineament corroboration, 37654d 2.8px >2px offcat, registry-repulsive`
- sha256 `d10c99c3652266f78b346d1baa3c6554628385f538d306fcbba1369339aca36f`
- Gates: [`../evidence/kdam/release.json`](../evidence/kdam/release.json) · holdout: [`../evidence/kdam/e1_holdout.json`](../evidence/kdam/e1_holdout.json) · novelty scan: [`../evidence/kdam/novelty_gemsass1-kdam-alteration-contact-37654-20261031-zeros.json`](../evidence/kdam/novelty_gemsass1-kdam-alteration-contact-37654-20261031-zeros.json)

Measured on its lane's terms: HOLDOUT-DTI 0.1471 [0.1418, 0.1531] (unpruned arm, 37,654 dots) vs the
incumbent 0.2600-family field 0.1011 [0.0967, 0.1060] on the same five folds; competitive max 3 px
overlap 31.1% (limit 70%), max Spearman 0.0152 (limit 0.90), all 489 inventory rasters measured with the
synthetic 5 px calibration lattice (99.96%) exempt under AMEND-LATTICE-01 and disclosed.

### Scope disclosures that apply to every dotted file in this project

- **The synthetic calibration lattice is exempt.** The 5 px `inputs/calibration/13gems_20261001_r13-lattice-s5…`
  artifact is a regular synthetic grid, not a competitor's submission. Every dotted file — including the
  0.2778 champion — overlaps it at ≥99% within 3 px. If the lattice is counted as competitive, no dotted
  file in this project can pass the 70% rule (AMEND-LATTICE-01,
  [`../evidence/thermal/lattice_amendment.md`](../evidence/thermal/lattice_amendment.md)).
- **The uniqueness registry covers the nine focus sites** (GEMSDOE24/25/27/28/30/31/32/33/36). The
  sibling lanes named in the project prompt are outside it and were not compared.
- **Eligibility is unconfirmed.** The competition rules restrict competitors to U.S. citizens or permanent
  residents, or U.S.-incorporated entities. Confirm with the organizer before uploading; do not sign a
  certification that is not true.

## Superseded generated release (2026-10-30, H-TVGB lane) — DO NOT SUBMIT

`gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif` — last session's candidate. Format-valid and
holdout-positive (0.1287), but it did not clear the novelty gate the way this session's file does: 65.0%
of its dots sit within 3 px of one competitive raster and 99.79% within 3 px of the lattice. Superseded by
the 2026-10-31 files above; keep for audit, do not upload.
`gemsass1-hvtgb-thermal-anchored-37654-20261030-zeros.tif` — the earlier packaging of the same lane; it
failed the lane-drift gate at 79.1% (logged in `run_card_b2_duplicate_log.json`). Not OK to submit.

## Historical research artifacts — audit only, NOT approved

- `gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif` — H-PBSC research artifact. Lost its
  holdout comparison (0.0650 vs 0.1011). Not OK to submit.
- The 2026-10-31 step-over and sparse TIFFs are research artifacts, not submit-cleared
  (`ok_to_download_and_submit = false` on their cards).
- The historical SWGB TIFF remains **withdrawn** and audit-only (`ok_to_submit = false`).

See [`knowledge/NEXT_STEPS.md`](../../knowledge/NEXT_STEPS.md) and
[`knowledge/RESULTS_20261031.md`](../../knowledge/RESULTS_20261031.md) for gate status, numbers and the
irregularities flagged for review.
