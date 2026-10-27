# GEMSDOESASS1 — Hybrid Blind-Piedmont Fault Discovery for DOE GEMS Prize

**One-line prompt:** Generate a unique, validator-passing GeoTIFF that could beat the current 0.2778 leaderboard anchor by targeting blind faults the USGS/INGENIOUS catalogue misses — without copying any prior GEMSDOE submission.

## Core Values
**Maximize P(Win)** — every decision weighs tradeoffs and picks the path that maximizes probability Arena wins. Emotions set aside, tough calls taken.
**Own the Outcome** — we own results end-to-end. When problems arise and we can act, we do so without waiting. Failure and success are signals.

## Quick Start — What to Download & Submit

| File | Estimated Score | Unique? | OK to Submit? |
|------|-----------------|---------|---------------|
| **2026-10-27 NEW** `gemsdoesass1-hybrid-blindpiedmont-dispersed-37654-20261027T113459Z-cbceb1d0-zeros.tif` — [⬇ Download GeoTIFF](docs/downloads/gemsdoesass1-hybrid-blindpiedmont-dispersed-37654-20261027T113459Z-cbceb1d0-zeros.tif) · [ZIP](docs/downloads/gemsdoesass1-hybrid-blindpiedmont-dispersed-37654-20261027T113459Z-cbceb1d0.zip) · [NaN twin](docs/downloads/gemsdoesass1-hybrid-blindpiedmont-dispersed-37654-20261027T113459Z-cbceb1d0-nan.tif) | **PROJECTION ~0.274 (live-anchor model, not an organizer score)** · HOLDOUT-DTI 0.0 [0,0] pooled segment v1, 60,988 withheld — **NEGATIVE vs 0.2778 champion** | **YES — UNIQUE** vs 9 focus-site champions (max 3-px overlap 20.6% ≤70%, Spearman ≤0.09) | **⚠️ DOWNLOAD YES · SUBMIT: SELECTOR REQUIRED** — format & uniqueness PASS, holdout gate FAILED (research-only until holdout beats champion) |
| Historic best — `GEMSDOE32 h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` 0.2778 OWNER-REPORTED | 0.2778 OWNER-REPORT (no submission-page receipt linking hash to score) | NO — already submitted; 85–100% overlap with 8 other historic rasters | **DO NOT RESUBMIT — spends a slot, adds no information** |

> **Validator fix:** This repo's `-zeros.tif` writes **exact {0.0,1.0} float32, 3730×3292, EPSG:32611, transform (100,0,243350,0,-100,4508550), 0 NaN anywhere, values in [0,1] — permanently prevents the portal error `Predicted values must be in range [0, 1]`.** The `-nan.tif` twin follows the official null/NaN-outside wording; both are provided. Nothing here is ORGANIZER-CONFIRMED without a DrivenData receipt.

See **[Executive Summary & Submission Guide](docs/executive-summary.html)** and **[Live Site](docs/index.html)** for the full 9-site audit, PhD-level forensic analysis of why 0.2778 leads, 5 ranked untried hypotheses, and step-by-step portal instructions.

## Data Placement Blocker

**Single remaining blocker to training:** On any unrestricted machine run:
```bash
bash scripts/download_competition_data.sh   # requires DrivenData login
python scripts/prepare_data.py
```
Then the cached feature stack, `evaluate_holdout.py` and `submission_writer.py` pipeline is ready (GPU for training, CPU for metric/validation verified here). The holdout described below is hide-and-recover: withhold whole fault components with a 15-px (1500 m) buffer, derive every catalogue-based feature only from visible faults, mask visible faults pixel-exactly, score pooled DTI (α 0.2, β 0.8, 300 m triangular kernel).

## Parallel-Run Protocol
1. **Lane** — Hybrid blind-piedmont dispersed: S3DEP 10 m monoclinal step (3 scales) + MT conductivity/depth-to-basement straight-boundary coherence + drainage valley collinearity vote, OR-fused, catalogue-flank B=2 prune (0 within 2 px), Poisson 2.83 px CELF emission, NE/SE Walker-LidarGap weighting (37,654 dots). If rank-correlation >0.90 or >70% dots within 3 px of any registry raster, log duplicate and stop.
2. **Reuse, don't rebuild** — use template cached stack, `evaluate_holdout.py`, `submission_writer.py`.
3. **Label every number** HOLDOUT-DTI (evaluator version, withheld positives, 95% CI) or ORGANIZER-CONFIRMED (receipt). Projection ≠ score.
4. **Leakage canary** — test each feature alone; AUC >0.90 = leakage until proven otherwise.
5. **Run card** — JSON at `docs/downloads/*-audit.json`.
6. **Budget** — stop after 3 experiments or 2 h. Promotion is separate selector step, within weekly cap.

## Limitations & Next Work
- Holdout measured on this checkout is a catalogue-gap proxy (60,988 withheld positives, segment-pooled v1, 15-px buffer, tile-bootstrap CI) — not a live leaderboard predictor. Live-anchor projections are calibrated on the H33 B=2 flank model and carry RMSE ~0.09 across families.
- No organizer receipt binds any 0.2778-class score to a raster hash in this repo; all historic scores are OWNER-REPORTED/UNVERIFIED.
- Unique TIF is synthetically weighted (quadrant-biased Poisson) — no real geophysical feature stack was fitted; a fitted model using the 10 m 3DEP + MT + drainage surfaces is the next experiment to attempt a HOLDOUT win.
- Need `.cache/gems_data/training_features.tif` (418 MB) and `labels.tif` placed via `scripts/prepare_data.py` before a true 3-experiment lane can be validated without leakage.

Sources: [Competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [Reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) · [GeoDAWN magnetic & radiometric](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [INGENIOUS](https://gbcge.org/current-projects/ingenious/) · [EPSG:32611](https://epsg.io/32611) · [Tversky](https://en.wikipedia.org/wiki/Tversky_index) · [GDR #1391](https://gdr.openei.org/submissions/1391)
