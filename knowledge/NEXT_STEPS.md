# Next session — ordered actions

## 2026-10-30 update (read first)

1. **Eligibility first.** The official rules (§1.3) restrict competitors to U.S. citizens or permanent residents, or U.S.-incorporated entities. The user's location is Singapore. Confirm eligibility with the prize administrator before any upload, and do not sign the eligibility certification unless it is true.
2. **Policy decision (blocker).** The literal 70%/3 px rule against the GEMSDOE24 calibration lattice caps any passing file at 22,163 positive pixels (measured). It cannot separate duplicates from noise (random placement overlaps at 0.9987). Options for the user to decide, each needing a versioned amendment: (a) keep the literal rule, which blocks all competitive files; (b) use excess overlap over the random-placement null, where the 0.2778 raster has an excess of about 0.0005 (observed 0.9992 against a null mean of 0.9987), a threshold that would have to be fixed in advance; (c) exclude calibration lattices as a category with a stated reason. No option has been applied.
3. **Do not resubmit any of the nine best files.** Each is already a previous submission, and several are byte-identical dot sets under different site names.
4. **Restore the core data** if validation is to proceed: `scripts/prepare_data.py` (about 421 MB) plus the external lidar and GeoDAWN layers listed under `external` in `registry/upstream_data_manifest.json`. Mirror hashes are verified; it is not organizer-authenticated.
5. **Top hypothesis: H-BASEMENT-STEP-GRAD** (`knowledge/hypotheses_20261030.md`). Pre-register it, run the single-feature canary, then the holdout against the 0.2600 family incumbent. Not run this session.
6. **Verified sources and irregularities:** `knowledge/sources_verified_20261030.md`.

---

## Earlier plan (2026-10-28, still valid)

**No file in this repository is authorized for upload.** H-PBSC, SWGB and BGAC are all negative under the literal 70%/3 px rule once the GEMSDOE24 calibration lattice is included.

1. **Do not upload H-PBSC.** HOLDOUT-DTI 0.0650 [0.0605, 0.0693] lost the 0.1011 bar. Versus 17 competitive rasters it is unique (max 3 px 25.3%). Versus the 13gems lattice it is **99.48%** within 3 px (37,460 / 37,654). Research TIF retained for audit only.
2. **Do not upload SWGB.** Main-branch lattice audit: 99.8707% (44,033 / 44,090). The 17-file “promote” is superseded (`evidence/swgb/release_decision.json`).
3. **Do not resubmit GEMSDOE32 `h33-h33-2-b2` (0.2778 OWNER-REPORT).** It is H19-5 dotted minus catalogue-proximal dots. Another prune cannot beat it.
4. **Resolve the lattice policy outside a stopped run.** The 5-px lattice covers ~99.87% of the footprint, so any competitive-size dotted file fails 70%/3 px. An explicit, versioned amendment is required before another packaging attempt. Do not silently omit calibration rasters.
5. **H-LAH shoreline suppression** still needs GeoDAWN `22103_dem_a1/a2.tif` (ScienceBase doi:10.5066/P93LGLVQ) — not on this sandbox allowlist.
6. **Official data still login-walled.** DrivenData features / 1 m DEM links; USGS GeoDAWN full grids. Outbound here: github.com, pypi.org.
7. Read the briefs + `evidence/pbsc/run_card.json` + `evidence/swgb/release_decision.json` first next session. Do not erase negative evidence.
