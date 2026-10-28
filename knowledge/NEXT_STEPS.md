# Next session — read the release correction first

The former SWGB recommendation is revoked. See [2026-10-28 review](RELEASE_REVIEW_2026-10-28.md): the actual TIFF fails the literal expanded-registry novelty gate. Its build and site generators are blocked. No slot should be spent. Preserve the old SWGB evidence as historical, not an approval.

# Next session — ordered actions

1. **Resolve the novelty-policy obstruction outside this stopped run.** The 5-pixel lattice in `GEMSDOE24/inputs/calibration` is within 3 pixels of 99.8713% of the footprint and 100% of BGAC-1 dots. Never silently exclude it or change 70%/3 px. The strict protocol leaves no basis for manufacturing a submission-ready TIFF now. Any future amendment must be explicit, versioned and preregistered.
2. **Obtain independent official evidence, not credentials.** Needed: official competition input hashes/template, current metric/rules PDF, live weekly cap, and submission-page receipts tying historical filenames and hashes to results. DrivenData/USGS/GDR/NLR/Dropbox are not in this sandbox's outbound allowlist. A future environment with authorized public-source access or supplied files/receipts is needed. No passwords or tokens should be placed in chat.
3. **Establish a compatible incumbent holdout best.** The original checkout had no experiment. Historical frozen predictions were built using the full catalogue and are not fair same-instrument hide/recover controls. Port their actual builders with visible-only catalogue features, or use a fully reproducible label-free incumbent on the identical fixed folds/budget. Do not reuse historical numeric holdout bars from different instruments.
4. **Investigate source coupling.** Basement depth may be derived from gravity. The failed signed-opposition hypothesis could simply select the same inversion geometry twice; it is not evidence from independent instruments. AUC canaries do not establish feature independence or absence of source leakage.
5. **Audit deferred hypotheses before testing.** The ranked ideas in `hypotheses.md` are not scientifically established, globally novel or validated. Check raw layer definitions and official free availability. In particular, radiometric quantization/coverage and conductivity source resolution require verification.
6. **Extend registry scope.** This run covers all 414 TIFF blobs outside `data/` in the nine priority repositories at frozen commits, not all 90+ sites mentioned in chat or inaccessible submissions. Repair or obtain a valid counterpart for the nonfinite GEMSDOE31 prior. Do not convert an incomplete scope to a blanket uniqueness claim.
7. **Only after the above: one new preregistered experiment.** Preserve BGAC-1's negative evidence. Continue using the shared cached stack, whole-component buffered folds, feature canaries, pooled DTI and physical-block paired intervals. Stop at three experiments/two hours, or immediately on duplication.
8. **Packaging and selector.** An eventual candidate must pass all automated gates, then receive a separate selector decision under the verified weekly cap. Publish a one-click all-finite TIFF, exact SHA256, unique name/note <=140 characters, validator receipt and immutable run card. Keep `approved_for_submission=false` until the release decision exists. No portal upload belongs in the research runner.

## Website operations

- Check the existing legacy `main` / root Pages deployment after merge. Attempting to switch Pages to Actions returned HTTP 403; do not claim that reconfiguration succeeded. Root entry links into docs/. Checks run in Actions if repository policy permits.
- The browser automatically checks public GitHub commit heads with a one-hour cache; API/rate-limit failures are explicit. Daily Actions snapshots are advisory artifacts, not automatic Pages deployments or commits.
- The source feed reports GitHub commit changes only. It cannot update a verified competition leaderboard from this network.
- Nine-site summaries here do not modify the nine separate upstream repositories. Updating their own landing pages would require a separate authorized cross-repository release.
- Read README + PROJECT_BRIEF + the frozen run card first, every session.

## 2026-10-28 SWGB correction (takes precedence over the earlier SWGB slot suggestion)

The earlier SWGB approval is **withdrawn**: its 17-file registry omitted a pinned GEMSDOE24 calibration lattice. Independently rerunning the exact raster overlap on the preserved SWGB TIFF found 44,033/44,090 dots within 3 px of the lattice (99.8707% > 70%). `evidence/swgb_lattice_audit.json` and `evidence/swgb/release_decision.json` supersede the old SWGB `run_card.json` promotion. The legacy builder is now fail-closed; all landing pages say NOT OK TO SUBMIT. No new experiment, TIF, or portal slot was used. Do not submit the preserved research TIFF.

Before attempting another research run, resolve the literal all-registry lattice obstruction with an explicit versioned policy amendment **outside this stopped run**; don't quietly omit calibration rasters, restrict the registry to scored files after the fact, or change thresholds. Verify official data/licensing/weekly cap and receipts in an environment with access to organizer resources. If a subsequent run is authorized, preregister its method lane and compare every candidate surface and final dots against the full pinned inventory before claiming approval. The existing holdout estimates do not predict a leaderboard result above the owner-reported 0.2778 or the conflicting 0.3195/0.4413 figures.
