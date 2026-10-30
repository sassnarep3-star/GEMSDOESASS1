# Next session — ordered actions (updated 2026-10-30 after the H-TVGB release)

1. **Selector decision on the generated H-TVGB file.** `docs/downloads/gemsass1-hvtgb-thermal-anchored-37654-20261030-zeros.tif`
   passes every automatic gate (format/validator, exact-duplicate scan, lane-drift novelty gate vs the
   competitive registry, HOLDOUT-DTI 0.1407 [0.1354, 0.1464] at the shipped config vs bar 0.1011).
   Spending a weekly slot is a separate selector decision within the official cap. Do not upload
   any historical file (SWGB withdrawn, H-PBSC negative, BGAC-1 stopped).
2. **Formalize IR-LATTICE-01.** The scope amendment draft is `evidence/thermal/lattice_amendment.md`.
   The maintainer must ratify or reject it. If rejected, no dotted file can pass the 70%/3 px rule
   (the 13gems calibration lattice covers ≥99% of every dotted raster, including the 0.2778 champion)
   and the project must move to a non-dotted emission format or an explicit registry exclusion.
3. **Beat 0.3195 with field quality, not emission.** The H19-5 emission ladder is exhausted at 0.2778
   (0.2600 → 0.2708 → 0.2778 came only from deleting near-catalogue dots). The supervised family is
   the only local instrument above the 0.2600 base (HOLDOUT-DTI 0.14–0.16 vs 0.1011). Next concrete
   steps: (a) add tip/step-over geometry and orientation-persistence features to the learner and
   re-run the paired ablation; (b) raise the far-field credit (farfield 0.119–0.135 vs pooled 0.14–0.16)
   because the live truth is far-field; (c) re-test the geothermal family as an EMISSION prior
   (concentrate dots near warm-spring/sinter/2mDAB anchors) — as learner features it is a measured
   negative (paired Δ −0.0124 [−0.0170, −0.0079]).
4. **Emission sensitivity exists but is out of the preregistered operating point.** E3 measured
   0.1516 [0.1445, 0.1574] at 52,000 dots / >2 px prune vs 0.1407 at the champion point
   (37,654 / >2 px). The champion point is fixed by live evidence (the 0.2600→0.2778 ladder);
   if a future selector prefers holdout-optimal mass, the 52k config is one sweep away.
5. **Official data still login-walled.** DrivenData features / 1 m DEM links; USGS GeoDAWN full grids.
   Outbound here: github.com, pypi.org. Every historical score remains OWNER-REPORT until an
   organizer receipt is captured. The prompt's high-score claims conflict (0.4413 vs 0.3195).
6. **Keep the frozen negatives.** Do not delete or soften `evidence/run_card.json` (BGAC-1),
   `evidence/pbsc/run_card.json`, `evidence/swgb/`, or the lattice audits. New evidence goes in new
   directories (`evidence/thermal/`).
7. **Read first next session:** this file, `README.md` (project prompt appendix),
   `knowledge/PROJECT_BRIEF.md`, `knowledge/hypotheses_20261030.md`, `evidence/thermal/run_card.json`,
   `evidence/thermal/release.json`.
