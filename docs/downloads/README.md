# Downloads

## The generated submission (2026-10-31, H-TIPRELAY lane) — ACTIVE

**This is the only file to download and submit.** Read the machine verdict on the
[executive summary](../executive-summary.html) first — it is computed from the run card's gate
table, not typed by hand.

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

## Superseded generated release (2026-10-30, H-TVGB lane) — DO NOT SUBMIT

`gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif` passed its own session's gates and is
now **superseded** by the 2026-10-31 file above. The 2 px packaging
(`gemsass1-hvtgb-thermal-anchored-37654-20261030-zeros.tif`) was logged as a lane-drift duplicate
(79.1% within 3 px of one GEMSDOE25 raster) and was never OK to submit.

## Historical research artifacts — audit only, NOT approved

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
