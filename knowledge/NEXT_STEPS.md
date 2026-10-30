# Next session — ordered actions

## 2026-10-30 update (review, no upload)

Review: [`docs/REPO_REVIEW_2026-10-30.md`](../docs/REPO_REVIEW_2026-10-30.md). Leaderboard and score conflicts: [`knowledge/leaderboard_evidence_20261030.md`](leaderboard_evidence_20261030.md).

- **Frozen registry is stale.** Nine focus repos moved after the 2026-10-27 pin; 74 TIFF blob identities (67 distinct contents) are new. The refreshed manifest [`registry/focus_inventory_20261030.json`](../registry/focus_inventory_20261030.json) (489 TIFFs, all blob-verified) is additive; the frozen manifest is untouched.
- **Negative candidates re-checked against the refreshed registry:** H-PBSC 99.48% and SWGB 99.87% directed overlap within 3 px, both duplicates. The positive control self-matches at 1.0. Receipt: [`evidence/registry_refresh_20261030.json`](../evidence/registry_refresh_20261030.json).
- **New first priority:** explicit owner decisions on (a) whether calibration/lattice rasters belong in the novelty registry (item 4 below) and (b) how the unassessable GEMSDOE31 `gemsdoe31-csdu-stepover-8cf9dc27-nan.tif` (2,610,312 non-finite footprint cells) is treated. Under the current code, (b) alone blocks every candidate.
- **Re-read the official leaderboard** from an environment that reaches drivendata.org, with a dated capture. The owner ledger's 0.4544 row (2026-10-28, labelled organizer-confirmed) is unverified and conflicts with the 0.4413 figure.
- **Do not use `scripts/registry_snapshot.py --refresh`** to update the registry: it overwrites the pinned manifest. Use `scripts/registry_refresh.py --out <new path>`.


**No file in this repository is authorized for upload.** H-PBSC, SWGB and BGAC are all negative under the literal 70%/3 px rule once the GEMSDOE24 calibration lattice is included.

1. **Do not upload H-PBSC.** HOLDOUT-DTI 0.0650 [0.0605, 0.0693] lost the 0.1011 bar. Versus 17 competitive rasters it is unique (max 3 px 25.3%). Versus the 13gems lattice it is **99.48%** within 3 px (37,460 / 37,654). Research TIF retained for audit only.
2. **Do not upload SWGB.** Main-branch lattice audit: 99.8707% (44,033 / 44,090). The 17-file “promote” is superseded (`evidence/swgb/release_decision.json`).
3. **Do not resubmit GEMSDOE32 `h33-h33-2-b2` (0.2778 OWNER-REPORT).** It is H19-5 dotted minus catalogue-proximal dots. Another prune cannot beat it.
4. **Resolve the lattice policy outside a stopped run.** The 5-px lattice covers ~99.87% of the footprint, so any competitive-size dotted file fails 70%/3 px. An explicit, versioned amendment is required before another packaging attempt. Do not silently omit calibration rasters.
5. **H-LAH shoreline suppression** still needs GeoDAWN `22103_dem_a1/a2.tif` (ScienceBase doi:10.5066/P93LGLVQ) — not on this sandbox allowlist.
6. **Official data still login-walled.** DrivenData features / 1 m DEM links; USGS GeoDAWN full grids. Outbound here: github.com, pypi.org.
7. Read the briefs + `evidence/pbsc/run_card.json` + `evidence/swgb/release_decision.json` first next session. Do not erase negative evidence.
