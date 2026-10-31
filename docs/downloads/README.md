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

## Historical research artifacts — audit only, NOT approved

**No SWGB, H-PBSC or BGAC-1 file is approved for submission.** These files stay here for
reproducibility and negative-evidence audits:

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
