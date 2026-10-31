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
