# Downloads

## Current status (2026-10-31, H-REGAVOID session)

| File | Verdict | HOLDOUT-DTI (labelled) | Uniqueness vs 414-raster registry |
|---|---|---|---|
| `gemsass1-regavoid-m2-36557dots-20261031T060637Z-cb801cf1f910-zeros.tif` (2026-10-31, H-REGAVOID) | **NOT OK — DO NOT SUBMIT** (AMEND-2 shipped-bytes gate, preregistered) | protocol rule-quality cell **0.4443 [0.4349, 0.4529]**; **shipped bytes 0.000027** (structural: full-catalogue prune) | cleared: dots max 3 px overlap **0.188**, max ρ 0.003 (no duplicates) |
| `gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif` (2026-10-30, H-TVGB) | **OK per its own gates — the standing download** | rule-quality cell 0.1287 [0.1231, 0.1355]; **shipped bytes measured 0.0000** — IR-SHIPPED-BITS-01: the release cited the visible-prune E3 cell while the file was emitted full-catalogue-pruned; every full-catalogue-pruned file scores ~0 on hide-recover | cleared: 0.650 ≤ 0.70 |

Neither number forecasts a leaderboard score (holdout↔live Spearman −0.08). Eligibility (rules
§1.3) and the weekly-cap selector remain blocking user decisions before any upload.

## The standing submission file (2026-10-30, H-TVGB lane)


**This is the only file to download and submit.** Read the machine verdict on the
[executive summary](../executive-summary.html) first — it is computed from the run card's gate
table, not typed by hand.

| File | What it is |
|---|---|
| `gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif` | Generated unique submission TIF (single-band float32 GeoTIFF, values in [0,1], no NaN anywhere — zeros outside the footprint; 37,654 dots, 600 m catalogue exclusion). |
| `gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.zip` | The same TIFF alone in a ZIP, for the upload form's ZIP option. |
| `gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.checks.json` | Automatic on-disk validator receipt (grid, dtype, range, NaN, catalogue-mass checks). |

- Submission name: `gemsass1-hvtgb-thermal-anchored-37654-b6-20261030`
- Note (≤140 chars, copy into the form): `GEMSASS1 H-TVGB thermal-anchored supervised 37654d >600m-off-cat 2.8px; see evidence/thermal/run_card.json`
- sha256 and gates: [`../evidence/thermal/run_card.json`](../evidence/thermal/run_card.json) · verdict page: [how to submit](../how-to-submit.html)

**OK TO DOWNLOAD AND SUBMIT** is printed for `gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif`
because every gate passed: format validator (values in [0,1], no NaN, exact CRS/shape/geotransform),
no exact duplicate of any registry raster or prior repo file, lane-drift novelty gates (Spearman ≤ 0.90
and ≤ 70% of dots within 3 px of any competitive registry raster), HOLDOUT-DTI above the 0.2600-family
bar (0.1287 [0.1231, 0.1355] vs 0.1011), zero mass on mapped faults. If a future run's verdict reads
NOT OK, do not upload that run's file.

## Historical research artifacts — audit only, NOT approved

| File | What it is |
|---|---|
| `gemsass1-regavoid-m2-36557dots-20261031T060637Z-cb801cf1f910-zeros.*` | 2026-10-31 H-REGAVOID research artifacts (**NOT OK** — AMEND-2; sha256 `6568c180441c99bedfda233321184a729e7dddaef850d7062ad5aa5968c50a47`; validator 11/11). Kept for the record: protocol rule-quality cell 0.4443, novelty cleared at 0.188 overlap. |

**No SWGB, H-PBSC or BGAC-1 file is approved for submission.** These files stay here for
reproducibility and negative-evidence audits:

- `gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif` — format-valid H-PBSC
  research artifact. It lost its holdout comparison (HOLDOUT-DTI 0.0650 vs bar 0.1011) and 99.48%
  of its dots fall within 3 px of the calibration lattice; `ok_to_submit = false`. Audit only.
- `gemsass1-hvtgb-thermal-anchored-37654-20261030-zeros.tif` — the superseded first packaging of
  this release. Its dots failed the lane-drift gate (79.1% within 3 px of
  `gems25-h38-greedy-credit-k3p5-20261025-18de99d38bb0-nan.tif`); it is logged as a duplicate in
  `run_card_b2_duplicate_log.json` and is NOT OK to submit. Kept for audit only.
- The historical SWGB TIFF is withdrawn: 99.87% of its dots fall within 3 px of the same lattice.
  It is retained for audit only, not as an approved selector output.

Do not upload or re-submit the historical files. See
[`knowledge/NEXT_STEPS.md`](../../knowledge/NEXT_STEPS.md) and
[`evidence/thermal/lattice_amendment.md`](../evidence/thermal/lattice_amendment.md) for gate
status and the IR-LATTICE-01 scope amendment.
