# Verified sources and irregularities — 2026-10-30

Every claim below was read from a page fetched in this session (dates are the fetch date, 2026-10-30, UTC). Nothing here is ORGANIZER-CONFIRMED unless a row says so. Links are for manual review.

## Official sources read this session

| # | Source (official) | What was verified | Notes |
|---|---|---|---|
| 1 | DrivenData problem page, metric and submission format: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/> | DTI = TP_w / (TP_w + α·FP_w + β·FN_w), α = 0.2, β = 0.8, triangular kernel with R = 300 m (3 px at 100 m). Submission: single float32 layer, EPSG:32611, 100 m, same bounds, data outside bounds null or NaN, values in [0, 1]. | Matches `src/gems/metric.py`, which was checked line by line against the formulas (TP per truth pixel = max p·k; FP = Σ p·(1 − max k); FN = |G| − TP). |
| 2 | DrivenData leaderboard: <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/> | Public DW-Tversky, top rows: #1 **0.4544**, #2 0.3916, #3 0.3911, #4 0.3841, #5 0.3642; #49 **0.3195**; #50 **0.3169** (last row shown). | **0.4413 does not appear** in the 50 rows shown. **0.2778 does not appear** (below #50). The page shows relative times only, so this is a snapshot, not a timestamped record. |
| 3 | DrivenData data page: <https://www.drivendata.org/competitions/306/competition-doe-gems/data/> | Redirects to the login page. | Confirms the user's login-wall note. Data was taken from the pinned GitHub mirror instead, with hashes checked (see `registry/upstream_data_manifest.json`). |
| 4 | DrivenData rules page: <https://www.drivendata.org/competitions/306/competition-doe-gems/rules/> | Points to HeroX resource 2274. | — |
| 5 | HeroX resource 2274: <https://www.herox.com/GEMSPrize/resource/2274> | Points to the official rules PDF below. | — |
| 6 | **Official GEMS Prize Rules** (DOE/NLR, September 2026): <https://www.nlr.gov/docs/fy26osti/96647.pdf> | See the rules table below. Chunks 0–5 of 7 were read; chunk 6 (definitions and platform) was not. | — |
| 7 | GeoDAWN release, DOI 10.5066/P93LGLVQ: <https://doi.org/10.5066/P93LGLVQ> | Cited by the rules §2 as the feature source. | Not fetched this session. |
| 8 | INGENIOUS Great Basin compilation, DOI 10.15121/1881483: <https://doi.org/10.15121/1881483> | Cited by the rules §3.3 as the label source. | Not fetched this session. |

Earlier sessions also cited the community thread on known-fault masking (<https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516>) and the reference solution. **Neither was re-fetched this session.** Both remain in `knowledge/sources.json` as previously recorded.

## What the official rules say that matters here

| Rule (section) | Text, paraphrased closely | Consequence |
|---|---|---|
| Eligibility §1.3 | Individuals must be U.S. citizens or permanent residents. Private entities must be incorporated in, and have a primary place of business in, the U.S. Academic institutions must be U.S.-based. Eligibility is verified before prizes are awarded. | **The user's listed location is Singapore (SG). Eligibility must be confirmed with the prize administrator before any upload.** This session cannot determine nationality, residency or entity status. |
| Certification §1.3 and A.1 | The registrant signs a statement, under penalty of perjury, that the named competitor meets the eligibility requirements. | Do not sign unless it is true. |
| Submission limit §3.2, §3.4 | Up to **three** scoring submissions per week. | The weekly cap is 3, as the user noted. |
| One final entry §1.1, §3.4, §3.5 | Competitors choose **one** final submission before the deadline. | Selection is a separate decision. This repo does not pick submissions. |
| Automatic scoring §3.5, §3.6.1 | Scoring is automatic on the platform. The public score is shown on the leaderboard. | Scoring has no human step. |
| Human judgment §3.6.4, A.13 | A DOE judge makes the final winner determination, taking into account policy factors. Those factors include "technological or programmatic diversity when compared to … other competitors." | Uniqueness is also a formal award factor, not only a gate. Human review applies to prize determination, not to format validation or scoring. |
| Format screen A.1 | The administrator may disqualify after initial screening for missing required elements, and may let the competitor fix non-substantive errors. | Format is screened by the administrator. |
| Foreign-interference review A.12 | DOE may run a risk review that can eliminate a submission, and the elimination is not appealable. | Eligibility and review risk are separate from the technical gate. |
| Generative-AI disclosure §3.2 | Use of generative AI is allowed, but the extent and manner of use must be disclosed in the narrative. | Any submission narrative must disclose AI use. |

