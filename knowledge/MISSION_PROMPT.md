# Mission prompt — verbatim project brief (read at the start of every session)

Stored here so it is never lost and so the README can stay readable. This is the
owner's brief, transcribed without editing. Read
[`README.md`](../README.md), this file, [`knowledge/NEXT_STEPS.md`](NEXT_STEPS.md)
and [`evidence/offset_step_v2/run_card.json`](../evidence/offset_step_v2/run_card.json)
before changing anything.

## Goal

Review the repo. Focus on the highest-scoring submissions from GEMSDOE24, GEMSDOE25,
GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33 and GEMSDOE36.

Produce an **executive summary on every site** that makes it clear and obvious which
is the best submission to submit to obtain a high score on the leaderboard. It must
also be unique and not an exact duplicate of any previous submission in the list.

**Keep iterating and testing until we have the highest-scoring submission to download
and submit.**

## Scoring table

We should be able to estimate the score for a submission. The executive summary must
contain a table that clearly lists **what file to download**, **what the estimated
score is**, and **whether it is a unique submission** unlike any of the other GEMSDOE
sites listed.

## Highest urgency

> MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS
> SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. BUT WE MUST GENERATE A UNIQUE TIF
> SUBMISSION. IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED
> TIF SUBMISSION.

There must be an easy-to-download submission TIF as described by the prompt, and it must
be obvious when you visit the site. Many sites mention inspection only and a human
inspector, but **the inspection needs to be done through the project and needs to be
validated for submission without human intervention.**

## The question to answer

The highest score in the supplied list is
[GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)
`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778`. **Why and how did this get the
highest score, and are we able to generate a submission that scores higher than 0.2778?**
Answer at PhD level, then use the answer to generate a unique TIF. Must be unique
unlike any within the GEMSDOE sites. **Verify working line by line, no hallucinations.**

The brief also cites a current leaderboard high score of `0.4413`, and later `0.3195` as
the bar to beat. These figures are mutually inconsistent and none is organizer-confirmed;
see [irregularities](#irregularities).

## Parallel-run protocol

1. **Lane.** Stay inside the assigned method. If the raster's rank-correlation with any
   registry raster exceeds 0.90, or more than 70 % of its dots fall within 3 px of one
   registry raster's dots, it has drifted into another lane: log it as a duplicate and stop.
   Check on the surface before placement AND on the final dots.
2. **Reuse, don't rebuild.** Use the template's cached feature stack, `evaluate_holdout.py`
   and `submission_writer.py`. Holdout = hide-and-recover: withhold whole fault segments
   with a buffer, derive every catalogue-based feature only from the visible faults, mask
   visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular
   kernel). If a shared tool is wrong, fix it once in the template and report it; never
   keep a private fork.
3. **Label every number** HOLDOUT-DTI (evaluator version, number of withheld positives,
   95 % CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). **A projection
   is never written as a score.**
4. **Leakage canary.** Test each feature alone on the holdout before trusting any result.
   AUC above 0.90 means leakage until proven otherwise.
5. **Run card.** End with one JSON card: hypothesis; mechanism; the named non-fault process
   that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256;
   validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform
   match); submission name + note of at most 140 characters; verdict promote / negative.
   **Negative results are deliverables.**
6. **Budget.** Stop after 3 experiments or 2 hours. Do not pick submissions: promotion to a
   real slot is a separate selector step, within the weekly cap shown on the submission page.

## Hypotheses

Before implementing, generate 3–5 candidate geological hypotheses not yet tried, each
naming: the specific layer(s) involved; the physical signature being targeted (e.g. an
edge-detection or curvature transform); why it should catch a fault **missing from** the
USGS/INGENIOUS catalogue rather than one already in it; and how it differs from anything
already implemented in this repo. Rank them by expected DTI improvement and implementation
cost. **Validate the top candidate on the spatially-blocked holdout before touching a weekly
submission slot — do not spend a submission slot on an idea that hasn't beaten the current
holdout best.** If a candidate can't be validated without new external data, name the specific
free, official source needed and check it's obtainable before proposing it as viable.

## Research and method

Work line by line, verifying from official verified trusted sources, with links for manual
review. No manual input — work autonomously. Flag any irregularities for review.
**No hallucinations.**

Study, analyse and understand the highest score. Do deep research and critical thinking and
come up with new hypotheses to test. Find sources of data others are overlooking. Be
contrarian but smart: everyone is competing for the top prize. Store all information and
knowledge gathered from official verified sources so other projects can start from it.

## Site creation

Create a GitHub Page for this repo: clean UI, user-friendly, simple, easy to use, organised.
It must include all relevant information in an easy-to-read format with official verified
links as sources for review. The downloadable submission TIF must be obvious at the very
beginning of the site.

## Submission mechanics

The portal accepts a single-band GeoTIFF (.tif), or a .zip containing a single GeoTIFF,
matching the submission format's CRS, shape and geotransform. A previous upload returned
**“Predicted values must be in range [0, 1]”**. Each submission needs a unique name and a
short comment (a note of at most 140 characters) to tell submissions apart later.

There must be an **executive-summary subpage** that explains exactly how to make a submission
into the contest.

## Core values

- **Maximize P(Win)** — in every decision, weigh tradeoffs, assess risk, and choose the path
  that maximizes the probability of success. Set aside emotions; make tough decisions.
- **Own the Outcome** — own results end to end, not just our individual slice. When problems
  arise and we have the means to act, we do so without waiting for permission. Treat failure
  and success as signals and use them to improve.

## Working cadence

Run the task through multiple passes. Pass 1: implement completely and verify. Pass 2: review
for bugs, missing requirements, incorrect assumptions and edge cases; fix everything found.
Pass 3: re-check the entire implementation against the original request and improve accuracy,
reliability, completeness and code quality. Do not stop after the first pass.

Then open a pull request and merge it to `main`, stating what work still needs to be done and
what limitations are in the way — to be worked on in the next session.

<a id="irregularities"></a>
## Standing irregularities in this brief

- The three quoted leaderboard figures (0.4413, 0.3195, and the cached page's 0.4544) are
  mutually inconsistent and none is organizer-confirmed.
- Pending items: `gems91-s91-…` and `gems91-s28-…` appear in the supplied ledger with no
  score at all.
- Rules §1.3 appear to limit entrants to U.S. citizens, permanent residents or
  U.S.-incorporated entities; the account location is Calgary, Alberta.
  [Rules PDF (NLR)](https://www.nlr.gov/docs/fy26osti/96647.pdf)
- Several supplied links (DrivenData, Dropbox, USGS, GDR, NLR) are outside this sandbox's
  outbound allowlist and cannot be fetched here.
