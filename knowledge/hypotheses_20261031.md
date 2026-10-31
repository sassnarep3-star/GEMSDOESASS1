# Preregistered hypotheses and lane — 2026-10-31 (written BEFORE any experiment in this session)

Session mandate: *"generate 3–5 candidate geological hypotheses we haven't tried yet, each naming:
the specific layer(s) involved, the physical signature being targeted (e.g., an edge-detection or
curvature transform), why it should catch a fault missing from the USGS/INGENIOUS catalogue rather
than one already in it, and how it differs from anything already implemented in this repo. Rank them
by expected DTI improvement and implementation cost. Validate the top candidate on our
spatially-blocked holdout set before touching a weekly submission slot."*

This file is the lane for this session (PARALLEL-RUN PROTOCOL §1). Every feature is label-free at
construction time; catalogue-derived features are computed from VISIBLE faults only per fold (the
shared hide-and-recover evaluator, `GEMSASS1-HR-v2-segment`). No number below is a score.

## 0. Why a *new* family is required (evidence recap, all previously measured)

- All 12 files ≥ 0.24 OWNER-REPORT across the nine focus sites are ≥ 97.5 % within 3 px of the
  GEMSDOE25 `dotted-h19-5-d2-8` raster (0.2600): **one field, one family**
  (`evidence/nine_site_board.json`, `knowledge/01_why_0p2778_and_what_beats_it.md`).
- The 0.2778 champion is that field with 6,436 near-catalogue dots removed (symmetric difference 0,
  measured 2026-10-30). **Emission tricks on H19-5 are exhausted**; beating 0.2778 needs a field
  whose top ~38 k pixels carry more kernel credit, especially far-field (hidden truth habitat:
  median dot-to-catalogue distance 19.6 px for the champion vs 5.8 px for the live-0.0742 flank file).
- The only locally-proven instruments above the family base (HOLDOUT-DTI bar 0.1011) are
  segment-withheld supervised learners (E2-SWGB 0.1586; H-TSFX 0.1587; H-TVGB 0.1287). Their plain
  2 px-pruned dots collided with the GEMSDOE25 family at 70.2–72.3 % (H-TSFX stop) because the
  learned field ranks the same prominent lidar scarps. **A new field must rank *different*
  structures**, and the shipped emission must live in the far-field habitat.

## 1. New hypotheses (none of these transforms exists anywhere in this repo or in the 414-raster registry)

Ranked by expected HOLDOUT-DTI improvement × implementation cost. Each was *registered but not run*
in earlier slates (`knowledge/hypotheses_20261030.md` H-BSTEP / H-CONDUCTIVE-STEP / H-STRAIN-EDGE /
H-QUAKE-LINEAMENT / H-RELAYPOL — none was ever implemented as a transform; H-TSFX used the raw 19
bands as separate learner features and measured no gain, +0.0088 [−0.0018, +0.0194]).