## Irregularities for manual review

1. **The user's "highest score" figures conflict with the official snapshot.** The user cites 0.3195 as the highest score and also 0.4413 as the leaderboard high. On 2026-10-30 the public leaderboard shows #1 = 0.4544, and 0.3195 is rank #49. Neither 0.4413 nor 0.2778 appears in the top 50.
2. **Eligibility risk.** Singapore-based location versus the U.S.-only eligibility in §1.3. See the table above.
3. **Identical predictions submitted under different site names with identical owner scores.** The GEMSDOE25 file `dotted-h19-5-d2-8` and the GEMSDOE30 file `d28-poisson300m-offcat-44090` have the same positive-pixel set, and both carry owner score 0.2600. The registry has 164 exact dot-set groups, 6 of them spanning sites (`evidence/nine_site_board.json`, `exact_duplicates`).
4. **Probe files with identical dot sets.** GEMSDOE32 contains `gems25-dotted-h19-5-d2-8-…` (both variants), `gems32-probe-S1-ANCHOR-identical-to-live-02600` and `gems32-probe-S2-SCALE-lambda-0.5`. All four have the same positive-pixel set as the GEMSDOE25 file, so the 'probes' did not change the dots. The names suggest they were meant to differ.
5. **GEMSDOE30 has two names for one dot set.** The ledger name has no suffix. The plain file and the `-nanoutside` file carry the same positive pixels. The board uses the plain file, and records the choice.
6. **The "Predicted values must be in range [0, 1]" rejection is not reproduced.** All nine best files pass the official format text in `evidence/format_validation_nine_best.json`. This includes the NaN-outside variants, which the official text allows. The cause of the portal error is unknown. The zeros-outside variant avoids NaN entirely, so it is the lower-risk choice if the portal rejects NaN.
7. **The GEMSDOE13 calibration lattice** (`13gems_20261001_r13-lattice-s5_v2_nan-outside.tif`, 206,895 dots, submitted at owner-reported 0.0904) is a registry raster under the literal rule. Random placement of 37,654 dots overlaps it at a mean of 0.9987, so the literal test cannot separate duplicates from noise.
8. **The 2026-10-29 candidate slate depends on layers not in the cached 19-band stack** (`lidar step_max`, `coh100`, `relief`, `rad_K`, `rad_ThK`, `TMI_up150`). The manifests exist and the layers are listed in the pinned mirror (`registry/upstream_data_manifest.json`, group `external`). They are **not restored locally**. Restoring them needs the pinned GitHub mirror, which is allowed. USGS and ScienceBase are not on the sandbox allowlist, so those sources cannot be fetched directly from here.
9. **Holdout DTI does not rank live scores.** Spearman −0.081 across 17 registry rasters, Pearson 0.270 (`evidence/swgb/holdout_calibration.json`). The caveat there says registry holdouts may be optimistic, because those rasters were built with the full catalogue visible.
10. **A file from an archive folder is in the registry.** `GEMSDOE33/archive/legacy_candidates/gems33-c0-scored-reference-20261004-89bf5b9a2fea.tif` is byte-identical in dot set to the GEMSDOE31 and GEMSDOE28 `h27-4` family. It is in the frozen inventory, so it is counted.

## Verification log (commands that were run)

- `scripts/registry_snapshot.py` restored all 414 registry rasters from pinned blob SHAs (345 MB).
- `scripts/nine_site_board.py` produced `evidence/nine_site_board.json`. It checks each best file's SHA-256 against the inventory, checks grid identity, and cross-checks the KD-tree overlap against the shared `dot_overlap` (agreement required).
- `scripts/validate_format.py` produced `evidence/format_validation_nine_best.json` (9 of 9 pass).
- `tests/test_nine_site_board.py` (6 tests) and the existing 54 tests pass.
- `scripts/verify_release.py` passes. The frozen 2026-10-27 review hashes are kept unchanged. The post-review changes are pinned in `evidence/release_checks.json` under `post_review_2026-10-30_implementation_sha256`.
