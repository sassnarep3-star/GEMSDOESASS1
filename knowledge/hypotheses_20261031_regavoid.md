# H-REGAVOID — preregistration (2026-10-31, before any run)

> Written before the first experiment of this lane, per the PARALLEL-RUN PROTOCOL.
> Lane budget: 3 experiments / 2 hours, tracked in `evidence/regavoid/budget.json`.

## Hypothesis

Every competitive dotted file >= 0.24 owner-reported (the whole H19-5 openness/LRM emission
family, including the 0.2778 champion) shares dot positions on the same ridge crest lattice.
The 70 %/3 px uniqueness rule therefore fails for any emission that ranks like that family.
**H-REGAVOID: emitting from the repo's strongest *different* field — the H-TSFX 55-feature
segment-withheld learner (HOLDOUT-DTI 0.1587 [0.1522, 0.1658], GEMSASS1-HR-v2-segment) —
under a hard constraint that every dot lie at least `margin` px away from the dots of every
non-lattice registry raster, yields a raster that (a) passes the uniqueness gate against the
full 412-raster competitive registry with directed 3 px overlap = 0, and (b) retains
HOLDOUT-DTI above the promote bar 0.1011 [0.956, 0.1072].**

Mechanism: learner probability x anti-registry mask x visible-catalogue prune x greedy
Poisson-disk (spacing 2.8-3.3 px). The learner field concentrates on ridge structure
(GeoDAWN magnetics/gravity/radiometrics + lidar scarp polarity + strain/seismicity/basement
context) that the H19-5 topographic family never covered; the anti-registry mask removes the
family's dot positions rather than the field's values.

Named non-fault mimics that could produce the same dots: (1) the anti-registry constraint
pushes emission onto *weaker* ridge crests parallel to the family's — hillshade/flight-line
seams and lithologic contacts can outrank true scarps there; (2) pluvial shoreline benches and
fluvial terrace risers around thermal basins; (3) road/canal embankments; (4) basaltic vent rims.

## Why this is not any lane already run

| lane | field | emission | outcome |
|---|---|---|---|
| H19-5 family (champion) | openness/LRM topo | dotted, catalogue-pruned | live 0.2477-0.2778, fails uniqueness (is the family) |
| SWGB | supervised | field-ranked Poisson-disk | HOLDOUT 0.1401-0.1586, lattice-gate withdrawn |
| H-PBSC | hand corridor | playa-bounding step corridor | HOLDOUT 0.0650, unique vs 17, lattice fail |
| H-TSFX | supervised (55 feat) | field-ranked Poisson-disk | HOLDOUT 0.1587, dots fail 70.2-72.3 % vs 11 GEMSDOE25 rasters |
| H-TVGB | supervised (+thermal) | field-ranked, full-cat 600 m prune | HOLDOUT 0.1287, 65 % overlap, per-raster clear |
| **H-REGAVOID** | **supervised (same as TSFX)** | **field-ranked + hard >= margin px from ALL 412 registry rasters** | **(this lane)** |

No previous lane constrained emission against the registry itself; no previous lane reused the
TSFX learner field with a novelty-first emission. Nothing is copied: the shipped bytes are
generated here.

## Leakage canary

The exact 55-feature set was canaried on the identical folds last session
(`evidence/tsfx/leakage_canary.json`: max non-catalogue AUC 0.584 < 0.90 veto). The canary is
re-run in this lane's environment before E1 and must clear again.

## Experiments (budget 3)

- **E1** — retrain the 5-fold H-TSFX learner through the shared code path
  (`scripts/run_tsfx.py` functions imported, not forked). Fields frozen to
  `work/regavoid/regavoid_fields.npz`. [experiment 1]
- **E2** — emission sweep on the frozen fields, grid preregistered here:
  `avoid_margin in {0, 2.0, 3.0 px vs union of 412 competitive registry dot sets}` x
  `visible-prune in {2, 6 px}` x `n_dots in {37654, 44090}` x `spacing in {2.8, 3.3}` = 24
  configs. HOLDOUT-DTI on GEMSASS1-HR-v2-segment, 100-bootstrap CI. Fast eligibility check:
  worst directed 3 px overlap vs the 17 focus rasters <= 0.70. **Selection rule: among
  eligible configs, the maximum HOLDOUT-DTI wins; ties break on far-field DTI, then lower
  n_dots.** The union mask excludes the 13gems calibration lattice (AMEND-LATTICE-01) and any
  raster with an incompatible grid. [experiment 2]
