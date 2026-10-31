# Next session — ordered actions (updated 2026-10-31 after BOTH same-day lanes merged)

> 2026-10-31 shipped two independent gated candidates from concurrent sessions (H-TIPRELAY, this
> branch, merged last; H-KDAM, merged earlier the same day) plus the H-STEP-OVER research artifact.
> The cross-lane duplicate check PASSED (near-independent fields), so both candidates stand and the
> selector chooses within the weekly cap. The 2026-10-30 parts (Part 1/Part 2) remain valid history.

## Part 0 — state after the 2026-10-31 double release (read this first)

1. **Recommended default release (this session):** `docs/downloads/gemsass1-tiprelay-continuation-37654-b6-20261031-zeros.tif`
   (sha256 `43017aa4…`, run card `evidence/tiprelay/run_card.json`, verdict `promote`,
   `ok_to_download_and_submit = true`, 0 slots used). Shipped-cell HOLDOUT-DTI **0.1384 [0.1322,
   0.1458]** vs bar 0.1011 and incumbent 0.1287; E1 ablation cell 0.1573; paired Δ relay features
   **+0.0110 [+0.0081, +0.0141]**; novelty surface ρ 0.132 / dots 65.2% competitive; exact-duplicate
   scan 414/414 on disk.
2. **Parallel gated candidate (H-KDAM, selector alternative):** `gemsass1-kdam-alteration-contact-37654-20261031-zeros.tif`
   (sha256 `d10c99c3…`, `evidence/kdam/release.json`), HOLDOUT-DTI **0.1471 [0.1418, 0.1531]**
   unpruned arm vs same-emission family base 0.1011; competitive max 3 px overlap 31.1%; all 489
   inventory rasters measured with the lattice disclosed (99.96%, AMEND-LATTICE-01). Review pass
   fixed two integrity defects the same day (`knowledge/REVIEW_2026-10-31.md`): a concurrent
   rewrite of `registry/focus_inventory.json` (failed 0→114) was restored, and the sparse
   placeholder's card named a nonexistent file (irregularity #11, hash-locked).
3. **Cross-lane duplicate check (both audits were blind to each other) — PASSED:** full-footprint
   Spearman −0.0028; 169 of 37,654 dot pixels shared (0.45%); 3 px overlap 4.3%/10.3%. The fields
   are near-independent, not duplicates
   ([evidence/tiprelay/cross_lane_kdam_check.json](../evidence/tiprelay/cross_lane_kdam_check.json)).
4. **Open user decisions (unchanged, blocking any upload):** (a) eligibility — rules §1.3 restrict
   competitors to U.S. citizens/permanent residents or U.S.-incorporated entities; confirm with the
   administrator; (b) IR-LATTICE-01 / AMEND-LATTICE-01 uniqueness scope — the literal 70%/3 px rule
   is unsatisfiable for any dotted file (the lattice covers ≥99% of all of them, champion included);
   both readings are published for every artifact.
5. **Measured answers now on file (do not re-run):**
   - Relay/step-over/persistence learner features: paired Δ **+0.0110 [+0.0081, +0.0141]** — keep.
   - Far-field positives ×3 in the loss: paired Δ **−0.0055 [−0.0084, −0.0028]** — negative.
   - Geothermal anchors as emission prior: paired Δ **−0.0152 [−0.0191, −0.0113]** — negative
     (NEXT_STEPS 4c answered; the family is a measured negative as learner features AND emission prior).
   - E1 arm A reproduced the 2026-10-30 arm to 4 decimals (0.1462) — the shared instrument is stable.
   - H-KDAM field: +45.6% weighted hidden-fault credit vs the same-emission family base (0.1471 vs 0.1011).
6. **Next experiments, ranked across both lanes' plans:**
   a. **H-SOFTEMIT (from the H-KDAM review — highest value per cost).** The official metric scores
      fractional values fractionally (`TP_w = Σ_g max_x p(x)k(d)`, `FP_w = Σ_x p(x)[1−max k]`), and
      every registry file is binary. Emit the same field as graded probabilities and measure the
      paired holdout difference at equal support. Cheap (cached fields exist), cannot copy anyone.
   b. **Single-model full-catalogue field with a held-out emission sweep (both lanes need this).**
      The shipped files use one full-catalogue model (good); the holdout arms average five fold
      models. Re-run E1 with a single model trained on all catalogue segments and a held-out
      emission sweep so the shipping configuration is not chosen on the same holdout that scores it.
   c. **H-QFAULT-ATTR** — slip-rate/recency-weighted continuation corridors (data mirrored:
      `data/external/gdr_qfaults_traces.csv`, `qfault_attributes.csv`); the relay family's positive
      result makes attribute-weighted continuations the natural follow-up.
   d. **H-RADON-CONCORD** — radiometric gradient lineament concordance (lane-drift check against
      GEMSDOE74/75 files mandatory before running).
   e. Extend the novelty registry beyond the nine focus sites (sibling lanes GEMSDOE44–92, WBG,
      KANLER, GINNY, karage, apart publish their files publicly;
      `scripts/fetch_registry_current.py`, git sparse checkout — the REST contents API exhausts
      its 5,000/h quota).
7. **Instrument cautions stay in force:** HOLDOUT-DTI is not a leaderboard forecast (holdout↔live
   Spearman −0.08 over the 17-file family; it inverts the live prune effect — the 0.2778 file scores
   0.0044 here while the same field unpruned scores 0.1011); catalogue-prune width dominates the
   off-catalogue instrument (docs/INSTRUMENT_IRREGULARITY.md). Use the holdout to compare fields,
   never to predict live scores. Label every number HOLDOUT-DTI or OWNER-REPORT.
8. **Keep the frozen negatives** (BGAC-1, H-PBSC, SWGB, thermal lane, B2 duplicate log, lattice
   audits). New evidence goes in new directories.
9. **Read first next session:** this file, `README.md` (both 2026-10-31 status blocks),
   `knowledge/hypotheses_20261031.md` (both lanes' preregistrations + amendments),
   `knowledge/RESULTS_20261031.md` (both lanes' results), `knowledge/REVIEW_2026-10-31.md`,
   `evidence/tiprelay/run_card.json`, `evidence/kdam/release.json`.

---

## Part 1 — H-TVGB thermal-lane release record (2026-10-30, superseded by Part 0 where noted)

1. **Selector decision on the generated H-TVGB file.**
   `docs/downloads/gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif`
   passed every automatic gate in its own session under the per-raster reading of the lane-drift
   rule. **2026-10-31 update: superseded by the H-TIPRELAY and H-KDAM files above — do not submit
   it.** The superseded 2 px packaging remains a logged lane-drift duplicate
   (`evidence/thermal/run_card_b2_duplicate_log.json`) and must not be uploaded.
2. **Ratify or reject the lattice scope readings (user).** Both readings are reported for every
   artifact, including the new releases.
3. **Resolve eligibility (user, blocking).** See Part 0 item 4a.
4. **Beat 0.3195 with field quality — EXECUTED 2026-10-31** (see Part 0 item 5 for outcomes).
5. Emission sensitivity for H-TVGB measured; the relay-field sweep at 52k dots is pending.
6. **Keep the frozen negatives.** Unchanged.
7. Read-first list superseded by Part 0 item 9.
