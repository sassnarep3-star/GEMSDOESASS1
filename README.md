# GEMSDOESASS1 — DOE GEMS Prize Challenge: unique, auto-validated fault-prediction submissions

**Read first, every session:** [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) (the full user brief, verbatim) and the
[PARALLEL-RUN PROTOCOL](docs/PROJECT_BRIEF.md#parallel-run-protocol--read-first) inside it. Core values applied
throughout: **Maximize P(Win)** and **Own the Outcome**.

Site (GitHub Pages, built from `evidence/*.json`): `docs/index.html` → executive summary + one-click download ·
`docs/how-to-submit.html` · `docs/run-card.html` · `docs/hypotheses.html`

---

## ✅ The deliverable — OK TO DOWNLOAD AND SUBMIT

| | |
|---|---|
| **File** | [`docs/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif`](docs/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif) (or the `.zip` beside it) |
| **sha256** | `f98c20df5bc67a482de6debd4abef9d3d104498bda0aacf464d693e271287729` |
| **Submission note (127 chars)** | `GEMSASS1 SWGB: 5x segment-withheld HGB on lidar+GeoDAWN, 44090 dots 2.8px, >600m off-catalogue; HOLDOUT-DTI 0.140 vs base 0.101` |
| **Format** | single band float32 · EPSG:32611 · 3730×3292 · transform (100,0,243350,0,−100,4508550) · values {0,1} · **no NaN/Inf anywhere** · zeros outside footprint · 44,090 positive pixels · 0 on known-fault pixels — all 11 validator checks pass from bytes ([receipt](docs/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.checks.json)) |
| **Unique?** | **Yes.** Max Spearman vs the 17 registry rasters 0.115 (limit 0.90); max 57.8 % of dots within 3 px of any registry raster (limit 70 %) |
| **Estimated score** | **HOLDOUT-DTI 0.1401 [0.1329, 0.1452]** (`GEMSASS1-HR-v2-segment`, 60,988 withheld positives). The 0.2600 live file scores 0.1011 on the same evaluator. PROJECTION 0.19–0.28 — **a projection is not a score**; the holdout cannot rank the 0.24–0.28 family (IR-01). |
| **Verdict** | `promote` (to the selector; spending a weekly slot is the human/selector's decision per protocol §6) |

Why this fixes the "Predicted values must be in range [0, 1]" rejection: the writer clips to [0, 1], writes zeros (never NaN) outside the footprint, and refuses to write any file failing a check.

## Executive summary — the nine focus sites (file to download · estimated score · unique?)

| Site | Best file (owner-reported live) | HOLDOUT-DTI here | Unique vs the other sites? |
|---|---|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5…-nan.tif` — 0.2477 | 0.0968 | ✗ H19-5 family (100 % within 3 px of the 0.2600 raster) |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8…-nan.tif` — 0.2600 | 0.1011 (= the bar) | ✗ family base |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5…-nan.tif` — 0.2449 | 0.0965 | ✗ family (98 %) |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1…-nan.tif` — 0.2710 | 0.0302* | ✗ family (100 %) |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090…tif` — 0.2600 | 0.1011 | ✗ byte-identical to GEMSDOE25's base |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28…-nan.tif` — 0.2708 | 0.0314* | ✗ identical to GEMSDOE28 h27-4 |
| **GEMSDOE32** | `gemsdoe32-h33-h33-2-b2…-zeros.tif` — **0.2778 (group best)** | 0.0044* | ✗ = 0.2600 raster minus dots ≤2 px from catalogue (pixel-identical) |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30…tif` — 0.2632 | 0.0547* | ✗ family (99.7 %) |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854…-zeros.tif` — 0.2750 | 0.0045* | ✗ family (97.5 %) |
| **THIS SITE** | `gemsass1-swgb-hrv2-44090dots-…-f9b3f764-zeros.tif` — unscored | **0.1401** | **✓ UNIQUE** |

\* pruned rasters score ~0 on a catalogue-recovery holdout by construction (IR-01); compare only un-pruned files with ours.
Full table with links, CIs and dot counts: `docs/index.html`. Evidence: `evidence/holdout_calibration.json`, `evidence/registry_family_overlap.json`.

## Why 0.2778 won, in three lines (details: [`knowledge/01`](knowledge/01_why_0p2778_and_what_beats_it.md))
1. It is **exactly** the 0.2600 dotted H19-5 raster with the 6,436 dots within 200 m of the known catalogue deleted (re-derived from bytes, sym-diff 0).
2. `DTI = T / (0.2·(T+S−M) + 0.8·|G|)`: emitted mass is taxed at 0.2, known-fault pixels are ignored, so re-detections of mapped scarps 1–2 px off the trace are pure cost. The ladder 0.2600→0.2708→0.2778 is that tax being removed.
3. A catalogue-flank file (h66, dots 3–15 px from faults) scored 0.0742; the champion's dots sit a median 2 km away. Live "new faults" are far-field, so beating 0.2778 needs a better **field**, which is what the SWGB lane supplies (holdout +39 % over the base at the shipped emission; +57 % at 2 px exclusion).

## What was done (one session, autonomous)
* Cloned the 9 focus repositories from github.com (pages/Dropbox/DrivenData unreachable), recovered byte-verified mirrors of the template, catalogue and GeoDAWN/lidar feature stacks from GEMSDOE24, and the 17 top rasters.
* Shared tools (`src/gems/`): official metric with brute-force unit test; hide-and-recover holdout (whole segments + 3 px buffer, visible-only catalogue features, pooled DTI, tile-bootstrap CI, far-field diagnostic); emission; registry lane audit; validator + writer.
* Leakage canary (max AUC 0.715), 5 ranked hypotheses, experiments E1 (negative), E2 (promoted), E2b (negative), E3 sweep; final build; run card; site.

## Limitations / irregularities (flagged)
IR-01 holdout anti-ranks the live family (instrument limit) · IR-02 v1 tile-withholding artefact fixed in the shared evaluator · IR-03 four experiments not three (reason logged) · IR-04 all sibling scores are OWNER-REPORT, leaderboard unreachable here · IR-05 h66 was submitted despite its own "do not submit" flag · IR-06 competition originals replaced by byte-verified mirrors. Sandbox: 2 CPU, 3.9 GB RAM, no GPU, outbound only github.com/pypi.

## Next steps (this or next session)
1. **Spend one slot on the shipped file** and record the receipt in `registry/organizer_confirmed.json` — it is the only way to calibrate a far-field instrument; both outcomes are informative.
2. Obtain the blocked official data (GeoDAWN 100 m DEM / RTP / full TMI from ScienceBase doi:10.5066/P93LGLVQ; 1 m lidar tiles from the organizer's `1m_DEM_links.csv`) on an unrestricted machine → enables H-LAH (Lahontan shoreline suppression) and a true 1 m scarp detector.
3. Build a live-like holdout: use the far-field diagnostic as the primary bar and, once receipts exist, fit holdout→live on *our own* files only.
4. Automate the feed: a GitHub Action that re-runs the registry audit when sibling repos change and republishes `docs/`.

## Reproduce
```bash
pip install -r requirements.txt && bash scripts/fetch_reference_assets.sh && python3 -m pytest -q tests
python3 scripts/calibrate_holdout.py && for e in canary e1 e2 e2b; do python3 scripts/run_experiments.py $e; done
python3 scripts/run_experiments.py e3 e2 && python3 scripts/build_submission.py && python3 scripts/build_site.py
```
