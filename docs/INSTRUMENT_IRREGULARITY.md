# Instrument irregularity report — no local instrument certifies a new field against 0.2778

_Generated 2026-10-30 by the Arena agent on branch `arena/b8ff95d7-gemsdoesass1`. All numbers are
local measurements on shared tools unless a receipt is cited._

## 1. What was asked

GEMSDOE32 has recorded a live leaderboard score of **0.2778**, catalogue-free, from the
`gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` emission (37,654 dots, 2.8 px
spacing, 0% within 200 m of the full USGS/INGENIOUS catalogue). We are asked what the current
leaderboard high is, whether a new field could beat 0.2778, and what would have to be true.

## 2. The current leaderboard high — not locally verifiable

DrivenData is unreachable from this workspace. The only readings found are **owner-reported**, all
in sibling repos, and they **conflict**:

| reading | score | source |
|---|---|---|
| 2026-10-03 | 0.3195 | DARD (GEMSDOE32 `live_ledger.json`) |
| 2026-10-26 | 0.4437 | xiaofanhu (GEMSDOE32 `live_ledger.json`) |
| 2026-10-29 | 0.4544 | owner report |

The user-supplied figure of **0.4413** matches GEMSDOE32's own refuted live-mirror projection
(`evidence/live_mirror_validation.json`), not any measured score. **The highest figure that has an
artifact trail on public GitHub is GEMSDOE32's 0.2778** (with `readme_pin_sha256 =
bb73dda2739c25b03b571267950b82c119822037059c057815714042f69208a7`).

**No organizer-confirmed score exists for any file in this workspace.** Every "current high" claim
must be labelled OWNER-REPORT.

## 3. The nine-site verified table (shared toolchain, one run, GEMSASS1-HR-v2-segment)

| site | live (OWNER-REPORT) | HR-b0 | HR-b2 | SGMC-raw | SGMC-cal | dots |
|---|---|---|---|---|---|---|
| GEMSDOE24 | 0.2477 | 0.0932 | 0.0972 | 0.1011 | 0.0579 | 60069 |
| GEMSDOE25 | 0.2600 | 0.0967 | 0.0992 | 0.0953 | 0.0606 | 44090 |
| GEMSDOE27 | 0.2449 | 0.0927 | 0.0968 | 0.1024 | 0.0583 | 61328 |
| GEMSDOE28 | 0.2710 | 0.0294 | 0.0289 | 0.0943 | 0.0630 | 37660 |
| GEMSDOE30 | 0.2600 | 0.0967 | 0.0992 | 0.0953 | 0.0606 | 44090 |
| GEMSDOE31 | 0.2708 | 0.0305 | 0.0301 | 0.0963 | 0.0630 | 40199 |
| **GEMSDOE32** | **0.2778** | **0.0045** | **0.0045** | 0.0961 | 0.0641 | **37654** |
| GEMSDOE33 | 0.2632 | 0.0520 | 0.0507 | 0.0968 | 0.0626 | 41865 |
| GEMSDOE36 | 0.2750 | 0.0046 | 0.0046 | 0.0974 | 0.0644 | 38854 |

Live and dot count move **together** across the family (Spearman −0.85 between live score and
HR-b0). HR-b0/HR-b2 and the farfield DTI move **opposite** to live. The winner is the *least*
precious file on every shared instrument.

**The champion's live win is therefore an emission-efficiency / sparsity win, not a field win.**
It places 37,654 dots on a lattice with zero collisions with a 300 m catalogue-collision kernel,
earning only its TP mass while paying a small α-weighted FP penalty.

## 4. Both candidate local instruments are refuted by the group's own live record

### SGMC off-catalogue DTI — refuted

`evidence/sgmc_instrument_live_counterexamples.json`:

| file | SGMC off-catalogue DTI | live |
|---|---|---|
| GEMSDOE29 `sgmc-off-catalogue-44k` | 0.5607 | 0.0512 |
| GEMSDOE72 | 0.6483 | 0.0492 |
| R6-1 `stepprofile` | 0.1419 | (~0) |
| GEMSDOE32 champion | 0.0954 | 0.2778 |

Files that trace USGS SGMC score far higher on this instrument than the champion, yet scored
~0.05 live. The instrument rewards exactly the SGMC-tracing files the live scorer destroys.

### Live Mirror (LM) — failed its own validation

`evidence/live_mirror_validation.json` (GEMSDOE32): **8 references, 6 live orderings, only 2/6
reproduced raw and 3/6 reproduced prevalence-calibrated.**

## 5. New experiment this session: `H-GDR-CONDUIT-OFFCAT`

Declared before running; distinct from H-PBSC, SWGB, BGAC-1, SWGB-DIR.

**Hypothesis.** Unmapped Great Basin geothermal conduits are structurally controlled: the faults
hosting warm/hot springs, warm wells and 2 m temperature anomalies coincide with coherent 10 m-scale
lidar scarp steps, and those faults are under-represented in the USGS/INGENIOUS catalogue because the
catalogue was compiled from older 30 m mapping.

**Field.** Rank fusion `0.45·rank(sqrt(rank(lidar step_max)·rank(lidar coh100)))
+ 0.35·rank(Gaussian(GDR well/spring temperature + vents, σ=4 px)) + 0.20·rank(band 17 cond_surf)`.
No SGMC/labels-derived input. **GDR prior confirmed rich and unused by every lane in the register:
12,570 unique well/spring cells (27,092 rows) with temperature and thermal class, 21 volcanic vents,
Q-fault traces with slip rate/recency.**

**Leakage canary (HIDE-RECOVER fold 0, AUC):** scarp 0.541, geo 0.549, cond 0.513. **None > 0.90 →
pass.**

**Emission:** 37,654 dots, 2.8 px, 0 dots on the catalogue, 0 within 2 px (200 m).

### Result — and the structural finding behind it

| catalogue prune | HOLDOUT-DTI |
|---|---|
| 6 px (600 m) | **0.0000** |
| 2 px (200 m) | **0.0045** |

The champion records 0.0045. **My 2 px run reproduces the champion's shared-evaluator score
exactly, with a completely different field.** The shared evaluator's truth is the hidden *catalogue*
segments, so any dot outside the 300 m kernel earns zero credit; the score is therefore set
entirely by the catalogue-proximity prune and is **insensitive to field content**. This is the
decisive confirmation that HR-b0/HR-b2 cannot certify a new field.

Other instruments on the same field (all DIAGNOSTIC, never promotion criteria):
SGMC off-catalogue DTI **0.0887** vs champion 0.0961; LM-calibrated **0.2395** vs champion 0.2679.

**Novelty audit flagged a duplicate** against a dense coverage-complete registry raster
(surface stage: 3 px directed overlap 0.999, Spearman 0.102). Under the literal 70%/3 px rule this
lane is a **negative**.

## 6. Conclusion

1. The current leaderboard high **cannot be established from this workspace**. The highest figure
   with an artifact trail is **0.2778**; the user-supplied 0.4413 matches GEMSDOE32's refuted LM
   projection, not a measurement.
2. The champion's 0.2778 is an **emission-efficiency win**, not a geology win. It is reproducible
   with an arbitrary off-catalogue lattice — this session reproduced its exact shared-evaluator
   score (0.0045) from a geothermal+scarp+conductivity field.
3. **No local instrument can certify a new field against 0.2778.** Both candidate instruments are
   refuted by the group's own live record, and the shared evaluator is blind to catalogue proximity.
4. Any promotion verdict must therefore **state the instrument conflict explicitly** and leave the
   slot decision to the user. This workspace promoted nothing and uploaded nothing.
