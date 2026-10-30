# Repository review — 2026-10-30 (branch `arena/0fa98dd2-gemsdoesass1`)

Scope: verify the repo's claims line by line, run the checks, check the nine focus sites and the shipped TIFF, and flag irregularities. No experiment was run, no raster was generated, and no competition slot was used.

## Executive decision

**No TIFF is approved for submission. Do not download or submit any file from this repository.** The repo's own gates say so, and this review confirms it. Requests for a "unique, downloadable, scoring-ready TIFF" cannot be met honestly in this session, for the reasons below. A TIFF that fails the novelty gate would be a duplicate, and the user has explicitly ruled that out.

## What was verified (commands run, results)

| Check | Command | Result |
|---|---|---|
| Pinned environment | `pip install -r requirements-lock.txt` (venv `.venv`, git-ignored) | installed, exit 0 |
| Test suite | `.venv/bin/pytest -q` | **54 passed**, 19 warnings (the prior review recorded 53; the count has grown since) |
| Release verifier | `.venv/bin/python scripts/verify_release.py` | PASS: frozen negative release, 9 site summaries, 182 local links, strict JSON, vendor/code hashes, no submission TIFF, no slots |
| Shipped TIFF, independent read | rasterio on `docs/downloads/gemsass1-pbsc-playa-…-zeros.tif` | EPSG:32611, shape (3730, 3292), float32, single band, no nodata, transform (243350, 100, 0, 4508550, 0, −100), all finite, values {0, 1}, 37,654 positives. sha256 `2f3bd24e…47fd9` matches `docs/downloads/…checks.json`. |
| Focus repos reachable | `gh api repos/buffedlizard55-lab/GEMSDOE{24,25,27,28,30,31,32,33,36}` | all 9 reachable, default branch `main` |
| Historical 0.2778 file exists | `gh api …/GEMSDOE32/git/trees/HEAD?recursive=1` | `docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` present (plus `-nan.tif`, `-audit.json`). **File existence is verified; the score is not.** |
| GEMSDOE32 score label | fetched `docs/index.html` of GEMSDOE32 | its own page labels 0.2778 as **"OWNER-REPORT (owner-provided submission-log claim; no submission-page receipt)"**. Treat it as unverified. |

Not verified, because the sandbox allowlist excludes these hosts: the DrivenData competition page, leaderboard, rules, weekly cap, and data downloads (USGS, GDR/OpenEI, NLR, Dropbox). Official scores and rules in this review are therefore **not** ORGANIZER-CONFIRMED.

## Nine focus sites (GitHub API, 2026-10-30)

| Site | Default branch | Last push (UTC) | Notes |
|---|---|---|---|
| GEMSDOE24 | main | 2026-10-29 17:52:55 | |
| GEMSDOE25 | main | 2026-10-29 22:50:10 | |
| GEMSDOE27 | main | 2026-10-29 16:54:16 | |
| GEMSDOE28 | main | 2026-10-29 17:22:38 | |
| GEMSDOE30 | main | 2026-10-29 17:22:39 | |
| GEMSDOE31 | main | 2026-10-29 18:43:29 | |
| GEMSDOE32 | main | 2026-10-29 18:23:11 | contains the 0.2778 owner-report file |
| GEMSDOE33 | main | 2026-10-29 18:38:47 | |
| GEMSDOE36 | main | 2026-10-29 18:44:33 | |

The repos were last pushed on 2026-10-29, so the registry snapshot that this repo audits may be stale. The 2026-10-29 review already flagged this.

## Irregularities for review (flagged, not fixed)

