# Leaderboard and score evidence — 2026-10-30

Scope: every leaderboard or score figure that appears in the project brief, the owner repositories, or the existing ledgers, with its evidence class. Nothing here is a forecast.

**Evidence classes used (same as the project brief):** `HOLDOUT-DTI` (our evaluator, with CI) · `ORGANIZER-CONFIRMED` (a submission-page receipt) · `OFFICIAL-SNAPSHOT` (a leaderboard read, not a per-submission receipt) · `OWNER-REPORT` / `USER-REPORTED` (unverified).

**Access check (2026-10-30, this sandbox):** the DrivenData leaderboard, competition pages, USGS, GDR, NLR and EPSG.io returned no HTTP response (curl exit `000`), so none of the leaderboard figures below could be re-read here. The owner `github.io` pages also returned `000`. Only `github.com`, `api.github.com` and `codeload.github.com` responded. Everything below is therefore either from a repository file (checked by hash or by API) or from the user's brief.

## Leaderboard figures

| Figure | Value | As-of (as stated) | Where it appears | Evidence class in this repo | Irregularity |
|---|---|---|---|---|---|
| Rank-1 DARD (best public DW-Tversky) | 0.3195 | 2026-10-03 | Owner ledger [`docs/score-ledger.csv`](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/score-ledger.csv), row "rank-1 DARD" | `OFFICIAL-SNAPSHOT` as labelled by the owner; not re-read here | Stale. The user brief still calls 0.3195 "the highest score right now". |
| Rank-1 xiaofanhu | **0.4413** | 2026-10-25 | Owner ledger row "rank-1 xiaofanhu … 30 submissions"; the user brief also cites 0.4413 as the current GEMSDOE high | `OFFICIAL-SNAPSHOT` as labelled by the owner | The same row says it supersedes "then 0.3195-0.3262". The 0.3262 value appears nowhere else in this repo. |
| Rank-1 xiaofanhu, 33 submissions | **0.4544** | 2026-10-28T11:45:00Z | Owner ledger row "DrivenData-PublicLB-Top1" | Owner labels it `ORGANIZER-CONFIRMED public leaderboard row (no file attribution)` | **Not adopted.** A leaderboard read shows a public row; it is not a submission-page receipt that links bytes to a score. Also absent from this repo's executive summary, which still shows 0.4413. |
| Rank-3 | 0.3904 (2026-10-25 row) vs 0.3911 (2026-10-28 row) | — | Owner ledger, two reads | `OFFICIAL-SNAPSHOT` | Two reads disagree on rank-3. Possibly a real change, possibly a transcription error. Flagged, not resolved. |
| 0.3195 at rank 26 | 0.3195 | 2026-10-28 row | Owner ledger row "#26 kpomazi 0.3195" | — | Consistent with a reshuffle, but the same value was rank 1 on 2026-10-03. Needs a dated re-read. |

**Current position in this repo:** the highest leaderboard figure with a stated official-snapshot date is **0.4413 (2026-10-25)**. The owner ledger also contains **0.4544 (2026-10-28)**, which this repo cannot confirm. The 0.3195 figure is out of date.

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

1. **Two leaderboard reads disagree on rank-3** (0.3904 vs 0.3911), and the 0.3195 value moves from rank 1 to rank 26 within 25 days. Re-read the official page with a dated capture.
2. **0.4544 is labelled "ORGANIZER-CONFIRMED" by the owner** although the row is a leaderboard read. It needs a submission-page receipt before this repo can use that label.
3. **The brief says both "0.3195 is the highest score right now" and "current GEMSDOE high 0.4413".** Both cannot be current. The later dated figure (0.4413 on 2026-10-25, or 0.4544 on 2026-10-28) supersedes 0.3195.
4. **The same prediction appears under two nodata fills in the registry.** The GEMSDOE24 `24GEMSDOE-ventrad-blind-geothermal-20261028-34b558b554fb-zero.tif` and `…-nan.tif` files have identical values inside the footprint (checked 2026-10-30) and differ only outside it (0 vs NaN). Both are registry rasters, so a uniqueness check must treat them as one prediction. The owner ledger does not list this pair.
5. **Frozen uniqueness registry is stale.** Since the 2026-10-27 snapshot, all nine focus repositories have advanced and contain 74 new TIFF blob identities (67 distinct file contents). See [`evidence/owner_head_drift_20261030.json`](../evidence/owner_head_drift_20261030.json) and [`evidence/registry_refresh_20261030.json`](../evidence/registry_refresh_20261030.json).

## Sources

- Owner score ledger (GitHub, `main`): https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/score-ledger.csv
- GEMSDOE32 repository metadata (GitHub API, pushed 2026-10-29T18:23:11Z): https://api.github.com/repos/buffedlizard55-lab/GEMSDOE32
- Official leaderboard (not reachable from this sandbox): https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Official competition data page (not reachable from this sandbox): https://www.drivendata.org/competitions/306/competition-doe-gems/data/
