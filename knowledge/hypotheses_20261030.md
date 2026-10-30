<!-- Two parallel sessions wrote this filename on 2026-10-30; both records are kept verbatim. -->
<!-- Part 1: H-TVGB lane (thermal-vent slate, ran E1/E2/E3 + release). -->
<!-- Part 2: parallel H-GDR-CONDUIT-OFFCAT session (no experiment run; different conclusions). -->

# Candidate slate — 2026-10-30 (preregistered before any experiment in this session)

Session prompt focus: *"heavy and deep research into … the scientific discovery of geothermal vents …
find sources of data that others are over looking … come up with new hypothesis to test."*
All five candidates below use **label-free geothermal-indicator data** that no lane in this repo has
ever touched, and only two of the 414 registry rasters (nine focus sites) name geothermal inputs at
all (`gems24-gvc1-negative-geothermal-lineament-submod`, 0.0859 OWNER-REPORT, which *vetoed*
geothermal lineaments and sits 5.7 px from the catalogue; `gemsdoe36-anderson-geothermal-pinn`,
0.2750 OWNER-REPORT, which used a "GDR geotherm conduit" only as a modulation of the H19-5 champion
field). Every number in this file is a **data measurement [measured-here]** or explicitly labelled.

## Data inventory (all fetched and sha256-verified this session from the pinned owner mirrors)

