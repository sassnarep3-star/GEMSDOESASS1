# Session 2026-10-31 — H-RECALL-DOM lane: preregistration (written BEFORE any run)

Lane id: `H-RECALL-DOM`.
Written: 2026-10-31, before E1. Nothing below was chosen after seeing a result.

## 0. What forced this lane

`scripts/certify_metric.py` re-derived the shared evaluator's algebra from its own
bytes and every identity passed (`evidence/metric_certification.json`). Two facts
drive the whole lane:

1. **The denominator is linear in emitted mass.**
   `FN = K - TP` and `alpha + beta = 1`, so
   `D = TP + a*FP + b*FN = a*(TP + FP) + b*K`.
   Verified to 1e-9 against `dti_exact` and against the literal brute-force
   oracle on five prediction shapes.
2. **Recall and precision are not comparable levers.**
   `dDTI/dTP = (a*FP + b*K)/D^2` and `dDTI/dFP = -a*TP/D^2`. At the champion's
   operating point (`TP ~ 5.2k`, `FP ~ 17k`, `K ~ 14k`) one unit of TP is worth
   about **14 units of FP**; in the certification fixture the ratio was 37.7.

Consequence: the field-wide convention of thinning to Poisson-disk dots at
2.8–3 px spacing is only optimal if the posterior is flat inside its support.
It is not. A pixel that lies **on** a truth fault has `k_self = 1`, so its FP
cost is **zero** while it lifts coverage from `1 - (s/2)/3` to `1`. Densifying
along structures the field is *already confident about* is therefore close to
free, and the 2.8 px convention throws away coverage there while still paying
full FP everywhere it is uncertain.

## 1. Hypotheses considered (ranked by expected HOLDOUT-DTI gain x cost)

| rank | id | mechanism | expected gain | cost | status |
|---|---|---|---|---|---|
| 1 | **H-RECALL-DOM** | Replace fixed-spacing thinning with the certified marginal-acceptance set `dT > a*DTI*(dT + dFP)`; densify on high-confidence structures, stay sparse where the posterior is weak | high (recall lever is 14x the FP lever) | low — reuses `vendor/gems57/emit.py`, no new data | **RUN in E1/E2** |
| 2 | H-POST-GRADE | Replace the binary H19-5 mask with a graded posterior so the marginal rule has something to grade | medium-high | medium — needs a model over the restored 19-band stack | folded into E2 |
| 3 | H-CORRIDOR | Emit a saturated 3-px band instead of dots | **negative** — certification measured 0.714 vs 1.000 for the exact trace and 0.815 for 2.8 px dots on a perfect line | none | **falsified by certification, dropped** |
| 4 | H-MASS-OFF | Emit far *more* mass everywhere (the 6%/10% "dti-optimal-emission" idea) | negative — GEMSDOE22 measured 0.1002 / 0.0748 for it, and it is the same lever pushed past the bar | none | dropped, kept as a control in the sweep |
| 5 | H-FARFIELD | Restrict emission to >5 px from the visible catalogue | unknown | low | kept as a diagnostic (`score_pooled_farfield`) |

## 2. Preregistered design

* **Evaluator**: `GEMSASS1-HR-v2-segment` (`src/gems/holdout.py`), 5 whole-segment
  folds, 3 px hidden buffer, visible catalogue masked pixel-exactly from the
  scored domain, pooled DTI, 50x50-px block-bootstrap 95% CI, 300 resamples.
* **Leakage canary**: single-feature AUC on the withheld truth; **AUC > 0.90
  means leakage until proven otherwise**.
* **E1 — geometry only, field fixed.** Field = the champion's own H19-5 binary
  mask (`data/inputs/gems19-h19-5-...-nan.tif`, verified reachable from
  `buffedlizard55-lab/GEMSDOE24`). Emissions: Poisson-disk min-dist
  {1.0 (= full mask), 1.5, 2.0, 2.8 (champion reproduction), 4.0, 6.0} and the
  marginal-rule greedy allocator; catalogue prune {0, 2} px.
  **E1 isolates geometry: any difference is the emission, not the field.**
* **E2 — geometry on a graded posterior.** Same emission machinery applied to a
  graded field built from the restored official 19-band stack.
* **E3 — packaging.** Best configuration, novelty + format gates, run card.
* **Selection bias, declared in advance**: E1/E2 sweep many configurations on
  the *same* holdout. The best-of-N figure is optimistically biased and will be
  labelled as such. A configuration only counts as *established* if its paired
  CI against the champion control excludes 0 on the low side.
* **Budget**: 3 experiments / 2 h of experiment wall-clock.

## 3. Falsification criteria (written before the run)

H-RECALL-DOM is **negative** if any of these hold:

1. The champion reproduction (min-dist 2.8, prune 2 px) beats every denser
   variant on the pooled holdout by a margin whose paired CI excludes 0.
2. Denser emissions gain recall but the FP term grows faster than 14x slower,
   i.e. the observed `dDTI` is negative.
3. The leakage canary fires on the graded posterior.

## 4. Named non-fault process that could mimic the mechanism

