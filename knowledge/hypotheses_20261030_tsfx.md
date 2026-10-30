# Session 2026-10-30 — preregistered hypotheses, slate, and novelty-policy amendment

Written **before** any experiment was run in this session. Read together with
[`NEXT_STEPS.md`](NEXT_STEPS.md), [`hypotheses_20261029.md`](hypotheses_20261029.md) and
[`01_why_0p2778_and_what_beats_it.md`](01_why_0p2778_and_what_beats_it.md).

## 0. Policy decision taken first — AMEND-LATTICE-01 (the item NEXT_STEPS #4 demands)

NEXT_STEPS #4 required "an explicit, versioned amendment" for the calibration-lattice novelty
question **outside a stopped run**. This is that amendment. It does not relax either threshold
(ρ > 0.90, overlap > 0.70 at 3 px) and it does not silently omit any raster.

**Witness, re-measured from bytes in this checkout (2026-10-30):**

| raster | dots | dots within 3 px of the 13gems lattice | evidence class |
|---|---|---|---|
| `gemsdoe32-h33-h33-2-b2…-zeros.tif` (0.2778 OWNER-REPORT, the file this session analyses) | 37,654 | **37,622 / 37,654 = 99.915 %** | MEASURED-HERE |
| `gems25-dotted-h19-5-d2-8…-nan.tif` (0.2600 OWNER-REPORT) | 44,090 | 44,053 / 44,090 = 99.916 % | MEASURED-HERE |
| `gems28-h27-4-r1-solo-d2-8…-nan.tif` (0.2708 OWNER-REPORT) | 40,199 | 40,166 / 40,199 = 99.918 % | MEASURED-HERE |
| `13gems_20261001_r13-lattice-s5_v2_nan-outside.tif` itself | 206,895 | regular grid, dy = dx = **5 px exactly** | MEASURED-HERE |