- **E3** — package the winner: mean field, protocol dots (visible prune, anti-registry margin)
  scored on the holdout; shipped artifact = mean-field emission with the same prune radius
  against the FULL published catalogue (the champion's proven live edit) + the same
  anti-registry margin; surface + dots novelty scans over all 412 comparable rasters
  (AMEND-LATTICE-01 / AMEND-N2), sibling/prior extras scan, fail-closed writer, run card.
  The shipped file's own diagnostic holdout is reported separately (structural difference from
  the protocol dots is disclosed, not hidden). [experiment 3]

## Decision gates (fixed before the run)

1. Canary: no feature AUC > 0.90 -> else stop.
2. Surface pre-placement: max Spearman <= 0.90 and max 3 px overlap <= 0.70 vs competitive
   registry, else stop before placement.
3. Final dots: same thresholds vs competitive registry + sibling/prior extras; the lattice
   measurement is reported as IR-LATTICE-01 and excluded from pass/fail only under
   AMEND-LATTICE-01 (witness: the 0.2778 champion itself is 99.9 % vs the 5 px grid).
4. Verdict `promote` requires: canary pass, HOLDOUT-DTI (protocol dots) > 0.1011 bar **and**
   > 0.1287 (the current best *shipped unique* candidate holdout, H-TVGB b6), novelty clear,
   validator 11/11 from bytes. The paired per-fold difference vs the frozen H-TVGB E1 run and
   vs frozen E2-SWGB is reported as a diagnostic, not a gate (AMEND-1, written 2026-10-31
   before E1 started: the original draft gated on a paired-improvement CI vs E2-SWGB, which
   confounds the lane's purpose — H-REGAVOID deliberately trades holdout score for uniqueness;
   the correct incumbent is the best holdout among *shipped unique* candidates, H-TVGB 0.1287).
   Anything less = `negative` (a deliverable).
5. Even on `promote`, no weekly slot is spent here: promotion is a separate selector step,
   and eligibility (rules section 1.3: U.S. citizens / permanent residents or U.S.-incorporated
   entities) is a blocking user decision flagged in the run card.

**AMEND-2 (2026-10-31, written during E1 training, before any E2 result existed):** the
promote verdict additionally requires the *shipped* artifact's own diagnostic HOLDOUT-DTI
(full-catalogue prune) > 0.1011. If the full-catalogue prune collapses the shipped file's
diagnostic holdout below the bar (the structural effect documented for H-TSFX: 0.2708 live →
0.0314 holdout), the verdict is `negative` regardless of the protocol-dots score — the site
must never advertise a file whose own measured holdout is below the bar.

**AMEND-3 (2026-10-31, written after the first E2 execution exposed a mask bug; same
preregistered experiment re-executed once, no new grid, no new degrees of freedom):** the
literal registry union covers all 60,988 catalogue pixels because 21 registry rasters emit
dots on mapped faults (led by the `8GEMSDOE_Hedge-v2_submission.tif` calibration fixture with
60,988 on-catalogue dots). The withheld truth of the holdout *is* the catalogue grid, so a hard
margin vs the full union left 0 pixels within 3 px of any withheld segment and every m>0 config
degenerated to HOLDOUT-DTI 0.0000 (receipt: the partial `e2_emission_sweep` stage log, recorded
in `evidence/regavoid/budget.json` as `e2_partial_degenerate`). Emission therefore avoids only
**non-catalogue** competitor dots: union minus (catalogue dilated 2 px — the champion's own
prune radius). The novelty gate scans are untouched and remain literal. m=0 configs from the
first execution are unaffected (they never read the mask) and are kept.

## What success looks like

A unique, validated GeoTIFF in `docs/downloads/` with directed 3 px overlap 0.0 vs every
competitive registry raster, HOLDOUT-DTI >= 0.1287 (the current shipped-file best, H-TVGB) and
ideally close to the protocol best 0.1587, plus an obvious OK/NOT-OK download verdict on the
site. A holdout collapse below the 0.1011 bar is an expected possible outcome and is recorded
as a negative result.
