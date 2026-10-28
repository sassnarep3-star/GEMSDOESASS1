# Three-pass review — 2026-10-27

## Pass 1 — inventory, implementation and execution

- Initial repository inspected: one 14-byte README; no pipeline, data, cached stack, website or previous-session next steps existed here.
- Read official DrivenData reference README/notebook from commit `aebe92f7c8a990f0e3443451b7a825d9afd6336b`. Retained source-only notebook transcript and README in knowledge/. This supports reference fault detection and training-loss facts, not current contest scoring/rules or leaderboard authentication.
- Restored and verified the owner bridge: feature stack, labels/catalogue, and template. Populated the shared band cache. Later verified cache reuse without recomputation.
- Pinned all 414 TIFF blobs outside data/ in the nine priority repos; verified byte size, Git blob SHA1 and SHA256. No 8 MB/name heuristic discarded prediction-like files. One incompatible format fixture and one nonfinite prior were recorded explicitly.
- Wrote four ranked hypotheses before implementing one fixed lane, BGAC-1. No additional data were needed for it. Deferred external-data ideas were not called viable without source verification.
- Ran one hypothesis with shared whole-component fixed-quadrant splits, 80 px training exclusion, exact visible-fault masking, feature AUC canaries, pooled DTI, same-run ablations, and physical-block paired confidence intervals. The numerical result was negative and dot novelty failed; no TIFF was packaged.
- H33-B2 was independently reproduced as the site-31 mask with 2,545 dots removed at catalogue distance <=2 px, no additions. Historical score reports were not upgraded to organizer confirmation.

## Pass 2 — protocol bugs found, corrected and disclosed

**Important first-pass defect:** the pre-placement novelty check applied rank correlation only, not literal positive-support overlap. It also continued after an unassessable prior prevented complete clearance. This did not follow the inherited template's strict surface gate.

- Fixed overlap at BOTH phases using the unmodified shared `vendor/gems57/uniqueness.dot_overlap` implementation.
- Fixed the runner to stop before placement unless the surface audit is fully cleared, not merely when rank duplicate is true.
- Preserved `first_pass_run_card.json`, original full rank scan, final-dot scan, canaries and numerical holdout. The first-pass numerical holdout is explicitly **EXPLORATORY HOLDOUT-DTI**, not protocol-qualified promotion evidence.
- Recomputed only the identical frozen surface for a corrective pre-placement audit. Its SHA256 matches. It is already a literal duplicate. No new dot placement, holdout, candidate or TIFF followed the correction.
- The first-pass application source was not committed before review. The unchanged BGAC builder and shared evaluator hashes are retained, along with raw receipts and the documented changes. The corrected runner intentionally cannot replay the disqualified execution without restoring the bug. Do not present that execution as a compliant reproducible promotion trial.
- No shared metric, evaluator or submission writer was changed or privately forked. The defect was in the new orchestration/gate, not in the shared arithmetic.
- Negative scientific conclusion unchanged: the exploratory paired difference against the strongest same-run ablation is below zero throughout its conditional interval. No promotion, upload or slot selection occurred.

## Pass 3 — edge cases, UI, auditability and release checks

- Fixed empty/constant candidate and empty-compatible-registry clearance edge cases. A zero/undefined-rank surface cannot clear.
- Fixed standalone history-audit imports after the shared geometry dependency was added.
- Added verified cache-hit reuse; the restored raw features are not reread into a rebuilt stack on every invocation.
- Verified history duplicates on actual footprint float32 predictions, not only file hashes. GEMSDOE25 and GEMSDOE30 best artifacts have identical predictions; GEMSDOE31 is also mirrored among site-28 and site-33 variants. Individual summaries distinguish same-array aliases from new submission eligibility.
- Built 13 pages: landing, executive/how-to, research/sources, evidence, and nine per-site executive summaries. Every opening decision is blocked. There is no invented download, file SHA256, file validator receipt or leaderboard projection.
- Built an automatic, advisory-only browser GitHub source-head feed with hourly caching, timeouts, no credentials, explicit failure states and no mutation of experimental decisions. Daily Actions snapshots are artifacts, not automatic commits/deployments.
- Attempt to switch Pages from legacy to Actions returned HTTP 403. Retained the already configured `main` / root legacy Pages setup with root entry links into docs/. Did not claim reconfiguration succeeded.
- **34 Python tests pass**: shared exact metric vs brute-force oracle; pixel-exact masking; globally aligned crop blocks; whole-component tails/buffer; pooled rather than averaged ratios; matched truth counts; tied-rank formula; emitter spacing/determinism; both-phase overlap; incomplete/invalid/empty priors; invalid values; note/name limits; atomic writer failures; full-grid TIFF/ZIP roundtrip in temporary test directories; frozen negative artifact contract.
- **5 JavaScript tests pass**: current heads; changed heads; HTTP failure; hourly cache; invalid/future cache; no feed requests on non-feed pages (some assertions share one test).
- **Rendered browser audit passes**: Chromium 153 via test-only npm package, 13 desktop pages at 1440×1000 and 4 mobile pages at 375×812; no page errors or page-wide horizontal overflow; correct nine-row table and disabled submission button. Screenshots inspected in workspace. Improved mobile table scrolling/focus without adding dependencies to the site. Runtime libraries are confined to the optional browser-test environment.
- Offline release verifier checks strict JSON, code/vendor hashes, all generated internal links, copied evidence identity, negative verdict, no phantom TIFF and no slot usage. Build is deterministic with the committed source-feed snapshot. `git diff --check` passes.
- Rasterio/affine emitted harmless PendingDeprecationWarnings in unit-test fixture/writer paths. No test failed; shared source was not edited merely to silence a dependency warning.

