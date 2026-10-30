# Ranked hypotheses — 2026-10-30 (not run)

## Decision first

**No candidate was run, and no TIFF was generated.** Three reasons, each verified:

1. **The literal uniqueness rule cannot be satisfied by a competitive-size file.** A pass needs at least 30% of a candidate's dots more than 3 px from every dot of the GEMSDOE13 calibration lattice. Only dots on the 6,649 uncovered footprint cells can be outside that halo. So a file with more than **22,163** positive pixels fails no matter what it predicts. Competitive files have 37,654–61,328 (`evidence/nine_site_board.json`, `lattice_gate_bound`).
2. **The gate cannot tell duplicates from noise.** Random placement of 37,654 dots on allowed cells overlaps the lattice at a mean of 0.9987 (seeds 1–5: 0.9985–0.9990).
3. **Eligibility is unresolved.** The user's location is Singapore. The official rules restrict eligibility to U.S. citizens and permanent residents, or U.S.-incorporated entities (§1.3). See `knowledge/sources_verified_20261030.md`.

Running a holdout experiment now would produce a result that cannot change the release decision, so the experiment budget (3 experiments, 2 hours) was not spent. No submission slot was spent.

**A parallel session's proposal, not adopted here.** `knowledge/REVIEW_2026-10-30.md` (option A) proposes a null-calibrated amendment, under which SWGB (6 px prune, HOLDOUT-DTI 0.1401) would become eligible for one selector slot after a receipt-verified check of the rules. This record does not adopt it. Eligibility under §1.3 (see above) blocks any selector slot until it is resolved, whichever uniqueness test is chosen.

## Ranking

Rank order is a qualitative priority: expected usefulness for recovering withheld surface-scarp labels per implementation cost. It is **not a score, and it is not a projection.**

| Rank | Hypothesis | Layers (cached 19-band stack, band number) | Physical signature | Non-fault process that could mimic it | Difference from prior work | Expected DTI potential / cost | Canary and gate status |
|---|---|---|---|---|---|---|---|
| 1 | **H-BASEMENT-STEP-GRAD**: a sharp basement-depth discontinuity that coincides with horizontal gradient maxima in both gravity and magnetics | `depth_to_base_surf` (15) gradient; `iso_grav_anom_hg` (18); `tmi_hg` (3); optional `det_elev_slope` (19) | Basement offset along a structure appears as a depth step, with a gravity and magnetic gradient maximum on the same line | Sedimentary basin margins and dike or intrusive contacts, which give gradient maxima without displacement | Prior work used magnetic edges and basin-bounding steps. This one requires three independent cached layers to co-locate (depth step × gravity gradient × magnetic gradient). | Unquantified. Medium uncertainty. Low cost (cached bands only, CPU). | Not implemented. Requires a per-feature leakage canary (AUC > 0.90 means leakage). Not gated by data, but gated by the literal lattice rule for any competitive-size output. |
| 2 | **H-CONDUCTIVE-STEP**: lateral conductivity contrast co-located with a basement-depth step | `cond_surf` (17) gradient; `depth_to_base_surf` (15) gradient | Fluid-saturated fault gouge or alteration can raise conductivity along a structure | Conductive sediments and clay-rich margins along basin edges | Combines electrical conductivity with depth step. Not used together in prior work. | Unquantified. Low to medium. Low cost. | Not implemented. Same canary and gate status as rank 1. |
| 3 | **H-STRAIN-EDGE**: a sign change in geodetic dilatation co-located with a slope-break lineament | `geod_dilaterate` (8) sign change; `geod_shearrate` (7); `det_elev_slope` (19) | Extensional strain sign and shear concentrate along active structures | Regional strain fields from geodetic model smoothing, which lack local structure | Geodetic strain bands are coarse. This tests whether local slope-break lines align with strain-sign boundaries. | Unquantified. Low, because the strain fields are smooth. Low cost. | Not implemented. Canary required. |
| 4 | **H-QUAKE-LINEAMENT**: earthquake density ridges aligned with slope-break lineaments | `ieq_n100a15` (16); `deq_n100a15` (10); `det_elev_slope` (19) | Microseismicity clusters along active faults | Seismicity clusters at fault intersections, geothermal fields, or mining, not at new scarps | Uses earthquake catalogue density, which is not used in the prior lanes. | Unquantified. Uncertain. Low cost. | **High leakage risk**: earthquake catalogues may correlate with the withheld labels. Canary must pass before any holdout claim. |

## Candidates from the 2026-10-29 slate, status verified this session

The 2026-10-29 slate depends on layers that are **not in the cached 19-band stack**. Here is what each needs and where it comes from. Nothing was fetched this session.

| Slate item | Layers required | Restored locally? | Source in pinned mirror (`registry/upstream_data_manifest.json`) | Obtainable here? |
|---|---|---|---|---|
| H-SCARP-ASYM | lidar `step_max`, `coh100`, `relief` | No | `external/lidar_scarp_features_u8.tif` (group `external`, 36.9 MB) | Yes, through the pinned GitHub mirror, with the hash checked. Mirror is not organizer-authenticated. |
| H-RAD-CONTACT-SCARP | `rad_K`, `rad_ThK` | No | `external/geodawn_rad_u8.tif` (26.6 MB) | Yes, mirror. |
| H-MAG-EDGE-TERMINATION | `TMI_up150` | No | `external/geodawn_extensions_u8.tif` (27.1 MB) | Yes, mirror. |
| H-STRIKE-CONTINUITY-GAP, H-RAD-QUIET-SCARP | lidar and radiometric layers above | No | as above | Yes, mirror. |

The original USGS and ScienceBase sources are **not** on this sandbox's outbound allowlist (only GitHub, npm and PyPI hosts are). The mirror is the only route.

## Top hypothesis: holdout validation status

**H-BASEMENT-STEP-GRAD has not been validated on the spatially blocked holdout.** The protocol needs (a) a pre-registered feature transform, (b) the leakage canary, and (c) the shared evaluator run against an incumbent on identical folds. None of these was done. The reason is in the decision section above, not a technical blocker. No submission slot was spent.

## Next step, if the user decides the policy

1. Pre-register rank-1 with the exact transform and the non-fault mimic.
2. Restore `data/official` and `.cache/features` from the pinned mirror (`scripts/prepare_data.py`, about 421 MB).
3. Run the single-feature canary on each of the three layers.
4. Run the holdout against the 0.2600 family incumbent on the same folds, using `vendor/gems57/evaluate_holdout.py`.
5. Only a candidate that passes the canary and beats the incumbent, and that clears the uniqueness policy and the eligibility check, goes to the separate slot selector.