| rank | id | layer(s) | physical signature (transform) | why it catches *uncatalogued* faults | how it differs from everything already implemented | expected gain / cost |
|---|---|---|---|---|---|---|
| **1 (LANE)** | **H-BSTEP-CONCORD** | `depth_to_base_surf` (band 15), `iso_grav_anom_hg` (18), `tmi_hg` (3) of the GeoDAWN/derived 19-band stack | **edge-detection + co-location**: per-layer gradient-magnitude ridge strength (σ = 2–5 px), then the three-way coincidence product `ridge_step · ridge_grav · ridge_mag` (and pairwise geometric means) | basement-rooted normal faults under basin fill show a depth step with gravity- and magnetic-gradient maxima on one line; Qfaults maps through-going Holocene *surface* traces and misses short, buried, or alluvium-mantled segments that still carry a lidar scarp | H19-5 is lidar openness only; H-TSFX fed raw bands to the learner and never built coincidence transforms; GEMSDOE36 modulated H19-5 with a conduit; no registry raster uses basement/grav/mag edge concordance | high / low-medium |
| 2 | **H-RELAYBRIDGE** | `lidar_face_asym`, `lidar_strike*`, `lidar_coh100`, `lidar_step_max` (lidar scarp stack) | polarity-flip geometry: along-strike facing-asymmetry sign reversals (`gm(|asym|) − |gm(asym)|`) × strike concordance × cohesion — the surface expression of relay ramps between overlapping normal-fault segments | relay ramps and step-over zones are systematically under-mapped at 1:250 k and are the loci of segment linkage and palaeo-rupture; the lidar truth set contains them | H-TSFX folded four *single* polarity features into the learner; no lane used the flip×concordance product; GEMSDOE33's tip-stepover file used their own analog data | medium-high / low |
| 3 | **H-CONDUCTIVE-GOUGE** | `cond_surf` (17), `depth_to_base_surf` (15) | conductivity-edge × basement-step conjunction: `gm(cond_surf) · ridge_step` | fluid-saturated fault gouge and argillic alteration raise conductivity along permeable fault zones that never broke the surface cleanly; Qfaults misses them | the conductivity band was in H-TSFX as a raw feature; the conjunction transform is new; GEMSDOE76's tilt-thermal family never used conductivity edges | medium / low |
| 4 | **H-STRAIN-BOUNDARY** | `geod_dilaterate` (8), `geod_shearrate` (7), `det_elev_slope` (19) | curvature/edge on the strain field: dilatation-gradient ridges (sign-change lines) × shear-rate ridges × slope-break lineaments | strain compatibility boundaries localise distributed off-catalogue deformation where discrete scarps are too subtle to map | H-TSFX used raw strain bands; the sign-change-line transform is new | low-medium / low |
| 5 | **H-QUAKE-CURV** | `ieq_n100a15` (16), `deq_n100a15` (10), `det_elev_slope` (19) | earthquake-density curvature ridges (gradient of Gaussian-smoothed density) aligned with slope-break lineaments | microseismicity clusters on blind faults with no surface rupture in the catalogue | raw quake-density bands were in H-TSFX; the curvature-ridge transform is new. **Highest leakage risk** (seismicity catalogues can correlate with labels) — the canary must pass before any holdout claim | low-medium / low |

Non-fault process that could mimic every candidate (named per protocol): **pluvial shoreline
benches and fluvial terrace risers** (coherent, low-relief, contour-parallel, and they follow
basin margins where basement steps and conductivity contrasts also live), plus road/canal
embankments and basaltic vent rims. A three-way *coincidence* of independent potential-field edges
is the discriminator: shorelines produce topographic edges without basement or magnetic response.

## 2. Lane paragraph (this session's single method)