## Requirements that remain unmet — deliberately not hidden

| Requirement | Actual result / limitation |
|---|---|
| Generate a unique high-scoring competition TIFF | **Not achieved.** Literal duplicate-stop rule prohibits packaging this lane; the method also underperforms. No filename or jitter workaround was used. |
| Highest scoring / reliable leaderboard estimate | **Not established.** No organizer receipts/hidden truth/current official ranking. Owner reports are historical, not validated scores or forecasts. |
| Current holdout best comparison | No compatible prior experiment in this checkout. Strongest same-run ablation measured, but neither historical incompatible holdout numbers nor catalogue-informed frozen prior rasters were used as fair controls. |
| Official data and literature verification | Official GitHub reference read. Other official websites, rules PDF and supplied Dropbox are outside outbound allowlist. Mirror origin/licensing and rule eligibility not independently authenticated. No fabricated literature findings. |
| Unique across every GEMSDOE site / private submission | Scope is nine priority public repositories at frozen commits. Other sites, data/ blobs, unlinked and private files are outside this measured inventory. No universal uniqueness claim. |
| Executive summary on the nine separate deployed websites | Nine comparative subpages added **here**. No changes pushed to the nine upstream repositories. |
| Entire repeated prompt verbatim in README | Persistent deduplicated operational transcription in PROJECT_BRIEF, linked and summarized in README; explicitly not a verbatim archive. Original chat remains the complete literal record. |
| Continuously current official leaderboard feed | Not available. GitHub source freshness is automated, explicitly not a competition-score feed. |
| Submission without human visual inspection | Project gates are automatic. No candidate cleared. A future official account/slot authorization remains a separate competition access control, not visual inspection. |
| PR / merge / Pages | Repository delivery is separate from scientific promotion. Final PR/check/merge status is reported in the session response; Pages configuration change was denied. |

## Verdict

**Negative, stop.** Preserve the failed result and protocol correction. No competition artifact, no weekly slot, no unverified score claim. Next steps are ordered in knowledge/NEXT_STEPS.md; do not continue experimenting around the literal gate in this stopped lane.

### Freshness advisory at final review

The final GitHub-only source refresh observed GEMSDOE24 advancing from frozen `cf093c8c5e9fa77294ecf4c59b79cdade92cbc06` to `a1ecb683a9fda2aa4612f27e28896ebb8b19ad08`. The website marks registry re-audit required. The experiment remains tied to its frozen 414-file snapshot; no new experiment or clearance was inferred from the changed head. This is an additional reason not to treat historical inventory coverage as current global uniqueness.

### Concurrent main integration before PR merge

PR #3 reached main during this lane and introduced a separately negative synthetic weighted-Poisson research TIFF, historical documents and a run card. PR #6 initially conflicted on README and the two active landing/summary HTML files. All 14 changes from main `f620a70053d2f86eed6cadb0677e72d8605fb916` are preserved byte-for-byte in `archive/parallel-main-f620a70/original/`, with hashes and source paths. Original HTML is inert `.html.txt`. The current active pages retain this lane's stricter blocked status; the other TIFF/ZIP is learning-only, not repackaged, re-scored or endorsed. Its nine-champion uniqueness claim and projection are not promoted to full-registry clearance or a score. This integration was not another experiment. The frozen inventory remains an explicitly dated nine-external-site snapshot, not a claim to include every subsequently merged local artifact.

Main advanced a second time via PR #4 to `2f67facb5e822ec080ccbb8a85826c8d3bfd8166`. All 44 changed files from the original base are preserved with hashes in archive/parallel-main-2f67fac; this includes its useful independent negative witness audit and source tooling/tests. Its user-supplied historical ledger is retained additively in knowledge/. Current authoritative pipeline/site/gates remain one active version, with pytest.ini preventing archived source tests from executing accidentally. No foreign measured score, official-page claim, projection or experiment is silently adopted. This second integration is code/history preservation, not another geological experiment.

# 2026-10-28 correction — three review passes

1. **Reproduce / implement:** read both parallel lanes and the 414-raster inventory. Identified omitted GEMSDOE24 `inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif` in SWGB's 17-raster registry. Fetched its pinned Git blob through GitHub API, verified SHA256 `b4570b40...`, verified the existing SWGB TIFF SHA256 `f98c20df...`, compared same-grid positive supports with Euclidean 3 px distance. 44,033 / 44,090 = 99.8707% > 70%. Cross-checked the existing correction receipt and wrote an additional negative release card; no new TIFF or experiment.
2. **Bug/edge review:** discovered old SWGB builder could still regenerate a claimed approved TIFF, and site/root/README linked it with green submission CTAs despite the strict all-registry rule. Made builder fail closed, rewrote CTA and submission instructions to mark research-only, and added offline release checks to CI. Preserved historical cards for audit rather than rewriting old measurements.
3. **Recheck:** checked archived TIFF hash, correction numerator/denominator, on-disk format receipt and superseding release flag; ran Python/Node tests and original frozen BGAC release checks. Existing HOLDOUT-DTI is not a calibrated live score and cannot establish >0.2778. Remaining issue: current official rules and receipts inaccessible on this network; the lattice makes literal novelty impractical for almost all dots. No slot selected or spent.