1. **Bridge "sample_submission.tif" contains the answer.** `data/bridge/sample_submission.tif` (sha256 `2176d08e…35cbc`) has 60,988 pixels equal to 1. Those pixels are *identical* to the positives of `data/bridge/existing_faults.tif` (overlap 60,988 / 60,988). Its NaN pattern equals the faults-outside-footprint pattern. Its origin is not documented. If it is a derived product rather than an organizer sample, any code that treats it as neutral template or as a non-leaking reference is leaking catalogue information. `src/gems/grid.py` describes it as a mirror of the organizer template, and the grid constants (CRS, shape, transform, footprint) are taken from it. That mirror claim is unverified: the organizer template was not available here, and the file's positives are the catalogue. The file is used as the grid reference in `scripts/audit_swgb_witness.py`, `scripts/audit_swgb_lattice_witness.py`, and `vendor/gems57/evaluator_provenance.py`. **Needs owner decision: confirm provenance; if it is derived, use only its grid and footprint, never its positives.**
8. **`scripts/audit_history.py` fails on a clean checkout.** It reads `data/official/sample_submission.tif` and `data/official/existing_faults.tif`. Neither file exists (`data/official/` is absent), and the run exits with `RasterioIOError`. The README lists this script as a reproduce step. Verified by running it.
2. **`data/` is git-ignored but tracked.** `.gitignore` lists `data/`, yet five `data/` files are committed (`git ls-files data`). Intentional or not, the ignore rule does not protect them.
3. **Stale branch name in the prior review.** `docs/REPO_REVIEW_2026-10-29.md` says the review ran on `arena/bdfce0a1-gemsdoesass1`. This branch is `arena/0fa98dd2-gemsdoesass1`.
4. **Stale test count.** The 2026-10-29 review says 53 tests passed; 54 pass today.
5. **Contradictory leaderboard figures in the user's prompt.** The prompt cites 0.2778 as the highest GEMSDOE score, 0.3195 as "the highest score right now", 0.4413 as the "current competition leaderboard GEMSDOE high score", and 0.2778 as "highest". These cannot all be correct. None is ORGANIZER-CONFIRMED in this repo. The leaderboard URL (drivendata.org) could not be reached from the sandbox to resolve this.
6. **Conflicting instructions about downloads.** The user asks for "an easy to download submission tif". The repo's README and `docs/downloads/README.md` say "Do not submit any TIFF from this repository", and the site labels the only TIFF "DO NOT SUBMIT". The repo's position is the safer one and is kept. The user needs to know the gate is the reason, not a missing download link.
7. **Lattice policy is unresolved.** The calibration lattice in the registry covers ~99.5–99.9% of the footprint within 3 px. Under the literal 70%/3 px rule, competitive-size dotted rasters fail. This is the single biggest blocker and the repo correctly does not relax it.

## Why no new TIFF was generated

- Every existing candidate has failed a gate: H-PBSC lost its holdout (0.0650 vs bar 0.1011) and overlaps the lattice 99.48%; SWGB overlaps 99.87%; BGAC stopped on novelty.
- A new candidate would need the lattice policy resolved first, and that is a policy decision outside an automated run. Repeating the experiment without it would produce another duplicate.
- Without the official data (login-walled) the holdout cannot be checked against the organizer's features, so any new holdout DTI would be a proxy.
- Leaderboard score estimates remain **unavailable**. Holdout DTI is not calibrated to leaderboard DTI.

## Recommended next steps (in order)

1. Owner decision on the lattice/novelty policy, written as a versioned, prospective amendment. Do not change the threshold to clear an existing file.
2. Confirm the provenance of `data/bridge/sample_submission.tif` and mark it template-only or remove the positives (irregularity 1).
3. Obtain the organizer data and rules from an authorized environment (DrivenData login), and record hashes and receipts.
4. Refresh the nine focus-site registries at current heads and rerun the surface and dot novelty checks.
5. Only after 1–4: generate a candidate with the shared writer, validate its bytes, and keep selection and upload as a separate authorized step.

## Limitations

- The sandbox allowlist excludes DrivenData, USGS, GDR, NLR and Dropbox, so official inputs and the leaderboard cannot be verified here.
- The repo's historical scores are owner reports unless a submission-page receipt is recorded.
- This review found no scientific reason to expect a new candidate to beat 0.2778, 0.3195, or 0.4413. It also did not test one.
