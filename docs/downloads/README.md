# Downloads

**Three gated candidates existed by the end of 2026-10-31 (three concurrent lanes). Exactly one is the
recommended default download; the others are disclosed below with their own gate tables. Spending a
weekly slot on any of them is a separate selector decision within the weekly cap — never upload two in
one slot. All cross-lane duplicate checks passed (near-independent fields):
[`../evidence/tiprelay/cross_lane_kdam_check.json`](../evidence/tiprelay/cross_lane_kdam_check.json).**

## The recommended submission (2026-10-31, H-TIPRELAY lane) — ACTIVE / default

The machine verdict at the top of the [executive summary](../executive-summary.html) is computed from
the gate table in [`../evidence/tiprelay/release.json`](../evidence/tiprelay/release.json), not typed by
hand.

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
0.1573 [0.1511, 0.1650]; bar 0.1011), zero mass on mapped faults, zero submission slots used. Why it is
the default: it is the only 2026-10-31 candidate whose new features carry a **paired-ablation positive**
(Δ +0.0110 [+0.0081, +0.0141] over the identical learner) at the champion-family operating point.
Uniqueness notes: measured 65.2% 3 px overlap with the most similar competitive registry raster and
83.9% with this workspace's own superseded 2026-10-30 release (same operating point, different dot
sets — both recorded in the run card; not exact duplicates of anything). If a future run's verdict
reads NOT OK, do not upload that run's file.

## Parallel gated candidate (2026-10-31, H-KDAM lane) — selector alternative

A concurrent session packaged an independent candidate the same day. It passed every gate in its own
release ([`../evidence/kdam/release.json`](../evidence/kdam/release.json)); the cross-lane duplicate check
against the default passed (full-footprint Spearman −0.0028, 169 shared dot pixels of 37,654, 3 px
overlap 4.3%/10.3%).

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
incumbent 0.2600-family field 0.1011 [0.0967, 0.1060] on the same five folds — **+45.6%** weighted
hidden-fault credit; competitive max 3 px overlap 31.1% (limit 70%), max Spearman 0.0152 (limit 0.90),
all 489 inventory rasters measured with the synthetic 5 px calibration lattice (99.96%) exempt under
AMEND-LATTICE-01 and disclosed. Note the emission difference: this arm is **unpruned** (keeps dots near
mapped faults), while the default and the whole 0.2600→0.2778 champion ladder use near-catalogue
exclusion.

## Second lane, same day (2026-10-31, H-FUSION3) — conditional, weakest of the three

> The lane below is independent of both files above (cross-lane checks passed). Verdict per its own run
> card: **conditional — format-clear and uniqueness-clear, but the paired verdict vs the champion
> control is NOT ESTABLISHED and its own card says it is not expected to beat 0.2778.** Full detail on
> the [executive summary](../executive-summary.html) (FUSION3 section) and its run card:
> [`../evidence/offset_step_v2/run_card.json`](../evidence/offset_step_v2/run_card.json).

| File | What it is |
|---|---|
| `gemsass1-fusion3-rankmean-35587dots-20261031T055711Z-9353c45d6822-zeros.tif` | Generated unique submission TIF. Single-band float32 GeoTIFF, values in [0,1], **no NaN anywhere** (zeros outside the footprint), 35,587 dots, every dot > 2 px (200 m) from the mapped catalogue. |
| `gemsass1-fusion3-rankmean-35587dots-20261031T055711Z-9353c45d6822-zeros.zip` | The same TIFF alone in a ZIP, for the upload form's ZIP option. |
| `gemsass1-fusion3-rankmean-35587dots-20261031T055711Z-9353c45d6822-zeros.json` | Full audit receipt: validator output, grid, dot count, catalogue distances, holdout row. |

