# Repository review — 2026-10-30

## Decision

**No TIFF is approved to download or submit.** This review made no geological experiment, did not generate or edit a prediction raster, did not request a competition slot, and did not infer a leaderboard score. The active negative decision is unchanged.

The README's historical 0.2778 for GEMSDOE32 and the supplied 0.3195 / 0.4413 leaderboard claims remain unverified reports in this checkout: there is no submission-page receipt or organizer-confirmed score snapshot. The checkout's raster audit supports a narrower statement: the GEMSDOE32 prediction is exactly reproduced as the GEMSDOE25 D2.8 dots with dots within two pixels of the known-catalogue raster removed. That is a verified byte-derived transformation, not proof that the mask caused a higher official score. The current official metric/rules and exact score records could not be independently checked here.

## Review passes

### Pass 1 — repository and evidence inventory

- Confirmed the session branch is `arena/f9a8b377-gemsdoesass1` and the starting tree was clean.
- Read the project brief, README, next steps, prior reviews, run cards, registry inventory, and existing candidate slate.
- Confirmed nine focus-site summaries are built into the local site. They correctly withhold score estimates and upload approval when there is no receipt/validated estimate.
- Confirmed the stopped BGAC record is `negative`, has no raster SHA/name, reports zero slot usage, and was stopped by a pre-placement duplicate gate. H-PBSC and SWGB are separately documented as negative/withdrawn; their older positive language is superseded.
- Reviewed the already-preregistered 2026-10-29 slate; no candidate was newly invented or tested in this review. Its five candidates and relative rank remain qualitative research priorities, not score predictions.

### Pass 2 — reproduce checks and edge review

- Installed the pinned Python requirements in an ignored virtual environment.
- The complete suite passed: **56 tests**. Rasterio emitted 19 non-failing fixture/deprecation warnings.
- `python scripts/build_site.py` succeeded. `python scripts/verify_release.py` succeeded after updating the release manifest for this review.
- `git diff --check` succeeded.
- Found that `scripts/audit_history.py` unnecessarily required `data/official/sample_submission.tif` and `existing_faults.tif`, even though checksum-pinned copies already exist in `data/bridge/`. This blocked the documented lightweight history audit when the 419 MB official-feature mirror had not been restored. Added a fail-closed resolver: prefer `data/official`, otherwise use bridge files only after matching the upstream manifest's SHA256 and byte count. Added regression tests for the fallback and corrupted-input rejection.
- The full historical-raster audit was not rerun: the 414-raster `.cache/registry` payload is not present in this checkout. Its earlier recorded JSON is preserved; it was not represented as freshly recomputed.

### Pass 3 — requirements and scientific status

- Rechecked submission claims: no approved download is linked; all historical values are distinguished from organizer-confirmed scores; no “estimated score” is claimed; the no-NaN/range/grid requirements are documented as local export validation, not proof of portal acceptance.
- Rechecked the mandatory novelty rule: the documented calibration-lattice overlap obstruction is unresolved. No lattice exemption, jitter, alternate registry definition, dot placement, or packaging workaround was attempted.
- Rechecked the candidate slate: it does not validate without the shared holdout/cache and a resolved novelty policy. No candidate can properly be described as viable or higher scoring today.
- Rechecked source availability: the sandbox allows GitHub and Python package hosts, but not the named DrivenData/USGS/NLR/GDR/Dropbox domains. Official rules, current leaderboard receipts, and official raw data therefore remain unverified in this session; owner-hosted mirrors are not organizer authentication.

## Existing ranked hypotheses (not run in this review)

The following order is already recorded in [`knowledge/hypotheses_20261029.md`](../knowledge/hypotheses_20261029.md). “Potential” is qualitative and must not be read as a projected score.

| Rank | Candidate | Layers/signature | Why it might find an uncatalogued surface scarp | Main confounder / cost |
|---|---|---|---|---|
| 1 | H-SCARP-ASYM | Cached lidar step, coherence, relief, directional slope/curvature; one-sided cross-strike step plus along-strike coherence | Targets small, asymmetric piedmont scarps rather than generic openness ridges or mapped-trace proximity | Erosion, shorelines, terraces; low–medium cost |
| 2 | H-RAD-CONTACT-SCARP | K/Th radiometric gradients co-oriented with lidar step/coherence | A subtle scarp at an unmapped lithologic/cover boundary | Lithologic contacts and flight-line artifacts mimic faults; low cost |
| 3 | H-MAG-EDGE-TERMINATION | TMI-up150 edge topology/termination jointly with lidar scarp evidence | Short concealed structures may offset/terminate magnetic domains while creating a small surface break | Unrelated basement edges; low–medium cost |
| 4 | H-STRIKE-CONTINUITY-GAP | Fold-local visible-catalogue strike plus lidar step/coherence, with no simple trace continuation | Could recover isolated basin-interior segments not in the catalogue | Catalogue-derived leakage risk; medium cost |
| 5 | H-RAD-QUIET-SCARP | Radiometric texture/ratios as cover context plus lidar scarp evidence | Could prioritize subtle fault scarps under cover without relying on magnetic contrast | Background/survey texture confounding; low cost |

These are candidates from the existing repository slate, not newly verified geological discoveries. They use described cached layers and do not require proposing inaccessible new data. The ranking is a resource-allocation order, not a measured ranking. Do not start one until the explicit lattice-registry policy is resolved and an incumbent can be compared on the same holdout/evaluator.

## Open blockers and next actions

1. **Novelty-policy obstruction:** determine prospectively whether calibration/reference rasters count as registry submissions. Keep the literal current gate until a versioned, authorized policy decision; do not silently relax it.
2. **Fresh registry:** restore and refresh the complete nine-repository inventory at pinned commits before any future uniqueness claim. Other sites/private rasters remain outside that inventory.
3. **Official competition evidence:** obtain official data/rules/current leaderboard receipt in an authorized environment and record source URLs, timestamps, and hashes. Do not present user-provided numbers as confirmed.
4. **Comparable holdout incumbent:** once the policy allows a real test, preregister one of the listed hypotheses, reuse shared cached features/evaluator/writer, run per-feature leakage canaries, preserve all negatives, and compare with paired uncertainty before any selector decision.
5. **Current score tracking:** the GitHub source-head feed is not a competition leaderboard feed. Add an official receipt-driven score source only if it can be authenticated without exposing credentials.

## Trusted-source links for manual review

- [DrivenData competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DrivenData reference solution source](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE GDR / INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [Competition technical report PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

Links above are references for review, not claims those sites were reached or re-verified during this sandbox session.
