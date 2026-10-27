# GEMS Research Desk

> **Submission status: DO NOT SUBMIT.** No new candidate GeoTIFF was generated or cleared in this run. The nine-site historical files are research references, not upload recommendations. [Open the executive summary](executive-summary.html) · [Read the negative run card](evidence/run-card.json) · [View the GitHub Pages dashboard](https://sassnarep3-star.github.io/GEMSDOESASS1/).

## Read at the start of every session — project brief

The user's project brief is preserved here in operational form; repeated copies of the same request are collapsed, and the nine priority records are retained in [the claims ledger](data/site-summary.json), with the wider list of user-provided claims preserved [here](knowledge/user-provided-submission-ledger.md). The goal is to discover faults indicative of geothermal resources and ultimately compete for the GEMS Prize, while making evidence, sources, uncertainty, file identity, and the actual submission decision obvious. Build a clean, useful, auditable GitHub Pages site with an executive-summary subpage and an easy download **only for a genuinely eligible new file**. The user explicitly requests autonomous machine inspection, a unique filename and a short submission note, and no invented claims.

**User's highest-urgency instruction:** “MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION. IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.”

**Parallel-run protocol (user's wording, normalized only for formatting):**

1. **LANE.** Your lane is the single method paragraph below. Stay inside it. If your raster's rank-correlation with any registry raster exceeds 0.90, or more than 70% of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.
2. **REUSE, DON'T REBUILD.** Use the template's cached feature stack, `evaluate_holdout.py` and `submission_writer.py`. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.
3. **LABEL EVERY NUMBER** as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score. Historical user-supplied figures without a receipt are explicitly marked **USER-REPORTED / UNVERIFIED**, never promoted to either evidence class.
4. **LEAKAGE CANARY.** Test each feature alone on the holdout before trusting any result. AUC above 0.90 means leakage until proven otherwise.
5. **RUN CARD.** End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.
6. **BUDGET.** Stop after 3 experiments or 2 hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.

The supplied prompt refers to a “single method paragraph below” but contains no identifiable method assignment. Do not silently invent a lane. Before implementing a future lane, propose 3–5 geological hypotheses, rank expected holdout benefit and implementation cost, identify exact layers, transforms, non-fault mimics, differences from existing work, and trustworthy public data. Verify external data availability and rights; validate the top assigned candidate on the spatially blocked holdout against the same-protocol best. Do not spend a competition slot on an unvalidated idea.

**Maximize P(Win)** by weighing evidence and protecting limited slots. **Own the Outcome** by fixing what can be fixed, recording failures and constraints, and leaving reproducible next steps. Review the work in three passes: implement and verify; inspect and fix defects; re-check against the full request. The user's request also asks to open and merge a PR to main after verification, without claiming completion of blocked scientific work.

## What this session established

- The starting repository contained only a one-line README. No candidate lane, prepared shared stack, evaluation setup, complete registry, or authenticated competition files were present.
- The nine strongest historical claims in the supplied list are tracked in [the dashboard](index.html#priority-sites). GEMSDOE32 B2 is **0.2778 USER-REPORTED / UNVERIFIED**; no organizer submission-page receipt connects that value to the audited mirror bytes. No public-score estimate is defensible. A public leaderboard observation was **0.4544** at 2026-10-27 11:31 UTC; it is not a receipt for this project and may change.
- We fetched small, SHA-pinned owner-repository mirrors strictly for learning/audit, not to submit. All 72 directed comparisons among the nine historical masks exceed the 70% 3-pixel threshold. The audited GEMSDOE25 and GEMSDOE30 masks are identical; GEMSDOE32's B2 equals GEMSDOE25's dots after removing the two-pixel known-catalogue neighborhood. These relationships do not prove what bytes were uploaded or why scores changed.
- The exact GEMSDOE36 KPL36 file, despite a site banner saying to submit, has **99.17%** of dots within 3 pixels of a registered lattice. It fails the stated literal gate. A pinned lattice covers nearly the whole owner-mirror footprint and mathematically forces any 37,654-dot candidate to have at least **82.34%** overlap. This proof does not automatically rule out every smaller candidate or authorize targeting uncovered holes. See the [independent audit](evidence/witness-audit.json) and [evidence ledger](knowledge/evidence-and-sources.md).
- The owner-mirror sample's positive pixels exactly match its known-label mirror, inconsistent with the official page's description of an absence sample. Its hash proves mirror identity, not organizer provenance; it was used for grid and footprint only. The prior [0,1] portal rejection has no retained rejected bytes or diagnosis. Do not claim that either zeros or NaNs outside the footprint are accepted without verifying the authorized sample and organizer guidance.
- The official competition data tab redirects unauthenticated users to login. The related sites document two different shared-template lineages and an owner-published raw-feature mirror, but neither an agreed prepared cache nor the complete current registry is present. Zero geological experiments and zero weekly uploads were performed. [Four prospective hypotheses](knowledge/research-preregistration.md) and a [next-session plan](knowledge/next-session.md) are retained.

## Run the independent read-back audit

Requires Python 3.11 (tested), `gh` and access to the public pinned GitHub blobs. The audit downloads only small historical witnesses into `.local-data/` (Git-ignored); it is **not** a model, the shared holdout evaluator, the shared submission writer or a selector. It never submits anything.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch_witnesses.py
python scripts/audit_witnesses.py --output evidence/witness-audit.json
python scripts/render_site.py
python -m pytest -q
node tests/test_ui.cjs  # optional UI logic test
```

Input hashes and pinned source paths are in [`data/inputs.json`](data/inputs.json); [the full results](evidence/witness-audit.json) include actual read-back grid/range checks, 72 directional overlaps, KPL36's failed witness, the lattice bound and the mask identities. An intact SHA is not an organizer receipt. Do not use these audit witnesses as new submissions.

The dashboard's optional source-freshness check requests only the nine public GitHub repository heads, caches successful checks briefly, and shows changed or unavailable sources without changing the submission decision. It does **not** scrape DrivenData or treat a changed repository as a new score. Current competition data, quota, leaderboard and rules require their own authorized sources.

## Primary sources

- [DrivenData problem, metric and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) · [data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData staff clarification on exact known-fault masking](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4) · [official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) · [organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) · [DOE OpenEI INGENIOUS record](https://gdr.openei.org/submissions/1391) · [USGS blind-geothermal play-fairway synthesis](https://www.usgs.gov/publications/discovering-blind-geothermal-systems-great-basin-region-integrated-geologic-and)

Full provenance, licensing limitations, score classes and irregularities are in [the source ledger](knowledge/evidence-and-sources.md). The requested three-pass review is recorded [here](knowledge/review-passes.md).
