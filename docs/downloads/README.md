# Downloads

**Four gate-passing candidates exist from the 2026-10-31 concurrent lanes. This page presents one
file (the current release); every candidate below keeps its own machine gate table and verdict.
Spending a weekly slot on any of them is a separate selector decision within the weekly cap —
never upload two in one slot. Cross-lane duplicate checks passed (near-independent fields):
[`../evidence/tiprelay/cross_lane_kdam_check.json`](../evidence/tiprelay/cross_lane_kdam_check.json).**

## The current release (2026-10-31, H-BSTEP lane) — download this one

The machine verdict on the [executive summary](../executive-summary.html) is computed from the gate
table in [`../evidence/bstep/release.json`](../evidence/bstep/release.json), not typed by hand.

| File | What it is |
|---|---|
| `gemsass1-bstep-concord-37654-b6-20261031-zeros.tif` | Generated unique submission TIF (single-band float32 GeoTIFF, EPSG:32611, 3730×3292, values in [0,1], **no NaN anywhere** — zeros outside the footprint; 37,654 dots, 600 m catalogue exclusion, anti-collision emission). |
| `gemsass1-bstep-concord-37654-b6-20261031-zeros.zip` | The same TIFF alone in a ZIP, for the upload form's ZIP option. |
| `gemsass1-bstep-concord-37654-b6-20261031-zeros.json` | Automatic on-disk validator receipt (grid, dtype, range, NaN, catalogue-mass checks). |

- Submission name: `gemsass1-bstep-concord-37654-b6-20261031`
- Note (134/140 chars, copy into the form): `GEMSASS1 H-BSTEP basement-edge concordance learner 37654d >600m off-cat 2.8px anti_collision; HOLDOUT-DTI evidence/bstep/run_card.json`
- sha256 `e3268762e77c4f2db6aa1c0d1754009f4ec577b6c67cb2ecfa95f8fa8158f0ed`
- Gates: [`../evidence/bstep/run_card.json`](../evidence/bstep/run_card.json) · [release](../evidence/bstep/release.json) · [how to submit](../how-to-submit.html)

**OK TO DOWNLOAD AND SUBMIT** is printed for `gemsass1-bstep-concord-37654-b6-20261031-zeros.tif`
because every gate passed: format validator 11/11 from the written bytes (values in [0,1], no NaN,
exact CRS/shape/geotransform), zero mass on mapped catalogue pixels, no exact duplicate of any prior
repo file or any of the 414 pinned registry rasters, lane-drift novelty gates (max Spearman 0.015
≤ 0.90; max competitive 3 px dot overlap 25.4% ≤ 70% — the cleanest novelty margins of the four
candidates), HOLDOUT-DTI above the 0.2600-family bar (shipped anti-collision emission variant, measured as a
**protocol cell** on the fold fields: 0.1433 [0.1366, 0.1507]; far-field TRUE 0.1502; bar 0.1011
[0.0956, 0.1072]), zero submission slots used. **Instrument note (IR-SHIPPED-BITS-01):** scoring the
literal shipped bytes of any full-catalogue-pruned file measures ~0 on hide-and-recover (the 0.2778
champion included — see the H-REGAVOID panel), so this number is a rule-quality protocol cell, not a
shipped-bytes score and never a leaderboard projection.

## Selector alternatives (2026-10-31) — each gate-passing, each with its own record

Choosing among these (or none) is the user's selector decision; this workspace never uploads.

