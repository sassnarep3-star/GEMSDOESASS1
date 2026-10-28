# GEMSDOESASS1 — DOE GEMS Prize Challenge: unique, auto-validated fault-prediction submissions

**Read first, every session:** [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) (standing user brief, verbatim) and [`AGENTS.md`](AGENTS.md). Core values: **Maximize P(Win)** · **Own the Outcome**.

# Part 0 — H-PBSC lane (session 2026-10-28)

**Is the new GeoTIFF OK to submit?** **NO.** Unique and format-valid; lost the holdout bar.

| | |
|---|---|
| **Research file (DO NOT SUBMIT)** | [`docs/downloads/gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif`](docs/downloads/gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif) |
| **sha256** | `2f3bd24e7be6edb58df011482622075a72e08beb5eab772d50c4d6aa80247fd9` |
| **Note (107/140)** | `GEMSASS1 PBSC: playa-bounding step×coh×low-relief 37654d 2.8px >600m offcat; HOLDOUT-DTI 0.065 vs bar 0.101` |
| **HOLDOUT-DTI** | **0.0650 [0.0605, 0.0693]** (`GEMSASS1-HR-v2-segment`, 60,988 withheld positives) vs bar **0.1011 [0.0956, 0.1072]** |
| **Unique?** | **Yes.** max Spearman 0.029 (limit 0.90); max 25.3 % of dots within 3 px of any of 17 focus rasters (limit 70%); vs prior SWGB / SASS2 / SASS3 max 26.0 % |
| **Validator** | 11/11 from bytes: float32, EPSG:32611, 3730×3292, template transform, values {0,1}, no NaN/Inf, zeros outside footprint, 0 on catalogue |
| **Verdict** | `negative` · `ok_to_submit = false` |
| **What to upload instead** | Prior SWGB file in Part A (HOLDOUT-DTI 0.1401, unique, `promote`) |

Lane: playa-bounding scarp corridor (lidar `step_max` × `coh100` × low-relief 800 m neighborhood × LoG dipole). E1 (+ mag) 0.0621; E2 (no mag, shipped) 0.0650. E3 not run (bar not beaten). Canary max AUC 0.573. Median catalogue distance of shipped dots: 27 px (~2.7 km). Named mimic: Lake Lahontan shorelines. Evidence: `evidence/pbsc/run_card.json`. Hypotheses: `knowledge/03_hypotheses_20261028.md`. Site: [`index.html`](index.html) (hero is a red **DO NOT SUBMIT** banner).

Why 0.2778 (GEMSDOE32 `h33-h33-2-b2`) cannot be copied: it **is** the 0.2600 H19-5 dotted field minus dots ≤2 px from the catalogue (sym-diff 0). Beating it needs a better *field*. H-PBSC is a different field and is unique; it does not recover withheld catalogue segments as well as H19-5/SWGB, so it is not promoted.

---

> This README then has two earlier parts. **Part A (SWGB lane)** produced the only cleared-for-selector file. **Part B (BGAC lane)** is a prior negative. Nothing was deleted.

# Part A — SWGB lane (session 2026-10-27)

