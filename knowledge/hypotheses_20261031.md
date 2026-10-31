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
