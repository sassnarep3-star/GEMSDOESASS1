# Three-pass review — H-PBSC session 2026-10-28

## Pass 1 — implemented
Lane H-PBSC (playa-bounding scarp corridor) preregistered in `knowledge/03_hypotheses_20261028.md`.
E1 (+mag) HOLDOUT-DTI 0.0621; E2 (no mag) 0.0650 [0.0605, 0.0693]; neither beats bar 0.1011.
Canary max AUC 0.573. Unique vs 17 focus rasters (max ρ 0.029, max 3 px 25.3%) and vs prior SWGB/SASS2/SASS3 (26.0%).
Shipped research TIF: 37,654 dots, 11/11 validator, values {0,1}, EPSG:32611. Verdict negative.

## Pass 2 — bugs fixed
- Winner comparison KeyError (`winner["holdout_dti"]` vs `winner["rec"]["holdout_dti"]`) — fixed and rerun.
- Mechanism text claimed mag on the shipped file; E2 won — corrected on the run card.
- Existing tests forbade any `docs/downloads/*.tif` (BGAC-era contract) — scoped to “only the named H-PBSC research TIF, and only if `ok_to_submit` is false”.
- `verify_release.py` same contract; Fieldnotes still 13 HTML pages; H-PBSC how-to lives at repo root so CI `check_links` does not escape `/docs`.
- `build_site.py` banner updated so Fieldnotes does not contradict the research TIF’s existence.

## Pass 3 — against the original request
- Unique TIF generated, not a copy of GEMSDOE24–36 or of this repo’s SWGB file.
- Homepage makes submit/don’t-submit obvious (red / green).
- Nine-site table lists file, OWNER-REPORT live, HOLDOUT-DTI, uniqueness, submit?.
- No number is labeled as a live score unless OWNER-REPORT or HOLDOUT-DTI.
- E3 not run (bar not beaten). Budget 2/3 experiments, ~2 minutes (under 2 hours).
- Remaining blockers: DrivenData login, GeoDAWN DEM for H-LAH, IR-01 holdout vs live, weekly-cap/selector, IR-LATTICE-01.
