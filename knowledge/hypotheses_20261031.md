# Preregistered hypotheses — 2026-10-31 (two parallel lanes)

Two sessions preregistered hypotheses on 2026-10-31 before running any experiment in their own
lane. Both preregistrations are preserved verbatim below. Lane H-KDAM merged earlier the same day
(PR #28–31); lane H-BSTEP is the current release.

---

# Lane H-BSTEP preregistration (current release lane) — written BEFORE any experiment in its session

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

---

# Lane H-KDAM preregistration (merged earlier, 2026-10-31) — preserved verbatim

# Pre-registration — 2026-10-31 session (lane H-KDAM)

Written **before** E1/E2 were run (feature construction is label-free and was executed first; no
holdout score, emission or submission existed at the time this file was written). Any edit after the
first run must be appended below the line as an amendment with a timestamp, never silently rewritten.

## What the official sources actually say (verified this session)

| Item | Fact | Source |
|---|---|---|
| Task | Predict faults; experts hand-labelled *new* faults not in the USGS database; those are the test set | [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| Metric | Distance-weighted Tversky, `TP_w/(TP_w + α·FP_w + β·FN_w + ε)`, **α = 0.2, β = 0.8**, triangular kernel `(1 − d/R)₊`, **R = 300 m = 3 px** | same page, "Mathematical representation" |
| Soft values | Predictions are *"pixel-wise probabilities or confidence scores between 0 and 1"*; `TP_w` takes `max_x p(x)k(d)` and `FP_w` sums `p(x)[1 − max k]`, so fractional values are scored fractionally | same page |
| Known faults | *"Pixels corresponding to known USGS/INGENIOUS faults are masked / excluded from evaluation"*, in both rounds (DrivenData staff, 2026-09-16) | [forum 11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) |
| Format | single-band float32, EPSG:32611, 100 m, same bounds, values in [0,1], outside null/NaN | [submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| Live board | #1 **0.4544** (xiaofanhu), #2 0.3934, #3 0.3917 at read time 2026-10-31 | [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) |

Consequence for every hypothesis below: because known-fault pixels are masked, (a) mass placed on or
adjacent to the catalogue can only cost, and (b) recall of *unmapped* faults is the whole game. That is
the arithmetic behind the champion family (0.2600 → 0.2708 → 0.2778 came from deleting dots close to
the catalogue, not from a better field).

## Why the champion scored 0.2778 (re-derived, not quoted)

`gemsdoe32-h33-h33-2-b2-…-zeros.tif` is `gems25-dotted-h19-5-d2-8` (0.2600, 44,090 dots) with the dots
within 2 px of the catalogue removed: 44,090 − 6,436 = 37,654, symmetric difference 0 (measured in a
previous session, `knowledge/RESULTS_20261030.md`). Under the official formula a masked catalogue means
those 6,436 dots contributed FP mass and no TP credit. Solving
`TP/(TP + 0.2·FP + 0.8·FN) = 0.2778` after removing 6,436 FP units gives an implied `TP_w ≈ 5.2 × 10³`
weighted truth pixels of credit. **Every file at ≥ 0.24 in the nine focus sites is the same field**
(`evidence/swgb/registry_family_overlap.json`), so beating 0.2778 requires a different field, not
another prune of this one.

## The five hypotheses (ranked by expected DTI gain per unit cost)

| # | Hypothesis | Layers / transform | Why it should find faults the catalogue misses | Differs from this repo how | Cost |
|---|---|---|---|---|---|
| 1 | **H-KDAM** damage-zone alteration × potential-field contacts | K, Th, K/Th; spectral vertical derivative, tilt derivative, theta map, upward-continued HGM; multi-scale structure-tensor persistence; cross-instrument orientation agreement | Fault damage zones are hydrothermal fluid pathways: K is mobile and leached, Th is immobile, so `K/Th` drops in a halo around the damage zone while a magnetic contact/lineament marks the basement structure underneath. A concealed fault can show both while showing no lidar scarp (its scarp is buried or eroded), which is exactly the class missing from the USGS/INGENIOUS map | Every previous local lane fed *raw* bands and lidar scarp channels to a learner. No lane has used immobile-element-normalised depletion, spectral potential-field derivatives, or a two-instrument orientation-agreement term | **run** |
| 2 | H-STRKIN strain-kinematics coupling (dilatation × shear-strain-rate × fault strike residual) | competition strain-rate layers (login-walled here) | secondary/kinematic linkage of unmapped faults | prior lanes used strain only as raw learner features | blocked: `training_features.tif` needs DrivenData login |
| 3 | H-SOFTEMIT soft-probability emission | any field, emitted as graded values inside a support instead of binary dots | the official metric scores fractional values fractionally; graded values can buy credit where a binary dot would pay full FP | every registry file is binary dots or a dense binary-ish field | **run** as E2/E3 diagnostic on the same field (cheap, paired) |
| 4 | H-CURV multi-scale curvature/relief-hierarchy on the 1 m DEM | 3DEP 1 m DEM via `1m_DEM_links.csv` (login-walled list; public AWS/USGS tiles exist) | flexural/uplift signature of blind faults | previous DEM use is the pre-aggregated `lidar_scarp_features` only | blocked: link list login-walled; **not** proposed as viable until the free source is checked |
| 5 | H-SEISREL relocated-seismicity depth projection | ANSS/USGS catalogue | faults active but unmapped | prior lanes use raw seismicity density | low expected gain (catalogue sparse in the footprint); not run |

Only #1 (and its #3 emission variant) is run in this session: the budget is three experiments.

## Frozen design (no post-hoc changes)

- Feature block: `src/gems/kdam.py`, 19 label-free features (`STATIC_NAMES`) + 3 catalogue-derived
  features computed from the **visible** faults only (`dist_vis`, `dens_vis`, `tip_vis`).
- Learner: `HistGradientBoostingClassifier(max_iter=200, lr=0.06, leaves=31, min_leaf=40, l2=1.0)`,
  120,000 sampled negatives per fold, class weights balancing to the positive count.
- Folds: the shared `src/gems/holdout.py` `GEMSASS1-HR-v2-segment` evaluator, 5 whole-segment folds,
  3 px buffer, pooled DTI, block bootstrap CI. Nothing forked.
- Emission (champion operating point, so density cannot explain a difference): Poisson disk,
  **37,654 dots, min distance 2.8 px, catalogue prune 2 px**.
- **E1** = protocol emission. **E2** = the same field and the same operating point with one extra
  constraint: a dot must be **> 4 px from every positive pixel of the pinned 489-raster registry**
  (synthetic `inputs/calibration/*lattice*` fixtures and the explicit 32×48 FORMAT_TEST file exempt;
  recorded in `evidence/kdam/registry_union.json`). This is declared *before* seeing its score and is
  the novelty-by-construction rule. Its cost is reported as a paired delta, not hidden.
- Success bars: E1 must beat the 0.1011 family bar; E2 must stay above the bar and its max 3 px
  overlap against every competitive registry raster must be ≤ 0.70 and its Spearman ≤ 0.90.
- Budget: three experiments (E1, E2, final) and two hours.
- `verdict = promote` requires: validator pass from bytes, novelty gate pass, and E2 above the bar.
  Anything less is `negative` and stays out of `docs/downloads/`.

## Irreducible caveat stated before the numbers exist

Across 17 rasters the rank correlation between this holdout and the live leaderboard is −0.08
(`knowledge/RESULTS_20261030.md`). A holdout number is therefore **not** a leaderboard forecast, and
no projection is written as a score anywhere in this session's output.

---


*Below: the H-TIPRELAY lane preregistration (parallel session, merged after H-KDAM).*

# Candidate slate — 2026-10-31 (preregistered BEFORE any experiment in this session)

Session directive (user): *"generate 3–5 candidate geological hypotheses we haven't tried yet …
Rank them by expected DTI improvement and implementation cost. Validate the top candidate on our
spatially-blocked holdout set before touching a weekly submission slot."* Prior-session directive
this session executes first (`knowledge/NEXT_STEPS.md` Part 1 item 4): *(a) add tip/step-over
geometry and orientation-persistence features and re-run the paired ablation; (b) raise far-field
credit; (c) re-test the geothermal family as an EMISSION prior.*

**LANE (frozen single method paragraph).** H-TIPRELAY — continuation-geometry-supervised recovery:
the H-TVGB thermal-anchored segment-withheld HistGradientBoosting learner (the only locally-proven
instrument above the 0.1011 HOLDOUT-DTI bar) augmented with three new VISIBLE-only catalogue-geometry
feature families — (1) **tip-relay corridors**: opposing visible skeleton endpoints whose
along-strike projections meet across an uncatalogued gap; (2) **step-over / relay-ramp gaps**:
pixels 2–8 px off the visible trace that sit between two visible strands offset 15–45° in strike;
(3) **strike persistence**: local circular resultant of the visible-fault strike field (straight,
persistent traces continue beyond their mapped tips more often than erratic ones) — plus a
**far-field training-emphasis arm** (positives > 500 m from visible faults weighted ×3), emitted at
the live-evidenced champion operating point (n = 37,654 dots, 2.8 px Poisson spacing, > 600 m
catalogue exclusion at emission); the geothermal-anchor **emission prior** is tested as a paired
emission ablation. Everything is scored on the shared `GEMSASS1-HR-v2-segment` holdout and gated by
the 414-raster registry novelty scan before packaging. Shared tools reused, never forked:
`src/gems/holdout.py`, `src/gems/metric.py`, `src/gems/features.py`, `src/gems/emission.py`,
`src/gems/thermal.py`, `src/gems/submission.py`, `vendor/gems57/submission_writer.py`,
`scripts/novelty.py`. All output goes to `evidence/tiprelay/`.

## Why continuation geometry should find *uncatalogued* faults

Faults grow by tip propagation and link through relay ramps and step-overs. The USGS/INGENIOUS
catalogue records *mapped* traces; propagation tips, buried continuations and linking structures
between two mapped strands are systematically under-mapped (short, alluvium-covered, or below
1:250k mapping scale). The 0.2778 champion's hidden-truth habitat measured in this repo
(`knowledge/01_why_0p2778_and_what_beats_it.md`) sits at a **median ≈ 2 km (≈ 20 px) from the
catalogue** — exactly where a relay corridor between two mapped strands, or the continuation beyond
a single tip, lands. No registry raster (nine focus sites, 414 files) names tip-relay, step-over-gap
or strike-persistence *learner features*; the only previous use of tip geometry in this repo was
GEMSDOE32's `h32-1-prethin-tip-euler` family (OWNER-REPORT 0.2649 live) and this repo's BGAC lane
(distance-to-catalogue only). **Named non-fault mimics:** pluvial shoreline benches and fluvial
terrace risers (straight, coherent, can bridge between two scarps), canal/road embankments,
magma-dike margins (persistent strike).

## Ranked slate (expected HOLDOUT-DTI improvement × implementation cost)

| rank | id | layers | physical signature | why uncatalogued (not a Qfaults re-trace) | how it differs from everything already implemented | expected gain / cost |
|---|---|---|---|---|---|---|
| **1 (LANE — E1)** | **H-TIPRELAY-GEOM** tip-relay + step-over + strike-persistence learner features | visible-catalogue skeleton/tips/strike (per fold, visible-only) × existing 28 lidar/GeoDAWN layers | two facing visible tips whose along-strike rays meet across a gap; 2–8 px relay-ramp gaps between offset strands; persistence-weighted tip continuations | the gap between two mapped strands and the ground beyond a tip are by construction unmapped; hydrothermal systems preferentially exploit these young linking structures | registry has tip-*euler* *rule* files (GEMSDOE32) but no learner feature family; BGAC used plain catalogue distance only; no repo lane used skeleton endpoints or doubled-angle resultant length | **high** (targets the champion's far-field habitat directly) / medium |
| 2 (E1 arm C) | **H-FFEMPH** far-field positive emphasis | same learner; training positives > 500 m from visible faults weighted ×3 | same field, re-balanced decision boundary toward the live regime (live truth sits far from catalogue; holdout truth concentrates near visible faults) | unchanged — this is a loss re-weighting, not a new source | no prior lane re-weighted by visible-fault distance; previous lanes only *measured* far-field DTI | medium / low |
| 3 (E2) | **H-TH-EMIT** geothermal-anchor emission prior | H-TIPRELAY winner field × thermal-anchor density rank at emission only | dots preferentially occupy hydrothermal corridors (warm springs, 2 m probe anomalies, sinter) along candidate traces | anchors are external GDR point data, not catalogue geometry | NEXT_STEPS 4c; the 2026-10-30 lane tested geothermal anchors as *learner* features (paired Δ −0.0124, negative) but never as an *emission* prior | medium-low / low |
| 4 | **H-QFAULT-ATTR** slip-rate/recency-weighted tip continuation | `data/external/qfault_attributes.csv` (slip rate, recency) × tip-continuation corridors | continuation beyond tips of high-slip-rate (< 16 ka) traces ranks above continuations of quiescent ones | attributes are trace-side metadata; the continuation itself is unmapped | registered 2026-10-30 (rank 5), still never run in this repo | low–medium / medium |
| 5 | **H-RADON-CONCORD** radiometric-lineament concordance | K/Th/U/TC gradient rasters (existing) integrated along candidate strike (Radon-style) | scarp strike agreeing with a radiometric gradient lineament | radiometric lineaments follow buried structures lidar cannot see under playa cover | flagged: registry contains Radon-*rule* submissions (GEMSDOE74/75, live 0.0669/0.1627 OWNER-REPORT); lane-drift check mandatory before any run | low–medium / medium–high |

## Preregistered experiments (frozen before running)

* **Evaluator:** shared `GEMSASS1-HR-v2-segment` (whole segments withheld, 3 px buffer, visible-only
  catalogue features, pooled DTI α=0.2 β=0.8 300 m triangular kernel, 50 px tile-bootstrap CI).
* **Bar:** HOLDOUT-DTI 0.1011 [0.0956, 0.1072] (0.2600-family base). Repo incumbent (superseded
  packaging of the 2026-10-30 lane at this cell): 0.1287 at the registered b6 (600 m) cell.
* **Leakage canary (before E1):** every NEW feature alone (relay_corridor, relay_logdist,
  stepover_band, strike_persist, tip_align) → AUC on fold-0 withheld truth; AUC > 0.90 = leakage
  until proven otherwise. All features are computed from the fold's VISIBLE faults only.
* **E1 — paired feature ablation** on identical folds/seeds, scored at 44,090 dots / 2.8 px
  (comparable with the 2026-10-30 E2 cell) + far-field restricted (> 5 px from visible):
  A = H-TVGB reproduction (28 static + 4 ctx + 10 thermal);
  B = A + 5 relay-geometry features; C = B with far-field positives ×3.
  Promote criteria: paired Δ(B−A) > 0 with 95% tile-bootstrap CI excluding 0; then Δ(C−B).
* **E2 — paired emission ablation** at the shipped cell (37,654 / 2.8 px / > 6 px catalogue
  exclusion) on the E1 winner: plain emission vs geothermal-anchor-modulated emission
  (field rank × (0.8 + 0.2 × anchor-density rank)). Paired 95% CI.
* **E3 — final build:** winning arm retrained with FULL-catalogue context, emitted at the
  registered b6 cell, packaged through the shared fail-closed writer (`-zeros` variant, float32,
  EPSG:32611, values in [0,1] everywhere), then surface novelty (before placement) + dots novelty
  (after placement) vs the frozen 414-raster registry, exact-duplicate scan, validator receipt,
  run card + release JSON in `evidence/tiprelay/`.
* **Budget:** 3 experiments (E1, E2, E3) / 2 h. Canary and validator are gates, not experiments.
  No weekly submission slot is spent; promotion is a separate selector decision.

## Data obtainability statement

All inputs are already in-repo and hash-verified: the 19 cached GeoDAWN/lidar bands
(`evidence/feature_cache.json`), the GDR geothermal anchors (`data/external/`, official GDR 1391,
DOI 10.15121/1881483, CC BY 4.0), and the Qfault attribute mirror for candidate #4. No new external
source is required for candidates 1–3. Candidate #4 uses the already-mirrored Qfault attributes;
candidate #5 needs nothing new either (existing radiometric bands).

## Amendment A1 — 2026-10-31, before E1 (canary-gate fix; estimator only, hypothesis unchanged)

The canary gate caught a construction defect, not a leakage problem: the first tip-direction
estimator (9×9 interior centroid) plus a 20° two-sided cone accepted **0 relay pairs** on fold 0
(`evidence/tiprelay/leakage_canary.json` first run: `n_relay_pairs: 0`), because the clearance test
also included the tip pixels themselves and the centroid directions are too noisy for oblique relay
bridges. Two fixes, applied **before** any experiment ran: (1) the clearance test covers the open
gap (3-px end trim); (2) corridor acceptance uses the shared visible-strike field **at the tips**
(doubled-angle cosine ≤ 26.2° vs the connecting bearing, both tips mutually aligned) instead of
centroid directions. Fold-0 yield after the fix: **313 accepted relay pairs**, 265,957 px of
smoothed corridor influence, 2,708 step-over pixels. Canary re-run after the fix is the one of
record. `tip_align` likewise uses the nearest tip's strike (mod π).
