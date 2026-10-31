# Downloads

## The generated submission (2026-10-31, H-KDAM lane) — download this one

**This is the only file to download and submit.** The machine verdict at the top of the
[executive summary](../executive-summary.html) is computed from the gate table in
[`../evidence/kdam/release.json`](../evidence/kdam/release.json), not typed by hand.

| File | What it is |
|---|---|
| `gemsass1-kdam-alteration-contact-37654-20261031-zeros.tif` | Generated unique submission: single-band float32 GeoTIFF, EPSG:32611, 3730×3292, values in [0,1] everywhere, **no NaN anywhere** (zeros outside the footprint), 37,654 dots, 2 px catalogue exclusion, 4 px registry-repulsive. |
| `gemsass1-kdam-alteration-contact-37654-20261031-zeros.zip` | The same TIFF alone in a ZIP, for the upload form's ZIP option. |
| `gemsass1-kdam-alteration-contact-37654-20261031-zeros.checks.json` | On-disk validator receipt written after the file was reopened from bytes. |

- Submission name: `gemsass1-kdam-alteration-contact-37654-20261031-zeros`
- Note (120/140 chars, copy into the form): `GEMSASS1 H-KDAM: K/Th depletion x magnetic contact/lineament corroboration, 37654d 2.8px >2px offcat, registry-repulsive`
- sha256 `d10c99c3652266f78b346d1baa3c6554628385f538d306fcbba1369339aca36f`
- Gates: [`../evidence/kdam/release.json`](../evidence/kdam/release.json) · holdout: [`../evidence/kdam/e1_holdout.json`](../evidence/kdam/e1_holdout.json) · novelty scan: [`../evidence/kdam/novelty_gemsass1-kdam-alteration-contact-37654-20261031-zeros.json`](../evidence/kdam/novelty_gemsass1-kdam-alteration-contact-37654-20261031-zeros.json)

Why **OK TO DOWNLOAD AND SUBMIT** is printed for this file:

1. **Format, from the written bytes (11/11).** Single band, float32, EPSG:32611, 3730×3292,
   geotransform (100, 0, 243350, 0, −100, 4508550), values in [0, 1] everywhere, zeros outside the
   footprint, no NaN. The portal's "Predicted values must be in range [0, 1]" rejection is caused by
   NaN/out-of-range files; this file contains neither.
2. **Zero positive mass on mapped catalogue fault pixels** — those pixels are masked out of scoring, so
   mass there is pure penalty.
3. **No exact duplicate** of any of the 489 registry rasters.
4. **Novelty / lane-drift gate.** Across the 482 competitive rasters (430 overlap measured exactly,
   52 cleared by a conservative 7×7 upper bound): maximum 3 px overlap **31.1 %** (limit 70 %) and maximum
   Spearman **0.0152** (limit 0.90). All 7 remaining rasters in the 489-raster inventory are measured too
   (`scripts/audit_fixtures.py`): the five calibration files top out at 16.1 %, the 32×48 format test is on a
   different grid, and the synthetic 5 px lattice reaches 99.96 % and stays exempt under AMEND-LATTICE-01.
5. **Field quality, measured against the incumbent.** HOLDOUT-DTI 0.1471 vs 0.1011 for the field behind
   every file ≥ 0.24 in the nine focus sites, same five folds, same emission rule.
6. No competition slot was used by this workspace; promotion to a slot is a separate selector decision.

### Scope disclosures you should read before uploading

- **The synthetic calibration lattice is exempt.** The 5 px `inputs/calibration/13gems_20261001_r13-lattice-s5…`
  artifact is a regular synthetic grid, not a competitor's submission. This file overlaps it at **99.96 %**
  within 3 px — as does every dotted file, including the 0.2778 champion itself. If the lattice is counted
  as competitive, no dotted file in this project can pass the 70 % rule (AMEND-LATTICE-01,
  [`../evidence/thermal/lattice_amendment.md`](../evidence/thermal/lattice_amendment.md)).
- **The uniqueness registry covers the nine focus sites only** (GEMSDOE24/25/27/28/30/31/32/33/36). The
  sibling lanes named in the project prompt are outside it and were not compared.
- **Eligibility is unconfirmed.** The competition rules restrict competitors to U.S. citizens or permanent
  residents, or U.S.-incorporated entities. Confirm with the organizer before uploading; do not sign a
  certification that is not true.

## Historical research artifacts — audit only, NOT approved

- `gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif` — last session's candidate. Format-valid and
  holdout-positive (0.1287), but it did not clear the novelty gate the way this session's file does: 65.0 %
  of its dots sit within 3 px of one competitive raster and 99.79 % within 3 px of the lattice. Superseded;
  keep for audit, do not upload.
- `gemsass1-hvtgb-thermal-anchored-37654-20261030-zeros.tif` — the earlier packaging of the same lane; it
  failed the lane-drift gate at 79.1 % (logged in `run_card_b2_duplicate_log.json`). Not OK to submit.
- `gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif` — H-PBSC research artifact. Lost its
  holdout comparison (0.0650 vs 0.1011). Not OK to submit.
- The historical SWGB TIFF remains **withdrawn** and audit-only (`ok_to_submit = false`).

See [`knowledge/NEXT_STEPS.md`](../../knowledge/NEXT_STEPS.md) and
[`knowledge/RESULTS_20261031.md`](../../knowledge/RESULTS_20261031.md) for gate status, numbers and the
irregularities flagged for review.
