# Repository review — 2026-10-30 (thermal-lane release)

## Scope

Post-experiment packaging and release review for the H-TVGB lane. No historical negative
evidence was altered: `evidence/run_card.json` (BGAC-1), `evidence/pbsc/**`, `evidence/swgb/**`
and the two archived parallel-session manifests are unchanged. New evidence lives in
`evidence/thermal/`. Competition upload: none; weekly slots used: 0.

## Three-pass procedure

1. **Implement + verify.** Thermal lane E1/E2/E3 + final build (`scripts/run_thermal_lane.py`),
   release verifier (`scripts/make_release.py`), site generator (`scripts/build_site.py`),
   entry-point gates, tests. Every run output is an evidence JSON.
2. **Bug review.** Found and fixed: (a) `KeyError: 'rows'` in the final builder — the novelty
   audit returns `comparisons`; scan results are now cached per candidate digest; (b) the
   how-to-submit page rendered template expressions literally (missing f-string) — fixed and
   re-generated; (c) the first packaging (B2 emission cell) failed the literal lane-drift dots
   gate (79.1% of dots within 3 px of `gems25-h38-greedy-credit-k3p5-20261025-18de99d38bb0-nan.tif`,
   limit 70%). The artifact is kept on file and logged as a duplicate
   (`evidence/thermal/run_card_b2_duplicate_log.json`, `novelty_dots_b2.json`); the shipped
   artifact is the preregistered 600 m-exclusion cell (median catalogue distance 9.2 px vs the
   B2 cell's 5.7 px, matching the champion family's far-field habitat) and passes the same
   unchanged thresholds (dots max overlap 65.0% vs competitive registry; surface Spearman 0.133).
   The E3 far-field diagnostic ranks the 600 m cell above the 2 px cell at every sweep n
   (0.1343 vs 0.1192 at n=37,654), which is the independent scientific reason for the cell choice.
3. **Full re-check.** 55 pytest tests, 5 node feed tests, `build_site.py` + `swgb_build_site.py`,
   `verify_release.py`, `check_release_entrypoints.py`, `verify_swgb_correction.py`, then the
   generated-HTML byte gates.

## Documented test adaptations (protective intent preserved)

- `scripts/verify_swgb_correction.py`: the four SWGB pages keep the absolute ban on the approval
  phrase; the root entry point may state the generated release verdict only naming the
  run-card-approved raster (same rule as `check_release_entrypoints.py`). SWGB remains withdrawn.
- `tests/test_swgb_review.py`, `tests/test_pbsc_receipt.py`, `tests/test_pipeline.py`,
  `tests/test_release_review.py`: assertions updated to the 2026-10-30 release state — historical
  files stay revoked (`do not submit`, `ok_to_submit = false`, `withdrawn`); `docs/downloads` may
  hold the H-PBSC research artifact plus the thermal release and its superseded B2 log; the
  generated pages and download index may state the approval only for the run-card-approved raster.

## Release verdict (machine-computed)

- File: `docs/downloads/gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif`
- sha256: `d4061df68caf0e12eb7238088420178f6e9ebe1c56b121f2b9f401281088ee0b`
- HOLDOUT-DTI 0.1287 [0.1231, 0.1355] (bar 0.1011); far-field restricted 0.1343
- Lane-drift gates pass per-raster (IR-LATTICE-01 scope issue reported both ways in the run card)
- Verdict: **promote**; `ok_to_download_and_submit = true`; slots used 0.

## Post-review manifest

`evidence/release_checks.json` `implementation_sha256` recomputed for the reviewed files and
extended to the new gate scripts; `post_review_2026-10-30` records this review.