| Candidate | File | HOLDOUT-DTI (its own protocol) | Max 3 px overlap vs competitive registry | Distinction | Record |
|---|---|---|---|---|---|
| **H-TIPRELAY** (main's three-lane cross-check recommended this as default) | `gemsass1-tiprelay-continuation-37654-b6-20261031-zeros.tif` | shipped cell 0.1384 [0.1322, 0.1458]; E1 ablation cell 0.1573 [0.1511, 0.1650] | 65.2% (limit 70%) | Only candidate whose new features carry a **paired-ablation positive** (Δ +0.0110 [+0.0081, +0.0141] over the identical learner) at the champion-family operating point | [`../evidence/tiprelay/run_card.json`](../evidence/tiprelay/run_card.json) |
| **H-KDAM** | `gemsass1-kdam-alteration-contact-37654-20261031-zeros.tif` | unpruned arm 0.1471 [0.1418, 0.1531] (emission is **unpruned**, unlike the champion ladder) | 31.1% | K/Th depletion × magnetic-contact corroboration; +45.6% weighted hidden-fault credit vs the family base on the same folds | [`../evidence/kdam/release.json`](../evidence/kdam/release.json) |
| **H-FUSION3** (conditional — weakest of the three) | `gemsass1-fusion3-rankmean-35587dots-20261031T055711Z-9353c45d6822-zeros.tif` | 0.1004 [0.0947, 0.1052] vs champion control 0.1048 — **paired verdict NOT ESTABLISHED**; its own card says not expected to beat 0.2778 | not an exact duplicate of any of the nine best (0/9 byte-wise; max Spearman 0.56) | Rank-mean fusion of H19-5/H19-4/H16-1 lineament fields, 35,587 dots > 2 px off catalogue. Estimated live score 0.266 is a **projection** (band 0.22–0.29), not a score | [`../evidence/offset_step_v2/run_card.json`](../evidence/offset_step_v2/run_card.json) |

Cross-lane duplicate checks between the candidates passed (e.g. tiprelay vs kdam: full-footprint
Spearman −0.0028, 3 px overlap 4.3%/10.3%) — the lanes found near-independent fields.

Submission names and notes for the alternatives (copy exactly if the selector chooses one):

- H-TIPRELAY — name `gemsass1-tiprelay-continuation-37654-b6-20261031`; note (≤140):
  `GEMSASS1 H-TIPRELAY tip-relay/stepover/persistence 37654d >600m-offcat 2.8px; HOLDOUT-DTI 0.1384 vs bar 0.101`; sha256 `43017aa480526acf2789dbffb32202da830966b9dadc40cb4d84b995b651f5eb`
- H-KDAM — name `gemsass1-kdam-alteration-contact-37654-20261031-zeros`; note (120/140):
  `GEMSASS1 H-KDAM: K/Th depletion x magnetic contact/lineament corroboration, 37654d 2.8px >2px offcat, registry-repulsive`; sha256 `d10c99c3652266f78b346d1baa3c6554628385f538d306fcbba1369339aca36f`
- H-FUSION3 — name `gemsass1-fusion3-rankmean-35587dots-20261031T055711Z-9353c45d6822-zeros`; note (116/140):
  `GEMSASS1: rank-mean fusion of H19-5/H19-4/H16-1 lineament fields, 2.8px dot emission, >2px off catalogue, 35587 dots`; sha256 `72e92ed1fdc9bb67f6f9578b7e7293fd92f5e090316cbe638a23f399141550c8`

## Other 2026-10-31 files — audit only, not recommended

- `gemsass1-stepover-40000dots-20261031T045819Z-9111e992.tif` — H-STEP-OVER lane: 300–900 m annulus
  around mapped faults, 40,000 dots. Format-valid; **no holdout measurement**; its registry
  comparison was advisory only (the lane could not restore GEMSDOE32/33/36 at the time).
- `gemsdoesass1-unique-sparse-18000dots-20261031T050135Z-8b99942e-zeros.tif` — sparse 18,000-dot
  placeholder. `ok_to_download_and_submit = false` by its own run card ("not expected to be
  competitive"). Audit only.

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
  artifact is a regular synthetic grid, not a competitor's submission. Every dotted file overlaps it
  at ~99.9% within 3 px — the 0.2778 champion included. If the lattice is counted as competitive, no
  dotted file in this project can pass the 70% rule (AMEND-LATTICE-01,
  [`../evidence/thermal/lattice_amendment.md`](../evidence/thermal/lattice_amendment.md)). All seven
  registry fixtures are *measured*, not assumed
  ([fixture audit](../evidence/kdam/fixture_exemption_audit.json)): the five calibration files top
  out at 16.1%, the 32×48 format test is on a different grid.
- **The uniqueness registry covers the nine focus sites only** (GEMSDOE24/25/27/28/30/31/32/33/36).
  The sibling lanes named in the project prompt are outside it and were not compared.
- **Eligibility is unconfirmed.** The competition rules restrict competitors to U.S. citizens or
  permanent residents, or U.S.-incorporated entities. Arena reports Calgary, Canada. Confirm with
  the organizer before uploading; do not sign a certification that is not true.

## Superseded generated release (2026-10-30, H-TVGB lane) — DO NOT SUBMIT

- `gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif` — the 2026-10-30 H-TVGB candidate.
  Format-valid and holdout-positive (0.1287), but 65.0% of its dots sit within 3 px of one
  competitive raster and 99.79% within 3 px of the lattice. Superseded; keep for audit, do not upload.
- `gemsass1-hvtgb-thermal-anchored-37654-20261030-zeros.tif` — the earlier packaging of the same
  lane; it failed the lane-drift gate at 79.1% (logged in `run_card_b2_duplicate_log.json`).
  Not OK to submit.

## Historical research artifacts — audit only, NOT approved

**No SWGB, H-PBSC or BGAC-1 file is approved for submission.**

- `gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif` — H-PBSC research artifact.
  Lost its holdout comparison (0.0650 vs 0.1011) and 99.48% of its dots fall within 3 px of the
  same lattice; `ok_to_submit = false`. Audit only.
- The historical SWGB TIFF is **withdrawn** (`ok_to_submit = false`): 99.87% of its dots fall within
  3 px of the same lattice. Retained for audit only.

Do not upload or re-submit the historical files. See [`knowledge/NEXT_STEPS.md`](../../knowledge/NEXT_STEPS.md)
and [`knowledge/REVIEW_2026-10-31.md`](../../knowledge/REVIEW_2026-10-31.md) for gate status,
numbers and the irregularities flagged for review.
