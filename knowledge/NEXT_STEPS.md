# Next session — ordered actions

**Latest (2026-10-30): read [`RESULTS_20261030.md`](RESULTS_20261030.md) first.** H-TSFX holdout passed (0.1587; sweep 0.1674, selected on holdout) but the shipped dots are a duplicate of GEMSDOE25 (70–72 % within 3 px). **Nothing is approved for upload.** Next: design a registry-distinct emission geometry and a single full-catalogue model, pre-register them, and run held-out emission selection before any packaging.


**No file in this repository is authorized for upload.** H-PBSC, SWGB and BGAC are all negative under the literal 70%/3 px rule once the GEMSDOE24 calibration lattice is included.

1. **Do not upload H-PBSC.** HOLDOUT-DTI 0.0650 [0.0605, 0.0693] lost the 0.1011 bar. Versus 17 competitive rasters it is unique (max 3 px 25.3%). Versus the 13gems lattice it is **99.48%** within 3 px (37,460 / 37,654). Research TIF retained for audit only.
2. **Do not upload SWGB.** Main-branch lattice audit: 99.8707% (44,033 / 44,090). The 17-file “promote” is superseded (`evidence/swgb/release_decision.json`).
3. **Do not resubmit GEMSDOE32 `h33-h33-2-b2` (0.2778 OWNER-REPORT).** It is H19-5 dotted minus catalogue-proximal dots. Another prune cannot beat it.
4. **Resolve the lattice policy outside a stopped run.** The 5-px lattice covers ~99.87% of the footprint, so any competitive-size dotted file fails 70%/3 px. An explicit, versioned amendment is required before another packaging attempt. Do not silently omit calibration rasters.
5. **H-LAH shoreline suppression** still needs GeoDAWN `22103_dem_a1/a2.tif` (ScienceBase doi:10.5066/P93LGLVQ) — not on this sandbox allowlist.
6. **Official data still login-walled.** DrivenData features / 1 m DEM links; USGS GeoDAWN full grids. Outbound here: github.com, pypi.org.
7. Read the briefs + `evidence/pbsc/run_card.json` + `evidence/swgb/release_decision.json` first next session. Do not erase negative evidence.
