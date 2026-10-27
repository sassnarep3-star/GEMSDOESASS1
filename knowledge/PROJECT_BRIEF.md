# Persistent project brief — read before every session

This is a **deduplicated operational transcription**, not a verbatim archive of the repeated conversation. It preserves the goals, protocol, sources and constraints; the original chat remains the verbatim record. Read this and README.md at the start of every session.

## Mission and values

Build an auditable, usable project for the DOE GEMS Prize fault-detection competition, supporting discovery of unmapped structures relevant to geothermal exploration. Aim to maximize the probability of a genuinely competitive result, not to manufacture confidence. Fault predictions are not geothermal-vent discoveries.

**Maximize P(Win):** weigh risk and tradeoffs, prefer credible validation and useful negatives over leaderboard overfitting. **Own the Outcome:** own the data→method→evaluation→export→validation→website→release process; fix observable failures and preserve evidence.

## Highest urgency

Generate a genuinely unique competition-format single-band GeoTIFF when and only when the protocol permits it. Never copy a previous prediction, jitter it, or change metadata to claim novelty. Historical files may be examined for learning. The site must make it obvious whether a file is **approved to submit**, merely format-valid, or blocked. Do not call an unverified or duplicate file submission-ready to satisfy a download request.

Use finite float32 predictions in [0,1], with no NaN inside the footprint (this project conservatively requires no NaN anywhere), matching sample CRS, shape and geotransform. Zero outside the footprint and on visible known faults. Write a unique name and a short note of at most 140 characters. Automate validation inside the project; no human visual inspection gate. A local pass does not prove organizer acceptance.

## Parallel-run protocol (mandatory)

1. Stay in one explicitly named method lane. The conversation refers to a method paragraph but provides none; log this omission. If rank correlation with **any registry raster** exceeds 0.90 or more than 70% of candidate dots are within 3 pixels of one prior raster's dots, log duplicate and **stop**. Check surface before placement and final dots. Do not silently exempt saturated priors or change the thresholds.
2. Reuse the template's feature cache, evaluate_holdout.py and submission_writer.py. Hide-and-recover must withhold whole fault segments/components with a buffer. Build every catalogue feature only from visible faults; mask visible fault pixels exactly. Pool DTI components before computing the ratio. Alpha=0.2, beta=0.8, 300 m triangular kernel. Fix shared tools centrally, not in a private metric fork.
3. Label measured scores **HOLDOUT-DTI** with evaluator version, withheld positives and 95% CI, or **ORGANIZER-CONFIRMED** with a submission-page receipt. Projections are not scores. User/owner historical reports are explicitly unverified and excluded from those validated classes.
4. Test each feature alone on the holdout. AUC >0.90 is a leakage canary until proven otherwise. Passing a canary is not proof of no leakage.
5. End with one JSON run card: hypothesis; mechanism; a named non-fault mimic; holdout DTI+CI; registry correlation/overlap; raster SHA256; validator findings (finite/range/CRS/shape/transform); name and note <=140 chars; verdict promote/negative. Null values with reasons are required when an artifact is prohibited, not fabricated hashes or scores. Negative results are deliverables.
6. Stop after three experiments or two hours. No competition uploads or weekly-slot selection in this research run. Promotion is a separate selector step subject to the official weekly cap.

## Research and validation

Before implementation rank 3–5 new-to-this-repo geological hypotheses by qualitative expected benefit and cost. Name layers, physical transform, reason it might detect unmapped rather than already mapped faults, confounders and differences from prior methods. Do not claim global novelty from an empty checkout. Check that new external data are obtainable, free, official and eligible before calling an idea viable. Use deep research when the sources are actually reachable, and retain a claim/source ledger. Do not invent citations or claim line-by-line verification of inaccessible sources.

Run the leading hypothesis on buffered spatial holdout before any weekly slot. Require improvement over a comparable current holdout best; do not substitute scores from other evaluators, training on hidden components, synthetic truth or a leaderboard projection. Keep train/test boundaries and whole-component exclusions auditable. Retain negative experiments. Prioritize unfinished work from earlier sessions only when that work actually exists in this checkout.

## Executive summary and site

Focus on GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, GEMSDOE36. Provide a summary for each, plus an opening table listing filenames, evidence/score availability, uniqueness, format and submission approval. Keep original names and byte hashes; compare actual predictions, not just names/hashes. Investigate GEMSDOE32's reported 0.2778 and whether its mechanism could improve, without claiming causal proof from a report. Other claimed highs 0.3195 and 0.4413 conflict; do not choose one as current without official evidence.

Create a clean GitHub Pages site with an obvious opening decision and easy download **only for cleared artifacts**, an executive-summary subpage and precise submission instructions. Explain the [0,1] rejection without assuming an unproven cause. Include source links, data inventory, limitations, irregularities, freshness and next steps. Maintain a current source feed while keeping experimental evidence immutable. Do not automatically promote or upload after a source refresh. Subpages in this repo do not update the nine other repositories.

## Provided official starting points (availability must be measured)

- https://www.drivendata.org/competitions/306/competition-doe-gems/
- https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- https://github.com/drivendataorg/gems-prize-reference-solution
- https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- https://gdr.openei.org/submissions/1391
- https://gbcge.org/current-projects/ingenious/
- https://docs.nlr.gov/docs/fy26osti/96647.pdf
- https://epsg.io/32611
- https://en.wikipedia.org/wiki/Tversky_index (background, not an official contest authority)

Owner starting pages: https://buffedlizard55-lab.github.io/GEMSDOE24/ , /GEMSDOE25/ , /GEMSDOE27/ , /GEMSDOE28/ , /GEMSDOE30/ , /GEMSDOE31/docs/ , /GEMSDOE32/docs/index.html , /GEMSDOE33/ , /GEMSDOE36/docs/ . Full explicit source/file links are in the generated executive table and pinned inventory. Competition-data Dropbox links are present in the chat, but Dropbox and DrivenData downloads are not reachable through this sandbox's allowed outbound hosts. Do not report a verified login redirect if a network restriction was the actual observation.

## Data and execution limitations

The initial repo has no scripts, data, trained model, site, GPU claim or previous sessions' next steps—only a title. Do not repeat the prompt's claim that 'data placement is the single remaining blocker' as a finding. Public owner GitHub mirrors can provide hash-pinned data for CPU experiments. A hash proves byte integrity against that mirror, not official origin, data licensing, competition eligibility, live leaderboard performance, or a successful portal receipt. Never request passwords or tokens. Name exact remaining access needs in the report.

## Delivery and review

Work autonomously; flag irregularities instead of inventing answers. Do three passes: (1) implement and execute, (2) review bugs/assumptions/edge cases and fix, (3) recheck against the requirements and run checks. Create a PR from the fixed Arena session branch and merge it after successful checks, if GitHub permissions allow. Never use the merge to imply the scientific candidate is promoted. Record unresolved limitations and next-session actions.