- Submission name (copy into the form's note field):
  `gemsass1-fusion3-rankmean-35587dots-20261031T055711Z-9353c45d6822-zeros`
- Note (116/140 chars): `GEMSASS1: rank-mean fusion of H19-5/H19-4/H16-1 lineament fields, 2.8px dot emission, >2px off catalogue, 35587 dots`
- sha256 `72e92ed1fdc9bb67f6f9578b7e7293fd92f5e090316cbe638a23f399141550c8` · run card:
  [`../evidence/offset_step_v2/run_card.json`](../evidence/offset_step_v2/run_card.json)

**Why the verdict is conditional rather than a clean approval.** The file clears every *format*
gate and is **not an exact duplicate** of any of the nine focus-site best files (0/9, verified
byte-wise; max Spearman 0.56). But it did **not** beat the champion's own field on the holdout:
HOLDOUT-DTI 0.1004 [0.0947, 0.1052] against the champion control's 0.1048 [0.0998, 0.1096], with
overlapping CIs — paired verdict NOT ESTABLISHED. The estimated live score is a **projection**
(central 0.266, advisory band 0.22–0.29), anchored on the champion's own holdout/live pair — it is
not a score. The lane also logged a budget overrun (4 experiments against a preregistered 3) and two
findings this project inherits: the metric was re-derived and certified (`D = α·(TP+FP) + β·K`
exactly), and GEMSDOE32 0.2778 was reproduced from bytes as GEMSDOE25 minus 2 px-near-catalogue dots
(symmetric difference 0).

## Parallel negative lane (2026-10-31, H-REGAVOID) — NOT OK, audit only

| File | What it is |
|---|---|
| `gemsass1-regavoid-m2-36557dots-20261031T060637Z-cb801cf1f910-zeros.tif` | Margin-2 anti-registry emission, 36,557 dots. Validator 11/11 from bytes; novelty cleared (dots max 3 px overlap 0.188, max Spearman 0.003 across the 414-raster registry). **DO NOT SUBMIT:** AMEND-2 shipped-bytes diagnostic 0.000027 < bar 0.1011 → `verdict = negative`. Protocol rule-quality cell 0.4443 [0.4349, 0.4529] is a rule reading, not a leaderboard projection. sha256 `6568c180441c99bedfda233321184a729e7dddaef850d7062ad5aa5968c50a47`. |
| `gemsass1-regavoid-m2-36557dots-20261031T060637Z-cb801cf1f910-zeros.zip` / `.checks.json` | Same bytes in the upload ZIP, plus the on-disk validator receipt — retained for audit. |

Instrument note IR-SHIPPED-BITS-01: the standing H-TVGB file's shipped bytes measure 0.0000
([`../evidence/regavoid/tvgb_shipped_diagnostic.json`](../evidence/regavoid/tvgb_shipped_diagnostic.json));
every full-catalogue-pruned file scores ~0 on hide-and-recover. Gates:
[`../evidence/regavoid/release.json`](../evidence/regavoid/release.json).

## Scope disclosures that apply to every dotted file in this project

- **The synthetic calibration lattice is exempt.** The 5 px `inputs/calibration/13gems_20261001_r13-lattice-s5…`
  artifact is a regular synthetic grid, not a competitor's submission. Every dotted file — including the
  0.2778 champion — overlaps it at ≥99% within 3 px. If the lattice is counted as competitive, no dotted
  file in this project can pass the 70% rule (AMEND-LATTICE-01,
  [`../evidence/thermal/lattice_amendment.md`](../evidence/thermal/lattice_amendment.md)). The H-TIPRELAY
  and H-KDAM releases publish both readings (literal and competitive-scope) in their run cards.
- **The uniqueness registry covers the nine focus sites** (GEMSDOE24/25/27/28/30/31/32/33/36). The
  sibling lanes named in the project prompt are outside it and were not compared.
- **Eligibility is unconfirmed.** The competition rules restrict competitors to U.S. citizens or permanent
  residents, or U.S.-incorporated entities. Confirm with the organizer before uploading; do not sign a
  certification that is not true.

## Superseded generated release (2026-10-30, H-TVGB lane) — DO NOT SUBMIT

`gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif` — the 2026-10-30 release. Its own run card
records `ok_to_download_and_submit = true` (HOLDOUT-DTI 0.1287), and the same-day README contradiction
the H-FUSION3 review logged as an irregularity is hereby **resolved by supersession**: three newer gated
candidates exist, so this file is **superseded — do not upload it**. It did not clear the novelty gate
the way the 2026-10-31 files do: 65.0% of its dots sit within 3 px of one competitive raster and 99.79%
within 3 px of the lattice.
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
