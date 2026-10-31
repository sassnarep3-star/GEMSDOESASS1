# Session 2026-10-31 — H-REGAVOID lane (anti-registry emission)

**Decision: the session's generated file is NOT OK to submit (AMEND-2, preregistered before any
E2 result).** The standing H-TVGB release remains the file the site points to for download.
No competition slot was used. Machine-readable record:
[`evidence/regavoid/run_card.json`](../evidence/regavoid/run_card.json) · preregistration with
AMEND-1/2/3: [`knowledge/hypotheses_20261031_regavoid.md`](hypotheses_20261031_regavoid.md) ·
release card: [`evidence/regavoid/release.json`](../evidence/regavoid/release.json) ·
budget: [`evidence/regavoid/budget.json`](../evidence/regavoid/budget.json) (2 counted
experiments + packaging stage, 2,669 s of the 7,200 s budget).

## 1. The headline number — HOLDOUT-DTI, labelled

| number | value | label |
|---|---|---|
| H-REGAVOID protocol dots (visible prune 2 px, margin 2 px, n=37,654, 2.8 px) | **0.4443 [0.4349, 0.4529]** | HOLDOUT-DTI (`GEMSASS1-HR-v2-segment`, 60,988 withheld positives) |
| far-field restricted (>5 px from visible) | 0.4108 | HOLDOUT-DTI |
| promote bar (0.2600-family base) | 0.1011 [0.0956, 0.1072] | HOLDOUT-DTI (frozen calibration) |
| standing H-TVGB rule cell | 0.1287 [0.1231, 0.1355] | HOLDOUT-DTI (E3 cell, visible-prune) |
| prior repo protocol best (E2-SWGB 4 px) | 0.1591 | HOLDOUT-DTI |
| **shipped file diagnostic (this run's bytes)** | **0.000027** | HOLDOUT-DTI (AMEND-2 → fail) |
| paired Δ vs same-field H-TSFX E1 emission | **+0.2853 [0.2701, 0.3004]** | HOLDOUT-DTI paired per-fold |

The 0.4443 reading is the highest local instrument value ever recorded in this repository
(2.7× the family bar; +0.285 over the identical field's unconstrained emission). It is a
rule-quality measurement, not a leaderboard projection.

## 2. Novelty — cleared, at last, with margin to spare

* Surface (pre-placement, 412 comparable registry rasters): max Spearman **0.185**, max 3 px
  overlap **0.319**, no duplicates → cleared.
* Final dots: max Spearman **0.003**, max directed 3 px overlap **0.188**
  (`gems30-MSDB1-edge44090…`), no duplicates → cleared. Previous lanes failed at 0.65–0.72.
* Sibling/prior files: cleared. Lattice (IR-LATTICE-01): 0.9999, excluded under
  AMEND-LATTICE-01 (witness: the 0.2778 champion scores 99.915 % against the same grid).
* Validator: 11/11 from bytes — float32, EPSG:32611, 3730×3292, values {0,1}, 36,557 positive
  pixels, zero on mapped faults, no NaN anywhere. sha256
  `6568c180441c99bedfda233321184a729e7dddaef850d7062ad5aa5968c50a47`.

## 3. Why the verdict is still `negative` (AMEND-2, written before E2 ran)

The shipped artifact applies the champion's proven live edit — prune every dot within 2 px of
the **full** published catalogue. On the hide-and-recover instrument the withheld truth *is*
the catalogue, so this prune deletes the file's entire credit neighbourhood: the shipped
bytes score 0.000027, below the 0.1011 bar. AMEND-2 pre-committed that such a collapse forces
`verdict = negative` regardless of the protocol score. The gate fired; the run card is frozen;
the file `docs/downloads/gemsass1-regavoid-m2-36557dots-20261031T060637Z-cb801cf1f910-zeros.tif`
is marked **NOT OK TO SUBMIT** everywhere on the site.

**Irregularity discovered while applying it (IR-SHIPPED-BITS-01):** we scored the standing
H-TVGB shipped file's actual bytes the same way — **0.0000**
(`evidence/regavoid/tvgb_shipped_diagnostic.json`). Its release cited the E3 *visible-prune*
cell (0.1287), but the file was emitted with a full-catalogue 600 m prune
(`scripts/run_thermal_lane.py`, `catalogue_exclusion(cat, …)`). The number is a correct
rule-quality cell mislabelled as a shipped-bytes measurement. Structurally, **every**
full-catalogue-pruned file scores zero on this instrument (champion-style emissions all
prune 2–6 px off the catalogue); the instrument cannot see live-relevant credit of this
artifact family — consistent with the prior finding that "the score is set by the prune".
Consequences: (a) the standing TVGB verdict stands on its own preregistered gates (rule cell
0.1287 > bar, uniqueness 0.650 ≤ 0.70, validator 11/11) but its release text carries this
labeling caveat; (b) neither 0.4443 nor 0.1287 forecasts a live score; (c) the group's
champion-style live scores (0.24–0.28 OWNER-REPORT) were never measurable by this instrument.

## 4. What was actually new here (no copy of any previous submission)

* **Method:** emission with a hard constraint — every dot ≥2 px from the dots of every
  non-lattice registry raster (AMEND-3: minus catalogue ±2 px, see below). No prior lane
  constrained emission against the registry; the shipped bytes are generated in this session,
  hashed, and compared against all 414 registry rasters + sibling files.
* **AMEND-3 (root-caused mid-run):** the literal registry union covers all 60,988 catalogue
  pixels (21 rasters emit on mapped faults; the Hedge-v2 fixture covers every catalogue pixel),
  which made the first margin>0 sweep degenerate to DTI 0.0000 (receipt:
  `evidence/regavoid/budget.json:e2_partial_degenerate`). The emission avoid-set now excludes
  catalogue ±2 px; the gate scans remain literal. m=0 configs were unaffected and are kept.
* **Environment fixes (shared tools, reported once):** git-clone data restore
  (`scripts/restore_via_git.sh`, `scripts/restore_registry_via_git.py`) because the GitHub API
  quota was exhausted; u8 stacks must land in `data/features/` (patched in the restore script).

## 5. Interpretation (PhD-level summary of "why 0.2778 and what beats it")

0.2778 = the H19-5 openness/LRM ridge field (44,090 dots) minus every dot within 2 px of the
published catalogue: the field itself was not new, the *prune* was. Scoring theory (α=0.2,
β=0.8, 300 m kernel) rewards dots near genuinely unmapped strands and taxes unmatched mass,
so after the family exhausted prune widths (0.2600 → 0.2708 → 0.2778), the only remaining
levers are (i) a field that ranks *unknown* faults better, and (ii) placement rules that keep
emission off positions every competitor already covers. This session measured lever (ii)
directly: the same learner field goes 0.1587 → 0.4443 when emission avoids all registry dots,
with novelty dropping to 0.188. What remains unproven is transfer: no local instrument ranks
live scores (holdout↔live Spearman −0.08), the shipped-bytes instrument is structurally blind
to this artifact family, and the official leaderboard is login-walled. Beating 0.2778 (and
0.3195/0.4413/0.4544 — user figures remain mutually inconsistent, OWNER-REPORT) requires the
next lane to combine the margin-2 placement with a field whose credit lives outside every
catalogue halo, so the shipped artifact itself carries measurable holdout.

## 6. Budget and integrity receipts

* Experiments: E1 retrain (790 s), E2 sweep (24 configs, incl. the discarded degenerate
  execution — disclosed), E3 packaging. Cumulative 2,669 s < 7,200 s. Slots used: 0.
* Canary: re-run in this environment — 55 features, max mean AUC < 0.90, none flagged.
* Every number above is HOLDOUT-DTI (evaluator, withheld positives, 95 % CI shown) or marked
  OWNER-REPORT. No projection is written as a score. No ORGANIZER-CONFIRMED receipt exists.
* Eligibility (rules §1.3: U.S. citizens/permanent residents or U.S.-incorporated entities;
  user location Calgary, AB, Canada) remains a blocking decision before any upload.

## 7. Verdict

`verdict = negative`, `ok_to_submit = false` for
`gemsass1-regavoid-m2-36557dots-20261031T060637Z-cb801cf1f910-zeros.tif`.
**Do not upload it.** The site's downloadable file remains the standing H-TVGB candidate
(`gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif`), subject to the same
eligibility and selector decisions as before. Next lane is preregisterable in
[`knowledge/NEXT_STEPS.md`](NEXT_STEPS.md).