**H-BSTEP-CONCORD / H-BSL (basement-step concordance learner).** A segment-withheld supervised
recovery learner (HistGradientBoosting, the E2-SWGB hyper-parameters: 250 iterations, lr 0.08,
31 leaves, min leaf 100, L2 1.0) trained on the shared hide-and-recover folds
(`GEMSASS1-HR-v2-segment`, 5 folds, whole segments + 3 px buffer withheld, catalogue features from
VISIBLE faults only) with the feature set: 28 static lidar/GeoDAWN layers + 4 visible-catalogue
context features + the 19 raw derived bands (as in H-TSFX) + the nine new concordance transforms of
§1 (ranks 1–5 combined; the paired attribution of each transform is the E2 ablation's job later —
this lane's budget is 3 experiments). Emission: isolated dots at spacing 2.8 px with a
**preregistered catalogue exclusion of 600 m (> 6 px) at emission** (the far-field habitat cell:
the champion's dots sit median 19.6 px from the catalogue and the live metric masks known-fault
pixels, so any dot within 600 m of the catalogue is mostly re-trace risk), n = 37,654 dots (the
only live-evidenced count). If the plain emission trips the per-raster lane-drift dots gate
(> 70 % within 3 px of one comparable registry raster), the **preregistered anti-collision
emission** replaces it: identical greedy Poisson-disk priority over `allowed ∧ ¬halo₃px(R*)`,
where R* is the union of dots of the *offending* rasters only, with a deterministic fallback that
refills from `allowed` by field rank if the exclusion starves n_dots; both variants are scored and
the gate is re-measured, never silently steered. Final packaging uses a **single full-catalogue
model** (all catalogue segments as positives, full-catalogue context — the proper live field,
fixing H-TSFX irregularity 3) through the shared fail-closed writer (zeros outside footprint —
the fix for the portal's "Predicted values must be in range [0, 1]" rejection).

## 3. Preregistered protocol (frozen before running)

* **Evaluator:** `GEMSASS1-HR-v2-segment` (shared `src/gems/holdout.py`) — pooled DTI α=0.2 β=0.8,
  300 m triangular kernel, 50 px tile-bootstrap 95 % CI. Labels: every number is HOLDOUT-DTI
  (evaluator, withheld positives, CI) or OWNER-REPORT. **A projection is never written as a score.**
* **Bar to beat:** 0.1011 [0.0956, 0.1072] (the 0.2600 family base on the same evaluator).
  Repo incumbent: 0.1586 [0.1519, 0.1649] (E2-SWGB) / 0.1591 (sweep best). Holdout-pass is
  necessary, not sufficient (holdout-live Spearman −0.081 across 17 registry rasters).
* **E1 (experiment 1):** canary (every feature alone vs fold-0..4 withheld truth; single-feature
  AUC > 0.90 ⇒ leakage ⇒ stop) + the lane field at the *comparable* operating point (n = 37,654,
  2.8 px, > 2 px catalogue exclusion — same cell as every prior protocol number).
* **E2 (experiment 2):** emission sensitivity on the saved E1 fields: {2 px, 6 px} × {37,654,
  44,090} plus the anti-collision variant at the shipped cell. Reported as sensitivity; the
  shipped cell is fixed a priori at 37,654 / 2.8 px / > 6 px (§2). Pooled + far-field (> 5 px from
  visible) HOLDOUT-DTI per cell; max per-raster 3 px overlap vs the 17-file competitive registry.
* **E3 / package (experiment 3):** single full-catalogue model → shipped-cell emission → surface
  novelty scan (before placement) and dots novelty scan (after placement) against the complete
  frozen 414-raster registry (`registry/focus_inventory.json`, complete_within_scope required) +
  every prior repo TIFF; AMEND-LATTICE-01 (the 5 px calibration-lattice fixture is measured and
  reported in the run card as IR-LATTICE-01 but exempted from the overlap gate — without this
  exemption the 0.2778 champion itself is "a duplicate of" a 0.0904 grid; both readings printed)
  and AMEND-N2 (nonfinite published priors compared with nonfinite = 0 support); fail-closed
  writer; format validator (single-band float32, CRS/shape/transform == template, values in [0, 1]
  everywhere, no NaN anywhere, no positive outside footprint); run card.
* **Lane-drift rule (protocol §1):** ρ > 0.90 or > 70 % of dots within 3 px of ONE comparable
  registry raster ⇒ duplicate ⇒ log and stop. Checked on the surface before placement AND on the
  final dots. Incompatible-grid fixture (`GEMSDOE36 …FORMAT_TEST…`) excluded as unassessable by
  grid, never silently.
* **Budget:** 3 experiments / 2 h, tracked in `evidence/bstep/budget.json`. No competition slot is
  spent here (promotion to a slot is the separate selector step; this workspace never uploads).
* **Data:** the restored, sha256-pinned stack (19-band derived stack + lidar/GeoDAWN u8 stacks +
  bridge rasters + GDR point CSVs; `evidence/data_receipt.json`, owner-mirror provenance — NOT
  organizer-authenticated). No new external data is needed; every source is the pinned GitHub
  mirror of the organizer-packaged competition data and the USGS GeoDAWN release
  (doi:10.5066/P93LGLVQ, cited in the sidecars).

## 4. Irregularities flagged for review

1. **IR-LATTICE-01** stays open as a *policy* item; this lane runs under AMEND-LATTICE-01 and
   prints both readings in the run card (see §3). The user's 2026-10-31 mandate ("it needs to pass
   certain high scoring validation gates before confirming whether a file is unique and can be
   submitted") is recorded as the direction of travel: automated gates, machine verdict.
2. **Eligibility (rules §1.3, U.S. persons/entities).** Arena reports the user's location as
   Calgary, Alberta, Canada; earlier sessions recorded Singapore. Either way it is outside the
   stated U.S. eligibility. This lane generates and validates a file but **never uploads**;
   confirming eligibility with the administrator is a user decision before any submission.
3. **Leaderboard figures conflict** (0.4413 / 0.3195 / 0.4544 snapshot 2026-10-30). All live
   numbers remain OWNER-REPORT until an organizer receipt exists.
4. `labels.tif` is byte-identical to `existing_faults.tif` in the owner mirror; holdout truth is
   therefore catalogue-derived, and HOLDOUT-DTI is hide-and-recover evidence, never a live score.
