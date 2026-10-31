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