**Read first, every session:** [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) (the full user brief, verbatim) and the
[PARALLEL-RUN PROTOCOL](docs/PROJECT_BRIEF.md#parallel-run-protocol--read-first) inside it. Core values applied
throughout: **Maximize P(Win)** and **Own the Outcome**.

Site (GitHub Pages, built from `evidence/*.json`): `swgb/index.html` → executive summary + one-click download ·
`swgb/how-to-submit.html` · `swgb/run-card.html` · `swgb/hypotheses.html`

---

## ✅ The deliverable — OK TO DOWNLOAD AND SUBMIT

| | |
|---|---|
| **File** | [`swgb/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif`](swgb/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif) (or the `.zip` beside it) |
| **sha256** | `f98c20df5bc67a482de6debd4abef9d3d104498bda0aacf464d693e271287729` |
| **Submission note (127 chars)** | `GEMSASS1 SWGB: 5x segment-withheld HGB on lidar+GeoDAWN, 44090 dots 2.8px, >600m off-catalogue; HOLDOUT-DTI 0.140 vs base 0.101` |
| **Format** | single band float32 · EPSG:32611 · 3730×3292 · transform (100,0,243350,0,−100,4508550) · values {0,1} · **no NaN/Inf anywhere** · zeros outside footprint · 44,090 positive pixels · 0 on known-fault pixels — all 11 validator checks pass from bytes ([receipt](swgb/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.checks.json)) |
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
Full table with links, CIs and dot counts: `swgb/index.html`. Evidence: `evidence/swgb/holdout_calibration.json`, `evidence/swgb/registry_family_overlap.json`.

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

## Reproduce (SWGB lane)
```bash
pip install -r requirements-swgb.txt && bash scripts/fetch_reference_assets.sh && python3 -m pytest -q tests
python3 scripts/calibrate_holdout.py && for e in canary e1 e2 e2b; do python3 scripts/run_experiments.py $e; done
python3 scripts/run_experiments.py e3 e2 && python3 scripts/build_submission.py && python3 scripts/swgb_build_site.py
```


---

# Part B — BGAC lane (`vendor/gems57` pipeline)

> **Submission status (two parallel lanes, reconciled 2026-10-27):**
> * **BGAC lane (this section's pipeline): BLOCKED** — the single preregistered BGAC-1 experiment failed both the improvement and literal dot-overlap gates; no BGAC TIFF is cleared.
> * **SWGB lane (section above): one unique TIFF cleared by its automatic gates and promoted to the selector** — `swgb/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif`. Its evaluator (`GEMSASS1-HR-v2-segment`) differs from `gems57-pooled-hide-v2`; numbers from the two lanes are not directly comparable and neither is a leaderboard forecast.

**Start every session here**, then read [the persistent project brief](knowledge/PROJECT_BRIEF.md), [hypotheses](knowledge/hypotheses.md), [three-pass review](evidence/review.md) and [run card](evidence/run_card.json). The brief is a deduplicated transcription of the user's repeated prompt, not a verbatim archive. It preserves the mission, Core Values / Own the Outcome, strict protocol, sources, validation, download and release requirements.

## Executive result

| Item | Evidence / decision |
|---|---|
| BGAC-1 | **Exploratory HOLDOUT-DTI 0.0390**, 95% CI **[0.0283, 0.0501]**, 56,454 withheld positive pixels; evaluator `gems57-pooled-hide-v2`. Pass-2 review disqualified the first-pass execution: it should have stopped before placement. |
| Strongest same-run ablation | **HOLDOUT-DTI 0.0730**, 95% CI **[0.0569, 0.0892]**, same positives/evaluator |
| Paired difference | **HOLDOUT-DTI −0.0340**, 95% CI **[−0.0466, −0.0220]**, same positives/evaluator |
| New unique TIFF | **None.** Final dots have 100% directed overlap within 3 px of a registry lattice. The experiment stopped, without packaging. |
| Best historical result in supplied nine-site list | GEMSDOE32, **0.2778 — UNVERIFIED owner/user report, not ORGANIZER-CONFIRMED**. Exact mask mechanism and bytes verified; no submission-page receipt. |
| Estimated leaderboard score | **Unavailable.** Catalogue hide/recover is not a calibrated leaderboard forecast. |
| Competition slots used | None. No upload or slot selection code. |

See the [executive summary](docs/executive-summary.html), [nine-site pages](docs/index.html#historical), [scientific analysis](knowledge/scientific_analysis.md), [sources](knowledge/sources.json), [history audit](evidence/nine_site_audit.json), and [next actions](knowledge/NEXT_STEPS.md).

## What this checkout actually contains

The initial commit had only `# GEMSDOESASS1`. This change builds the first pipeline/site here. It does not inherit the training/GPU verification asserted in the chat. The CPU experiment reuses pinned shared tools from [GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32/tree/1398109a23f04a2ace71c1bd2f527cfba87860b5/vendor/gems57), including the cached-band builder, whole-component spatial folds, evaluator, and fail-closed submission writer. [Vendor provenance](vendor/PROVENANCE.json) identifies exact hashes; no shared metric was forked or changed.

The restored feature stack is approximately 419 MB. Raw data, caches, historical TIFFs and the Python environment are ignored by Git; only receipts, code and the static site are tracked. The complete frozen registry has 414 TIFF blobs in the nine public priority repos (outside `data/`). Other sites/private submissions are not covered. One prior has nonfinite footprint values and one is an incompatible format fixture; these are explicitly recorded, never silently normalized into clearance.

## Reproduce / verify

Python 3.11+, `gh`, and network access to GitHub and PyPI are sufficient for the measured CPU run. Arena already configures GitHub; never put credentials in files.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-lock.txt
.venv/bin/python scripts/prepare_data.py           # ~419 MB source + ignored band caches
.venv/bin/python scripts/registry_snapshot.py      # restore frozen 414-file registry, verify blobs
.venv/bin/python scripts/audit_history.py          # analysis only, no experiment
.venv/bin/python scripts/verify_release.py         # evidence + site checks, no data needed
.venv/bin/pytest -q
python scripts/build_site.py
python -m http.server 8000 --bind 0.0.0.0 --directory docs
```

The completed experiment is immutable: `scripts/evaluate_holdout.py` refuses to overwrite its run card. To reproduce scientifically, use a separate copy of the checkout with an empty evidence output directory after archiving the frozen evidence; never remove failed evidence to conceal a trial. Its one experimental command was:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/evaluate_holdout.py
```

No GPU was needed. All catalogue-derived information is limited to split construction, visible-fault masking, and the final known-fault exclusion—not the BGAC surface. Splits hide whole original components, including cross-quadrant tails; 80 px training buffer, fixed label-blind quadrants. DTI uses the user's protocol formula, independently unit-tested against the shared brute-force implementation; the official metric page was not reachable to authenticate its current definition. The official reference notebook confirms fault detection and asymmetric Tversky **training loss**, not the 300 m evaluation formula.

## Submission gate, not a promise

`vendor/gems57/submission_writer.py` refuses nonfinite, out-of-range, misaligned or outside-footprint positive output; it validates the on-disk TIFF/ZIP and never silently clips or fills model errors. It does **not** approve a scientific result. `scripts/evaluate_holdout.py` only calls it after novelty and canary clearance. The current run never reached it.

An eventual release requires: verified input provenance/rules; leakage clearance; strict surface + dot novelty; compatible incumbent holdout improvement with a paired CI; correct single-band CRS/shape/transform/range; a separately authorized selector within the official weekly cap. Portal acceptance and ORGANIZER-CONFIRMED score require an organizer receipt. No automatic submission is implemented.

## Site and refresh feed

GitHub Pages uses the existing legacy `main` / root configuration, with root links into `docs/`. There is a landing page, executive-summary/how-to page, research/source page, and one executive page per focus site. These are local comparative pages; the nine upstream websites have not been edited. The evidence page automatically checks current public GitHub heads in the browser with a one-hour cache and explicit timeout/rate-limit failures; a scheduled workflow also preserves advisory snapshots as Actions artifacts. Neither changes scores, experiments, novelty clearance or promotion. The experimental snapshot remains pinned. The GitHub connection returned HTTP 403 when asked to switch Pages to Actions deployment; the existing legacy deployment is retained, not misreported as reconfigured.

## Limitations that matter

- No verified DrivenData submission receipt, current leaderboard, weekly cap, rules PDF or current official data hashes. The provided high-score claims conflict. We cannot truthfully promise a higher leaderboard score.
- Outbound access is limited to GitHub/npm/PyPI hosts; USGS, GDR, NLR, DrivenData and Dropbox are outside that allowlist. Official GitHub reference code was inspected; owner mirrors are explicitly weaker evidence.
- The literal 70%/3 px rule is obstructed by a lattice covering 99.87% of the footprint within 3 px. No density exemption was applied. A policy decision outside this stopped run is needed before another method can realistically clear that registry.
- No new competition TIFF was produced because the required gates failed. This is a verified negative deliverable, not a completed high-scoring submission.

## Concurrent main integration

Another parallel session merged a separately negative synthetic research artifact into `main` while this branch ran. It is preserved, not deleted or treated as this lane's output: [parallel-main research archive](archive/parallel-main-f620a70/README.md). All 14 files are byte-hashed; old HTML is inert `.txt`, and TIFFs/ZIP remain learning-only in the archive, outside active downloads. Its limited uniqueness comparison and unvalidated projection are not adopted. The current BGAC-1 decision remains **negative / no approved TIFF**.

A second concurrent audit (PR #4, main `2f67fac`) is also [fully preserved](archive/parallel-main-2f67fac/README.md), including its independent negative lattice-witness read-back, tooling and tests. Its [broader user-provided historical ledger](knowledge/user-provided-submission-ledger.md) is retained additively; unreceipted reports remain unverified. Only the current pipeline/site is active, and pytest scopes execution to tests/, not archived source snapshots.
