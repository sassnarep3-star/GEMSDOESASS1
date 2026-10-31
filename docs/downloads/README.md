# Downloads


## The generated submission (2026-10-31, H-FUSION3 lane)

**This is the file to download and submit from this release.** Verdict: **conditional —
format-clear and uniqueness-clear, but not expected to beat 0.2778.** Read the machine-built
gate table on the [executive summary](../executive-summary.html) first; it is rendered from
`evidence/`, not typed by hand.

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
gate — this is precisely what fixes the portal's “Predicted values must be in range [0, 1]”
rejection — and it is **not an exact duplicate** of any of the nine focus-site best files
(0/9, verified byte-wise; max Spearman 0.56). But it did **not** beat the champion's own field
on our holdout: HOLDOUT-DTI 0.1004 [0.0947, 0.1052] against the champion control's
0.1048 [0.0998, 0.1096], with overlapping CIs. We therefore will not claim it beats 0.2778.
The estimated live score is a **projection** (central 0.266, advisory band 0.22–0.29),
anchored on the champion's own holdout/live pair — it is not a score.

Two gates are deliberately reported as failing or unresolved rather than softened:

- the protocol's stricter lane-drift rule (≤ 70 % of dots within 3 px of one registry raster)
  fails at 0.919 — but that rule is saturated (72/72 focus-site pairs exceed it, the maximum is
  1.000, and the 0.2778 champion is itself a strict subset of GEMSDOE25's file), so no
  competitive dotted file can satisfy it;
- eligibility under the official rules §1.3 is unresolved for a Calgary-based account.

Spending a weekly submission slot remains a separate selector decision. This workspace uses 0.

---

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


- `gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif` — the 2026-10-30 release.
  Its own run card records **OK TO DOWNLOAD AND SUBMIT** (`ok_to_download_and_submit = true`,
  HOLDOUT-DTI 0.1287 [0.1231, 0.1355] vs bar 0.1011). In the *same commit*, `README.md` and
  `AGENTS.md` state that no file is approved for submission. That contradiction is a recorded
  irregularity, not something this session will silently resolve in either direction: the
  earlier decision is preserved verbatim and is for the owner to adjudicate. Verify against
  [`../evidence/thermal/run_card.json`](../evidence/thermal/run_card.json) before relying on it.
- `gemsass1-hvtgb-thermal-anchored-37654-20261030-zeros.tif` — the superseded first packaging
  of that release. Its dots failed the lane-drift gate (79.1 % within 3 px of
  `gems25-h38-greedy-credit-k3p5-20261025-18de99d38bb0-nan.tif`) and it is logged as a
  duplicate in `run_card_b2_duplicate_log.json`; `ok_to_submit = false`. Audit only.
- `gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif` — format-valid H-PBSC
  research artifact. It lost its holdout comparison (HOLDOUT-DTI 0.0650 vs bar 0.1011) and
  99.48 % of its dots fall within 3 px of the calibration lattice; `ok_to_submit = false`.
- The historical SWGB TIFF is withdrawn: 99.87 % of its dots fall within 3 px of the same
  lattice. Retained for audit only, not as an approved selector output.

Do not upload or re-submit the historical files. See
[`knowledge/NEXT_STEPS.md`](../../knowledge/NEXT_STEPS.md),
[`knowledge/hypotheses_20261031_recalldom.md`](../../knowledge/hypotheses_20261031_recalldom.md)
and [`evidence/metric_certification.json`](../evidence/metric_certification.json).

---

See [`knowledge/NEXT_STEPS.md`](../../knowledge/NEXT_STEPS.md) and
[`knowledge/RESULTS_20261031.md`](../../knowledge/RESULTS_20261031.md) for gate status, numbers and the
irregularities flagged for review.

