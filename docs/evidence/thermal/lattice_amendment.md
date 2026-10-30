# IR-LATTICE-01 v2 — novelty-registry scope amendment (drafted 2026-10-30, before final placement)

## The obstruction (measured, not assumed)

`knowledge/NEXT_STEPS.md` item 4 required an **explicit, versioned amendment** before another
packaging attempt: the frozen novelty registry (414 TIFF blobs in the nine public focus repos)
contains **superposition calibration grids** — files whose own dot set tiles the whole footprint on
a ~5 px lattice. The largest is `inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif`
(itself a scored 0.0904 submission, a union of 13 sibling-site rasters on a 5 px lattice).
Measured directed 3 px overlap of competitive dotted files against that one raster:

| candidate | dots | % within 3 px of the 13gems lattice | source |
|---|---|---|---|
| SWGB-hrv2 | 44,090 | 99.87 % | `evidence/swgb_lattice_audit.json` (2026-10-28) |
| H-PBSC | 37,654 | 99.48 % | `evidence/pbsc/run_card.json` (2026-10-28) |
| the 0.2778 champion `h33-h33-2-b2` | 37,654 | ≥ 99 % (same lattice family) | geometry: any 2.8–5 px-spaced dot raster lies within 3 px of a 5 px lattice site |

A 5 px lattice has covering radius ~2.5–3.5 px, so **every** competitive dotted submission fails a
literal "≤ 70 % of dots within 3 px of ONE registry raster" test against it — including the
champion the rule is meant to protect. The rule as scoped is unsatisfiable; that is a scope bug,
not a property of any candidate.

## The amendment (scope correction; thresholds unchanged)

1. **Thresholds are not relaxed.** Spearman > 0.90 or directed 3 px overlap > 70 % still means
   lane-drift duplicate → stop. The 0.90 / 70 % / 3 px numbers are unchanged (`AGENTS.md` rule).
2. **Registry scope for the lane-drift test** = every registry raster that is a *distinct-method
   competitive submission* (all 395 `docs/downloads/**` files + the `inputs/gems*` inputs + all
   non-lattice calibration copies). A **superposition calibration grid** — operationally: a raster
   whose own positive support covers > 95 % of the footprint within 3 px — cannot discriminate
   lanes (it is within 3 px of everything) and is excluded from the *lane-drift denominator only*.
   Every such file is still (a) checked for **exact identity** (canonical sha256), (b) scanned for
   Spearman surface correlation, and (c) reported with its raw overlap number as an advisory.
3. **Nothing is silently omitted.** Every run card carries `lattice_rows` with the raw per-lattice
   overlap and both verdicts: `lane_drift_duplicate` (competitive scope) and
   `literal_full_registry_duplicate` (all 414). The download page shows both.
4. This amendment is a **policy draft** owned by the project maintainer. If the maintainer rules
   that calibration grids ARE in scope for the 70 % rule, then no dotted submission (including the
   0.2778 champion) can pass and the deliverable verdicts in this repository flip to
   `duplicate` — the artifacts and evidence remain on file either way.

## Both readings, always

| gate | scope | thresholds |
|---|---|---|
| lane-drift (protocol purpose: "drifted into another lane") | competitive registry rasters | ρ ≤ 0.90, overlap ≤ 70 % @ 3 px |
| literal full-registry | all 414 rasters incl. calibration lattices | same thresholds (expected FAIL for any dotted file — documented, not hidden) |
| exact-duplicate | all 414 + this repo's prior files | canonical sha256 identity ⇒ always in scope |

Reference: the same policy was applied, with disclosure, in the PBSC lane preregistration
(`knowledge/03_hypotheses_20261028.md`: "Lattice calibration raster … is logged as IR-LATTICE-01
and is **not** treated as a competing submission …; treating it as one makes the 70 % rule
vacuous"). This document versions that decision instead of leaving it informal.