Any linear feature that is not a fault: lithologic/dike contacts, welded-tuff
edges, pluvial shorelines, drainages, and cultural edges (roads, field
boundaries) all produce ridge-like lineaments in a DEM and in the magnetic
derivatives. Densifying along them raises FP **and** looks like recall on a
catalogue-based holdout if the catalogue itself was mapped from the same
imagery. The far-field diagnostic and the novelty audit are the guards.

## 5. E1 result (2026-10-31) and the amendment it forced

**E1 (geometry sweep, H19-5 field, `GEMSASS1-HR-v2-segment`), measured:**

| configuration | emitted | HOLDOUT-DTI | 95% CI | coverage |
|---|---|---|---|---|
| champion reproduction, prune 0, md 2.8, n=44,090 | 44,090 | 0.1007 | [0.0959, 0.1049] | 0.155 |

and two structural facts measured from the bytes:

* the H19-5 support is **121,131 px (2.34 % of the footprint)** and has **exactly
  zero** pixels in common with the catalogue (minimum distance 1.0 px) — the
  champion's field already excludes the known catalogue by construction;
* only **43.8 %** of catalogue pixels lie within 3 px of that support, which is
  why the champion's own holdout coverage is 0.155 while its live coverage is
  ~0.37. **The catalogue holdout is a biased proxy for the live truth**, exactly
  as the instrument-irregularity note said.

**Amendment AMEND-E1-01 (written after seeing E1, flagged as post hoc).**
E1's denser configurations were invalid as run: `poisson_disk_dots` was called
with `allowed = footprint` while `field` was 0 outside the support, so the
"thinned" variants placed dots over the whole footprint (n = 600,000 = the
function's `max_candidates` cap). The one valid row is the champion
reproduction. The geometry question is therefore **not** answered by E1 and is
re-posed analytically instead:

Under the certified algebra, with a support of length `S` dotted at spacing `s`,
a fraction `g` of the support on truth, and `K` truth pixels,

    T  = g*S*(1 - s/12)        FP = c*(1-g)*S/s        D = 0.2*(T+FP) + 0.8*K

Calibrating `(g, c, K)` on the champion's two known live scores (44,090 dots ->
0.2600; 37,654 dots -> 0.2778, the difference being 6,436 dots deleted for being
within 2 px of the catalogue, i.e. contributing FP only) fixes
`K ~ 14,086`, `T ~ 5,228`, `FP ~ 32,548`, `g ~ 0.065`. Sweeping `s` in that
calibrated model gives DTI 0.236 (s=1.4), 0.264 (s=2.0), **0.2778 (s=2.8)**,
**0.2784 (s=3.0)**, 0.272 (s=4.0).

**=> The group's 2.8–3.0 px convention is already at the optimum for a field of
this precision, and the flatness of the curve means emission geometry cannot
beat 0.2778. Precision `g` is the only lever that moves the score:**
holding `s = 2.8`, the same model gives DTI 0.2778 at `g = 0.065`,
**0.4544 at `g = 0.108`** (the current leaderboard top), and 0.555 at the
`g = K/S = 0.134` ceiling. **Beating 0.2778 requires raising `g`, not changing
`s`.** This is a NEGATIVE result for H-RECALL-DOM as originally posed, and it
is the finding that selects the E2 field below.

## 6. E2 — the field that E1 says is needed: H-OFFSET-STEP

**Hypothesis.** `g` (the fraction of an emitted lineament support that is
actually a hidden fault) is limited by *false lineaments*, not by missing
lineaments. In this basin the dominant false lineaments are pluvial-lake
shorelines, drainage channels and cultural edges: all three are expressed in
topography and therefore in every topographic openness/LRM field such as H19-5,
but **none of them offsets the basement**. A range-front normal fault, by
contrast, produces an *across-strike step* in the potential-field and
basement/conductivity surfaces as well as in topography.

**Mechanism.** Score a pixel by the product of (i) a topographic lineament
score and (ii) a geophysical lineament score, each from the across-strike
structure tensor (coherence x across-strike gradient energy) of an independent
instrument group:

* TOPO   : `det_elev`, `det_elev_slope`
* MAG    : `rtp`, `tmi`, `mag_anom`, `tmi_hg`
* GRAV   : `iso_grav_anom`, `iso_grav_anom_hg`, `iso_grav_anom_slope`
* BASE   : `depth_to_base_surf`, `cond_surf`
* GEOSEIS: `geod_2ndinv`, `geod_shearrate`, `geod_dilaterate`, `ieq_n100a15`

Requiring the product (not the sum) raises `g` because a shoreline has no
basement/gravity/magnetic step to corroborate it.

**Non-fault mimic.** A lithologic contact or a dike also offsets both topography
and the potential fields, so it survives the product test; a welded-tuff edge is
the specific danger. Guards: the leakage canary, the far-field diagnostic, and
the novelty audit.

**Validation.** E2 scores H-OFFSET-STEP with the *same* certified emission
(s = 2.8 px, fold-aware 2 px visible-catalogue prune) against the champion
reproduction (0.1007) and the repo bar (0.1011) on `GEMSASS1-HR-v2-segment`,
plus the >5 px far-field variant, and reports the leakage canary.
**A live-score improvement is NOT claimed from a holdout win** — the holdout
truth is catalogue, and section 5 shows the catalogue proxy is biased. The
holdout is used only to establish that the new field detects real faults at a
rate at least as good as the incumbent field, which is a necessary (not
sufficient) condition.
