# Next session — ordered actions (updated 2026-10-31 after the H-TIPRELAY release)

> Supersedes the ordering below only where it conflicts; the 2026-10-30 parts (Part 1/Part 2) remain
> valid history. The 2026-10-31 lane executed the previous Part 1 items 4a/4b/4c.

## Part 0 — state after the 2026-10-31 release (read this first)

1. **The active release is** `docs/downloads/gemsass1-tiprelay-continuation-37654-b6-20261031-zeros.tif`
   (sha256 `43017aa4…`, run card `evidence/tiprelay/run_card.json`, verdict `promote`,
   `ok_to_download_and_submit = true`, 0 slots used). Every gate passed: validator, exact-duplicate
   (414/414 on disk), lane-drift novelty (surface ρ 0.132; dots 65.2% ≤ 70% competitive), holdout
   bar, catalogue mass. **Selector decision still required before any upload**, plus the two open
   user decisions below.
2. **Open user decision 1 — eligibility** (unchanged from 2026-10-30 Part 2): rules §1.3 restrict
   competitors to U.S. citizens/permanent residents or U.S.-incorporated entities. Confirm with the
   administrator before any upload.
3. **Open user decision 2 — IR-LATTICE-01 uniqueness policy** (unchanged): the literal 70%/3 px rule
   is unsatisfiable for any competitive dotted file (the 13gems lattice covers 99.84% of this
   release too; both readings are in the run card). The per-raster competitive-scope reading was
   used for the release gate, with the lattice reading published beside it.
4. **Measured answers now on file (do not re-run):**
   - Relay/step-over/persistence learner features: paired Δ **+0.0110 [+0.0081, +0.0141]** — keep.
   - Far-field positives ×3 in the loss: paired Δ **−0.0055 [−0.0084, −0.0028]** — negative.
   - Geothermal anchors as emission prior: paired Δ **−0.0152 [−0.0191, −0.0113]** — negative
     (completes NEXT_STEPS 4c; the geothermal family is now a measured negative as learner features
     AND as an emission prior).
   - E1 arm A reproduced the 2026-10-30 arm to 4 decimals (0.1462) — the shared instrument is stable.
5. **Next experiments, ranked (preregister, canary, then run; budget 3 / 2 h):**
   a. **H-QFAULT-ATTR** — slip-rate/recency-weighted continuation corridors (data already mirrored:
      `data/external/gdr_qfaults_traces.csv`, `qfault_attributes.csv`). The relay family's positive
      result suggests attribute-weighted continuations are the natural follow-up.
   b. **H-RADON-CONCORD** — radiometric gradient lineament concordance (lane-drift check against
      GEMSDOE74/75 files mandatory before running).
   c. Emission-sweep on the tiprelay winner (52,000-dot cell measured 0.1516 for H-TVGB; not yet
      measured for the relay field — the sweep is one step away in `run_tiprelay_lane.py e2/e3`).
6. **Instrument cautions stay in force:** HOLDOUT-DTI is not a leaderboard forecast (holdout↔live
   Spearman −0.08 over the 17-file family); catalogue-prune width dominates the off-catalogue
   instrument (docs/INSTRUMENT_IRREGULARITY.md). Label every number HOLDOUT-DTI or OWNER-REPORT.
7. **Keep the frozen negatives** (BGAC-1, H-PBSC, SWGB, thermal lane, B2 duplicate log). New evidence
   goes in new directories.
8. **Read first next session:** this file, `README.md` (Status — 2026-10-31),
   `knowledge/hypotheses_20261031.md` (preregistration + amendment A1),
   `evidence/tiprelay/run_card.json`, and the 2026-10-30 parts below.

---

## Part 1 — H-TVGB thermal-lane release record (2026-10-30, superseded by Part 0 where noted)

1. **Selector decision on the generated H-TVGB file.**
   `docs/downloads/gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif`
   passes every automatic gate under the per-raster reading of the lane-drift rule (format
   validator, exact-duplicate scan vs 414 registry rasters + repo priors, per-raster novelty gates:
   surface Spearman ≤ 0.133, dots 3 px overlap 65.0% ≤ 70% vs the competitive registry;
   HOLDOUT-DTI 0.1287 [0.1231, 0.1355] at the shipped config vs bar 0.1011; far-field restricted
   0.1343). **2026-10-31 update: this file is superseded by the H-TIPRELAY release above — do not
   submit it.** The superseded 2 px packaging remains a logged lane-drift duplicate
   (`evidence/thermal/run_card_b2_duplicate_log.json`) and must not be uploaded.
2. **Ratify or reject the lattice scope readings (user).** The lattice-bound analysis shows the
   literal full-registry 70%/3 px rule is unsatisfiable for any competitive dotted file (the 13gems
   lattice covers ≥99%). Both readings are reported for every artifact, including the new release.
3. **Resolve eligibility (user, blocking).** See Part 0 item 2.
4. **Beat 0.3195 with field quality — EXECUTED 2026-10-31** (see Part 0 item 4 for outcomes).
5. Emission sensitivity for H-TVGB measured; the relay-field sweep is pending (Part 0 item 5c).
6. **Keep the frozen negatives.** Unchanged.
7. Read-first list superseded by Part 0 item 8.
