# Leaderboard and score evidence — 2026-10-30

Scope: every leaderboard or score figure that appears in the project brief, the owner repositories, the existing ledgers, or the official pages, with its evidence class. Nothing here is a forecast.

**Evidence classes used (same as the project brief):** `HOLDOUT-DTI` (our evaluator, with CI) · `ORGANIZER-CONFIRMED` (a submission-page receipt) · `OFFICIAL-LEADERBOARD-READ` (a dated read of the official public leaderboard, not a per-submission receipt) · `OFFICIAL-SNAPSHOT` (owner-cited leaderboard read, not re-read here) · `OWNER-REPORT` / `USER-REPORTED` (unverified).

**Access check (2026-10-30):** the bash sandbox cannot reach DrivenData, USGS, GDR, NLR or EPSG.io (curl `000`). The **fetch tool** can reach them. The leaderboard, competition page, rules page, NLR rules PDF, GDR and EPSG.io were read through the fetch tool on 2026-10-30. The owner `github.io` pages and USGS GeoDAWN were not re-tested with the fetch tool.

## Official leaderboard, fetch-tool read 2026-10-30

Source: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ (column "Best public"; the page's relative timestamps are not dated, so the read date is the fetch date, UTC 2026-10-30).

| Rank | Participant | Submissions | Best public score | Class |
|---|---|---|---|---|
| #1 | xiaofanhu | 35 | **0.4544** | `OFFICIAL-LEADERBOARD-READ` |
| #2 | cfld__ | 21 | 0.3916 | `OFFICIAL-LEADERBOARD-READ` |
| #3 | Batik Shirt Brothers | 60 | 0.3915 | `OFFICIAL-LEADERBOARD-READ` |
| #4 | BrandenKMurray | 35 | 0.3841 | `OFFICIAL-LEADERBOARD-READ` |
| #5 | op01 | 16 | 0.3642 | `OFFICIAL-LEADERBOARD-READ` |
| #48 | kpomazi | 35 | **0.3195** | `OFFICIAL-LEADERBOARD-READ` |

The top 50 rows were read (3 chunks). No row shows a GEMSDOE focus-site name. The owner's 0.2778 would fall below row 50, so it cannot be located in this read. Not verified.

## Leaderboard figures from the repo, the brief, and the owner ledger

| Figure | Value | As-of (as stated) | Where it appears | Evidence class in this repo | Irregularity |
|---|---|---|---|---|---|
| Rank-1 DARD (best public DW-Tversky) | 0.3195 | 2026-10-03 | Owner ledger [`docs/score-ledger.csv`](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/score-ledger.csv), row "rank-1 DARD" | `OWNER-REPORT` (owner-cited snapshot) | Stale. The user brief still calls 0.3195 "the highest score right now". The 2026-10-30 read puts 0.3195 at #48 under kpomazi, not DARD at #1. |
| Rank-1 xiaofanhu | 0.4413 | 2026-10-25 | Owner ledger row "rank-1 xiaofanhu … 30 submissions"; the user brief also cites 0.4413 as the current GEMSDOE high | `OWNER-REPORT` (owner-cited snapshot) | Superseded by the 2026-10-30 read (xiaofanhu 0.4544). |
| Rank-1 xiaofanhu, 33 submissions | 0.4544 | 2026-10-28T11:45:00Z (owner) | Owner ledger row "DrivenData-PublicLB-Top1" | Owner labels it `ORGANIZER-CONFIRMED`. **This repo does not adopt that label.** | Confirmed as a public leaderboard row by the 2026-10-30 fetch-tool read (35 submissions now). A leaderboard read is not a submission receipt, so the class is `OFFICIAL-LEADERBOARD-READ`. |
| Rank-3 | 0.3904 (2026-10-25 row) vs 0.3911 (2026-10-28 row) vs 0.3915 (2026-10-30 read, Batik Shirt Brothers) | — | Owner ledger, two reads; fetch read | `OFFICIAL-LEADERBOARD-READ` for 10-30 | Rank-3 changes between reads, which is expected on a live board. Flagged, not resolved. |

**Current position in this repo:** the highest *official* figure is **0.4544, #1 xiaofanhu**, from the fetch-tool read on 2026-10-30. Its class is `OFFICIAL-LEADERBOARD-READ`. It is not `ORGANIZER-CONFIRMED`. The 0.3195 figure is out of date (now rank 48).

## Owner-reported submission scores (focus nine)

| Site | Name supplied | Score supplied | Owner-ledger class | Verified here |
|---|---|---|---|---|
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | 0.2778 | `owner-report` (cites a DrivenData submission page on 2026-10-25) | **Bytes only.** The zeros file's sha256 matches the ledger prefix (`c55bafc470054e82…`, full `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9`). Format: float32, EPSG:32611, 3730×3292, 100 m, values {0,1}, no NaN, 37,654 positive cells. **No submission receipt is stored or reachable.** |
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 | `user-report` | Not verified |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 | `user-report` | Not verified |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 | `user-report` | Not verified |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 (also 0.2708, 0.2649, 0.2707) | `user-report` | Not verified |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 | `user-report` | Not verified |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 | `user-report` | Not verified |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 | `user-report` | Not verified |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 | `user-report` | Not verified |

Note the `-nan` suffix. Several owner files that the owner reports as scored carry NaN outside the footprint, so the owner's own reports do not establish that NaN outside the footprint is the cause of the user's "Predicted values must be in range [0, 1]" error. The cause is unknown; see the review.

## Irregularities for manual review

1. **Leaderboard figures in the repo are stale or conflicting.** The brief says both "0.3195 is the highest score right now" and "current GEMSDOE high 0.4413". The 2026-10-30 fetch read shows 0.4544 at #1 and 0.3195 at #48. Use the dated fetch read; keep the owner's older rows as history.
2. **0.4544 is labelled "ORGANIZER-CONFIRMED" by the owner** although the row is a leaderboard read. The 2026-10-30 read confirms the leaderboard row. It is still not a submission-page receipt, so this repo keeps the class `OFFICIAL-LEADERBOARD-READ`.
3. **The same prediction appears under two nodata fills in the registry.** The GEMSDOE24 `24GEMSDOE-ventrad-blind-geothermal-20261028-34b558b554fb-zero.tif` and `…-nan.tif` files have identical values inside the footprint (checked 2026-10-30) and differ only outside it (0 vs NaN). Both are registry rasters, so a uniqueness check must treat them as one prediction. The owner ledger does not list this pair.
4. **Frozen uniqueness registry is stale.** Since the 2026-10-27 snapshot, all nine focus repositories have advanced and contain 74 new TIFF blob identities (67 distinct file contents). See [`evidence/owner_head_drift_20261030.json`](../evidence/owner_head_drift_20261030.json) and [`evidence/registry_refresh_20261030.json`](../evidence/registry_refresh_20261030.json).
5. **Public leaderboard is not the final ranking.** The column is "Best public". Rules §3.2 say public scores "may not be the same as" the final private scores. Phase 1 ranks on a private test set (§3.6.2). Phase 2 ranks on a re-labelled set.

## Sources

- Official leaderboard, fetch-tool read 2026-10-30: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Official rules PDF (September 2026): https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Owner score ledger (GitHub, `main`): https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/score-ledger.csv
- GEMSDOE32 repository metadata (GitHub API, pushed 2026-10-29T18:23:11Z): https://api.github.com/repos/buffedlizard55-lab/GEMSDOE32
- Official competition data page (not fetched in this pass): https://www.drivendata.org/competitions/306/competition-doe-gems/data/