| layer | rows in footprint | source (official) | label-free? |
|---|---|---|---|
| Wells & spring temperature/chemistry (thermalclass Hot 1,006 unique / Warm 2,245 rows; geothermometer T up to 296.5 °C) | 27,092 rows / 12,975 unique sites | GDR 1391, DOI [10.15121/1881483](https://doi.org/10.15121/1881483), CC BY 4.0 | yes — the `dist_known_fault_px` column is **label-derived and is excluded from every feature** |
| INGENIOUS 2 m temperature probes (`2mDAB` anomaly above local background; max 54.7 °C, p90 3.4 °C) | 3,800 stations | GDR 1391 (UNR/GBCGE), same DOI | yes |
| Paleo-geothermal deposits (Travertine 258, Tufa 146, Sinter 95 + silicified/alteration/explosion-crater/Sulfur) | 709 regional / **402 in footprint** | GDR 1391 Paleo-Geothermal Features | yes |
| Quaternary volcanic vents (Basalt 20, Rhyolite 1) | 21 | GDR 1391 | yes |
| Qfaults trace attributes (slip rate, recency, slip sense) | 1,000+ segments | GDR 1391 INGENIOUS traces | catalogue geometry is NOT used as a label; attributes are catalogue-side context only |
| Lidar scarp stack (step_max, coh100, dipole, …) + GeoDAWN K/Th/U/TC + TMI-up150 | 28 static features | USGS GeoDAWN doi:[10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ) | yes |

## Why a geothermal prior should find *uncatalogued* faults

Great Basin hydrothermal systems are structurally controlled: meteoric water circulates along
Holocene normal-fault damage zones and discharges as warm springs, sinter/travertine mounds and
shallow heat-flow anomalies (the Beowawe–Steamboat–Brady's corridor is the type example). A fault
segment can therefore carry a **surface geothermal expression** (spring alignment, sinter terrace,
2 m temperature anomaly) even where the USGS/INGENIOUS Qfaults compilation never mapped the scarp —
either because the segment is short, alluvium-buried, or mapped only at 1:250k. The hidden 1 m lidar
label set is known [measured-here, knowledge/01] to sit a **median ~2 km from the catalogue** (the
0.2778 champion's dots), i.e. in exactly the basin-interior/piedmont habitat where unmapped
hydrothermal structures live. The named **non-fault mimic** for all candidates: pluvial shoreline
benches and fluvial terrace risers around thermal basins (they are coherent, low-relief and
contour-parallel), plus road/canal embankments and basaltic vent rims.

## Ranked slate (expected HOLDOUT-DTI improvement × implementation cost)

| rank | id | layers | physical signature | why uncatalogued (not a re-trace of Qfaults) | how it differs from everything already implemented | expected gain / cost |
|---|---|---|---|---|---|---|
| **1 (LANE — run this)** | **H-TVGB geothermally-anchored supervised recovery** | 28 static lidar/GeoDAWN layers + visible-only catalogue context + **new thermal family** (log-distance to hot/warm spring & geothermometer-positive well clusters, paleo sinter/tufa/travertine proximity, vent proximity, 2 mDAB probe-anomaly raster, anchor-cluster density, along-strike anchor alignment cos2) | the joint morpho-geophysical signature of *withheld* fault segments **conditioned on geothermal expression**: a scarp pixel whose along-strike projection meets a thermal anchor cluster ranks above an identical scarp without one | geothermally active segments are Holocene-active and lidar-mapped but under-mapped in Qfaults; anchors are external point data, not catalogue geometry | SWGB (this repo) trained the same learner **without** any thermal feature and reached HOLDOUT-DTI 0.1586; GEMSDOE36's anderson file used geotherm conduits only to modulate the H19-5 field (0.2750 live, margin +0.002 on their own LM holdout); GEMSDOE36's hvg36 "vent-dipole OOF ensemble" was a dipole-ensemble flavour (their receipt: HOLDOUT-DTI 0.1358 vs 0.1332 base, NEGATIVE) — none put a thermal family inside a segment-withheld learner | **high** (only locally-proven instrument that beats the 0.1011 bar) / medium |
| 2 | **H-TVR pure thermal-anchor scarp field** (ablation of rank 1, no learner) | lidar step/coh/dipole × thermal-anchor alignment & density | rule-based scarp × anchor-alignment conjunction | same as above | no registry raster is a thermal-anchored rule field; GEMSDOE24's gvc1 *vetoed* geothermal lineaments | medium / **low** |
| 3 | **H-PROBE heat-flow corridor** | 2 mDAB probe raster (σ=3 px Gaussian), lidar step_max/coh100 | coherent scarp crossing a shallow-temperature anomaly corridor | shallow heat marks permeable fault zones that never reached the mapping scale | no lane used the INGENIOUS probe network; GEMSDOE19's "thermal-pop" was a spring-*population* count on the H19 field, not a probe-anomaly raster | medium / low |
| 4 | **H-SINTER-DEPOSIT margin scarp** | paleo deposit buffers (1–3 px), lidar dipole/asymmetry | scarp at the margin of sinter/travertine mounds (paleo upflow zones) | fossil vent systems sit on unmapped structures; deposits themselves are not faults | no registry raster references the paleo compilation | low–medium / low |
| 5 | **H-QFAULT-ATTR tip propagation** | Qfaults slip-rate/recency attributes × lidar step/coh | continuation of high-slip-rate trace ends (≥0.1 mm/yr, <16 ka recency) into lidar scarps beyond the mapped trace | the catalogue raster records the *mapped extent*; continuations beyond tips are by construction uncatalogued | BGAC used only catalogue distance; no lane used slip-rate/recency attributes | low–medium / medium |

## Preregistered experiment (frozen before running)

* **Evaluator:** `GEMSASS1-HR-v2-segment` (shared `src/gems/holdout.py`) — whole fault segments
  withheld with 3 px buffer; every catalogue-derived feature computed from VISIBLE faults only;
  pixel-exact visible-fault masking; pooled DTI α=0.2 β=0.8 300 m triangular kernel; 50 px
  tile-bootstrap 95% CI. This is the prompt's "spatially-blocked hide-and-recover" design
  (segment-level blocks, not pixel splits).
* **Bar to beat:** 0.1011 [0.0956, 0.1072] HOLDOUT-DTI (0.2600 family base). Repo incumbent to beat
  for `promote`: SWGB 0.1401 [0.1329, 0.1452] (emitted) / 0.1586 (raw field).
* **E1 (experiment 1):** H-TVR pure rule field (rank-2 candidate) at n=37,654, spacing 2.8 px,
  >2 px catalogue exclusion on `fd.active` — the champion operating point.
* **E2 (experiment 2):** paired ablation on identical folds/seeds: H-TVGB (28 static + context +
  thermal family) vs SWGB reproduction (same learner, thermal family removed). Promote criterion
  for the thermal family: paired Δ HOLDOUT-DTI > 0 with non-overlapping CIs or paired-tile CI
  excluding 0.
* **E3 (experiment 3):** emission sweep on the winning field:
  n ∈ {37,654, 44,090, 52,000} × prune ∈ {2 px, 6 px} at spacing 2.8 px. **Selection rule
  (amended 2026-10-30, before any run):** the *shipped* config is fixed at the live-evidenced
  champion operating point (n = 37,654, spacing 2.8 px, > 2 px catalogue exclusion at emission) —
  the only live evidence on emission is the champion ladder (0.2600 → 0.2708 → 0.2778 came purely
  from pruning near-catalogue dots), and holdout truth sits near visible faults (the opposite of
  the live regime), so holdout ranking of prune width is anti-correlated with live. The sweep is
  measured as sensitivity evidence; any config beating the shipped one on holdout is reported for
  the separate selector step. Then final build on the FULL catalogue (no holdout masking) + writer.
* **Leakage canary:** every feature alone → AUC on fold-0 withheld truth; AUC > 0.90 = leakage
  until proven otherwise. The `dist_known_fault_px` column is excluded at load time and the canary
  is expected to catch any accidental reintroduction (distance-to-catalogue features are computed
  from VISIBLE faults per fold only).
* **Novelty:** surface scan (exact rank Spearman) **before placement** and dot scan (directed 3 px
  overlap) **after placement** against the full frozen 414-raster registry + this repo's prior
  files; thresholds unchanged (ρ > 0.90 or overlap > 70 % ⇒ lane-drift duplicate ⇒ stop).
  The 13gems calibration-lattice obstruction (IR-LATTICE-01) is reported explicitly for every
  candidate, never silently omitted — see the amendment drafted in `evidence/thermal/`.
* **Budget:** 3 experiments / 2 h. No weekly submission slot is spent here (promotion to a real
  slot is a separate selector step).

## Irregularities flagged for review

1. **IR-LATTICE-01 (open policy item):** the registry contains superposition *calibration grids*
   (e.g. `13gems_20261001_r13-lattice-s5_v2`, itself a 0.0904 submission) whose dot sets tile the
   footprint at ~5 px. Measured 2026-10-27/28: any competitive-size dotted raster has ≥ 99 % of its
   dots within 3 px of that one file. The literal "≤ 70 % vs ONE registry raster" rule is therefore
   unsatisfiable for every dotted submission, including the 0.2778 champion itself. Resolution
   demanded by `knowledge/NEXT_STEPS.md` item 4; this session drafts the versioned amendment in
   `evidence/thermal/lattice_amendment.md` and reports both readings for every artifact.
2. **Owner-reported scores only.** No organizer receipt exists in this group; the user-prompt
   leaderboard values conflict (0.4413 vs 0.3195 "highest right now"). All historical scores in the
   executive table are OWNER-REPORT.
3. **Label-derived column** `dist_known_fault_px` exists in the GDR CSV mirrors; it is excluded
   from every feature and named in the canary audit.

---

# Part 2 — parallel-session record (preserved verbatim, not adopted)

The following is the other 2026-10-30 session's document for the same filename. Its conclusions
differ from Part 1; both are kept without editing. Note especially its eligibility finding
(rules §1.3, U.S. persons/entities) and its lattice-bound argument.

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