**Finding.** The lattice is a synthetic full-footprint 5 px calibration grid (path
`inputs/calibration/` in GEMSDOE24; itself OWNER-REPORT 0.0904). For any square grid of spacing
5 px, essentially every point in the plane lies within 3 px of a grid point (measured ≥ 99.9 %
for three independent real submissions, including the 0.2778 champion). The literal
"more than 70 % of your dots within 3 px of one registry raster's dots" rule, when applied to
this lattice, is therefore **vacuous: it flags every possible submission as a duplicate,
including the very file this project was asked to analyse and beat**. The rule's stated purpose
is lane-drift (copying another lane's emission); a regular-grid fixture cannot detect that.

**AMEND-LATTICE-01 (versioned, explicit):**

1. The rank-correlation gate (ρ ≤ 0.90 vs **every** of the 414 registry rasters, including the
   lattice) applies literally and is reported.
2. The 3 px / 70 % overlap gate applies literally to every registry raster **except** synthetic
   calibration fixtures that are regular grids covering the footprint (identified here:
   `GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif`, dy = dx = 5 px,
   206,895 dots). Such fixtures are still measured, and the raw number is printed in the run card
   as `IR-LATTICE-01` alongside this witness, never omitted.
3. Any registry raster that is a real published submission (including its mirrors across focus
   sites) is subject to the full gate unchanged.
4. This amendment is required for the gate to be satisfiable at all; retracting it would classify
   the 0.2778 champion, the 0.2600 base, and every dotted submission in the group as duplicates
   of a 0.0904 grid.

Also under this amendment: **AMEND-N2** — a registry raster with nonfinite values inside the
footprint cannot be rank-compared as published; it is evaluated with nonfinite treated as 0
support (the same reduction `binary_dots` applies), instead of blocking clearance. Thresholds
unchanged.

## 1. What the 0.2778 champion is (verified line-by-line from bytes this session)

| claim | measurement (MEASURED-HERE) |
|---|---|
| champion == `d2.8 ∩ {EDT(existing_faults) > 2 px}` | symdiff = **0** |
| `h27-4` == `d2.8 ∩ {EDT > 1 px}` | symdiff = **0**; 3,891 dots removed at 1 px, 6,436 at 2 px |
| champion ⊆ d2.8, counts 44,090 − 6,436 = 37,654 | exact |
| champion values | float32, 0/1, no NaN anywhere |

Why it scores (labelled): DTI = TP / (TP + 0.2·FP + 0.8·FN) with 300 m triangular credit and
**known catalogue pixels excluded from scoring** (official: staff forum thread 11516) ⇒
(a) mass is taxed at 0.2 but coverage is credited once per truth pixel ⇒ thin dots beat lines;
(b) dots on/near the catalogue are ignored or pure FP risk ⇒ deleting them raised 0.2600 →
0.2708 → 0.2778 live (OWNER-REPORT ladder); (c) every remaining dot must earn
k > 0.2·DTI ≈ 0.056. All nine focus sites' ≥0.2449 files are one H19-5 family
(≥ 97.5 % within 3 px of the 0.2600 base, `evidence/swgb/registry_family_overlap.json`).

**Beating 0.2778 requires a better far-field lidar-scarp field at ~38–44k dots, not another
H19-5 prune.** Holdout (hide-and-recover of catalogue segments) is the only local instrument;
it does not rank within-family emission edits (Spearman −0.08, `evidence/swgb/holdout_calibration.json`),
so every holdout number below is a gate, never a leaderboard projection.

## 2. Five candidate hypotheses (none has been run in this checkout)

Layers named below all exist in this checkout (u8 stacks in `data/features/`, 19-band stack via
`data/official/training_features.tif`, sidecars in `data/features/*.json`) — no external data is
required, so every candidate is runnable now. Ranking = expected HOLDOUT-DTI improvement over the
current repo holdout best × implementation cost (qualitative, not a score projection).

| rank | id | specific layer(s) | physical signature targeted | why it can catch a fault missing from USGS/INGENIOUS | how it differs from everything already in this repo | expected gain / cost |
|---|---|---|---|---|---|---|
| **1 (LANE)** | **H-TSFX tectonic-strain fusion learner** | SWGB's 32 layers **plus** unused 19-band stack: `geod_shearrate`, `geod_2ndinv`, `geod_dilaterate` (GPS/InSAR strain), `deq_n100a15` / `ieq_n100a15` (seismicity), `depth_to_base_surf` (+gradient), `cond_surf`, `det_elev(_slope)`, `rtp`, `tmi_hg`, `iso_grav_anom_hg`, **plus new** label-free polarity-coherence features (below) | joint segment-withheld learner over scarp morphology × geodetic strain-rate loci × microseismicity × basement-step/conductivity context | unmapped Holocene strands concentrate where strain rate and seismicity accumulate but mapped traces stop; the learner recovers withheld scarps from morphology conditioned on those tectonic priors — the priors themselves never touch the catalogue | no lane here has ever fed the geodetic-strain, seismicity, depth-to-basement, conductivity or detrended-elevation bands to any learner (BGAC used gravity/basement as a label-free signed anti-gradient and scored 0.039–0.073 HOLDOUT-DTI; SWGB used only lidar/rad/mag + catalogue context) | **high / medium** |
| 2 | **H-POLCOH scarp polarity coherence** | lidar `step_max`, `downface_max`/`upface_max` signed into `face_asym`, `strike`, `coh100` | a fresh normal-fault scarp steps down in the **same** direction along strike for kilometres: circular concentration of doubled strike × sign-consistent facing over connected high-step ridges, rejecting symmetric ridges, flows and terrace risers whose facing flips | the hidden labels are unmapped surface scarps; polarity persistence is a young-dip-slip property that canyon walls/roads fail (their facing follows drainage) | not the 2026-10-29 abstract "asymmetry" note (never implemented, and it used local asymmetry magnitude only); not RFPD (no visible-catalogue strike gate, no dipole couple); not PBSC (no playa/relief conjunction); label-free | medium / low |
| 3 | **H-BSTEP basement-step scarp coincidence** | `depth_to_base_surf` horizontal gradient (σ 3–8 px), lidar `step_max` × `coh100`, weak `mag_hgrad_s5` | **positive coincidence** of a buried basement step edge with a surface scarp (upward fault propagates from a basement ramp and breaks the cover) | range-front scarps in alluvium sit above basement steps that are invisible in surface geology maps | BGAC tested *signed opposition between gravity and basement gradients with weak surface expression*; this is *edge–scarp coincidence* and veto-weights topographic-quiet sites — opposite regime to H-CXSE (which vetoes scarps) | low–medium / low |
| 4 | **H-SEISKG seismicity-weighted lineaments** | `deq_n100a15`, `ieq_n100a15` × lidar `step_max`/`coh100` lineaments | instrumental earthquake density is highest on the still-active strands; a scarp where instrumental seismicity clusters is more likely a Holocene fault than a relict one | Qfaults omits uninstrumented Holocene scarps, while the earthquake catalogue is an independent, non-geologic observation of where slip is accumulating | the distance-to-earthquake bands have never been used by any lane or by any public focus-site file we measured | low / low |
| 5 | **H-RELAYPOL polarity-flip relay bridge** | lidar `face_asym`, `strike`, `step_max`, `coh100` | at a releasing relay/stepover, the down-facing polarity of two en echelon scarps flips across a short connecting anticlinal/oblique hinge — bridging them finds the un-mapped connector segment | connectors between mapped strands are exactly the segments Qfaults under-maps in alluvium, and they carry the same scarp morphology | the H19-5 family takes relay/tip geometry from the **visible catalogue**; this derives relay geometry purely from label-free polarity fields; siblings' dual-horizon/conduit lanes used different physics (do-not-copy list) | medium / medium |

## 3. Frozen experiment plan (≤ 3 experiments, ≤ 2 hours, this session)

- **Bars (both stated):** protocol promote bar = 0.1011 [0.0956, 0.1072] (un-pruned 0.2600 family
  base); **current repo holdout best = 0.1591** (E2-field, prune 4 px, 44,090 dots,
  `evidence/swgb/e3_prune_sweep_e2.json`; as-evaluated E2 = 0.1586). Promotion to a selector slot
  requires beating **0.1591** with a paired-compatible evaluator, not merely 0.1011.
- **E1 = H-TSFX.** Same splits (`GEMSASS1-HR-v2-segment`, seed 20261027), same model class and
  hyper-parameters as frozen E2-SWGB (clean feature ablation), emission 44,090 dots / 2.8 px on
  `fd.active` only. Every input feature alone must pass the leakage canary (AUC ≤ 0.90) on
  withheld truth before results are read.
- **E2 = emission sweep on the E1 fields** (n ∈ {37,654, 44,090} × spacing ∈ {2.8, 3.3} ×
  visible-prune ∈ {2, 4, 6} px) — only if E1 beats 0.1011; the winner must keep ≤ 0.70 overlap
  vs the h66 flank raster and beat 0.1591.
- **E3 = packaging or backup.** If E1/E2 beat 0.1591: full-registry novelty scan (414 + sibling
  files), fail-closed writer, run card. If not: run H-POLCOH as the label-free backup within
  budget, or stop with a negative card — negatives remain deliverables.
- **Shipped emission (only after all gates):** the protocol dots are the measured artifact; the
  shipped TIFF additionally applies the champion's own proven live edit — exclusion > 2 px from
  the **full published** catalogue (public competition input, legal for live scoring per staff
  forum 11516) — disclosed as a separate emission with its own holdout number printed.
- **No projection is written as a score.** Any forward number is labelled PROJECTED with its
  method and band; owner-reported ledger values stay OWNER-REPORT; ORGANIZER-CONFIRMED appears
  only from submission-page receipts (none exist here).

## 4. Non-fault mimics named in advance

- Fluvial terrace risers and canal banks (same crest–toe dipole, facing follows drainage).
- Pluvial Lake Lahontan shorelines (contour-parallel, low-relief, playa-bounding).
- Lithologic contacts and flight-line seams (mag/rad edges without faulting).
- Seismicity-distance bands are smooth population/instrument-coverage fields, not structure.
- Geodetic strain-rate grids are interpolated from GPS/InSAR networks — a smooth prior, not a scarp.
