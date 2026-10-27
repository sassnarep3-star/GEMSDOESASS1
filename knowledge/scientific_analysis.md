# Scientific interpretation — what the result does and does not establish

## Why H33-B2 could improve a dotted emission

**Measured transformation:** the exact GEMSDOE32 B2 prediction equals the GEMSDOE31 base intersected with `distance_to_published_catalogue > 2 pixels`. The base contains 40,199 dots; B2 contains 37,654. It removes 2,545 and adds none. This was checked on the actual arrays, not inferred from names. See [measured audit](../evidence/nine_site_audit.json) and [pinned original implementation](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/1398109a23f04a2ace71c1bd2f527cfba87860b5/src/gems32/hypotheses33.py#L313-L331).

The reported historical leaderboard value is **0.2778 — UNVERIFIED owner/user report, not ORGANIZER-CONFIRMED**. The owner [explicitly says its ledger has no matching organizer receipts](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/1398109a23f04a2ace71c1bd2f527cfba87860b5/registry/claims.json). An exact verified transformation is not a verified score or causal explanation.

Under the **protocol-specified** DTI formula, write T = weighted truth coverage, F = weighted false-positive mass, K = withheld truth count, alpha=0.2 and beta=0.8:

    DTI = T / [T + alpha F + beta(K - T)]
        = T / [alpha T + alpha F + beta K].

A deletion with weighted coverage loss dT >= 0 and false-positive reduction dF >= 0 improves the ratio precisely when:

    dT * (alpha F + beta K) < alpha T * dF.

This follows by cross-multiplying the positive old/new denominators. If dT=0 and dF>0, pruning necessarily helps. If a removed dot was the sole nearby predictor for a hidden new trace, the coverage loss can outweigh the saving. The unknown organizer T/F/K prevent evaluating that condition for the reported submission.

Dotted, separated emissions can avoid paying for many redundant positive pixels around the same truth neighborhood. A catalogue-flank mask can further remove low-value mass if hidden new traces are scarce there. But that population assumption must be tested: a new splay close to a known trace is a counterexample. Known-fault **pixels** being excluded from scoring is not a rule that every prediction within a 200 m **halo** is false. The source's stronger prose is not adopted here.

Therefore the plausible mechanism is **emission/metric efficiency**, not evidence that B2 discovered new geothermal structures. Fine variations of the same base can be strongly overlapping submissions and cannot satisfy this run's uniqueness requirement merely by improving their byte hash.

## What BGAC-1 tested

A low-density sedimentary basin may have lower gravity where basement is deeper. A buried fault could produce a persistent signed opposition of the gravity and basement-depth gradients without a pronounced topographic step. BGAC-1 required that opposition at fixed smoothing scales of 2 and 5 pixels and weighted toward weak topographic gradients. This is a hypothesis, not a verified fault interpretation.

Important confounders:

- **Non-fault depositional basin margin:** smooth sediment-thickness/density changes can generate the same gradient opposition.
- **Shared inversion information:** the basement surface may itself be derived from gravity. Agreement between those products is not independent multi-instrument corroboration.
- **Resolution and population mismatch:** catalogue faults tend to be mappable; concealed faults are the intended test target. Hide-and-recover does not fully reproduce that selection process.
- **Footprint and missing-data boundaries:** the experiment restricted support to pixels at least 20 pixels inside common finite support, the fixed four-sigma radius of the largest Gaussian scale, to avoid selecting filled-data edges.
- **Transductive normalization:** feature ranks use unlabeled eligible feature values across the footprint. No held-out labels enter features or their rank normalization, but this is not an inductive out-of-region deployment claim.

## Numerical result and qualification

**Exploratory HOLDOUT-DTI**: BGAC-1 0.0390362, 95% physical-block bootstrap CI [0.0283104, 0.0501349]; strongest same-run ablation 0.0730272, CI [0.0568760, 0.0892154]; paired difference -0.0339910, CI [-0.0466399, -0.0219705]. All use evaluator `gems57-pooled-hide-v2` and 56,454 withheld positive pixels. These are conditional intervals on catalogue proxy truth, not leaderboard forecasts.

**Protocol qualification:** pass 2 found that the first surface audit omitted overlap and continued with incomplete clearance. The corrected gate rejects the identical surface before placement. The measured DTI is retained as an exploratory negative, never as promotion-qualified evidence. The raw receipts and original card are preserved. No new dots or experiment were generated after correction.

Passing per-feature AUC canaries (observed 0.4045–0.5727) only says that this simple screen did not trigger. It does not prove independence, no source leakage, reliable probability calibration, or transfer to hidden unmapped faults. Catalogue-zero background is unlabeled, not verified fault absence.

## Can this establish a submission above 0.2778?

No. It establishes an unpromotable negative. Neither the historical report nor this proxy instrument supports a numerical leaderboard estimate for a new file. No actual official competition score, current leader, or weekly cap was read in this environment. The two different high-score claims in the request remain unresolved.

The literal novelty policy is also obstructed: a prior lattice is within 3 pixels of 99.8713% of the footprint and all of the first-pass candidate dots. Exact Spearman surface dissimilarity does not rescue a forward-overlap failure. There is no authorized density exception, and choosing only the tiny lattice-uncovered area would be a registry-shaped workaround, not a validated geological discovery strategy. This run stopped rather than manufacturing such an artifact.

A stronger next programme needs a clarified/versioned novelty policy, official input/rule provenance, a fair reproducible incumbent on identical buffered visible-only splits, independent source checks, and preregistered hypotheses with negative controls. None of those steps justifies spending a weekly slot before validation.

## Authority boundaries

The [official reference notebook](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb) verifies a reference fault-detection approach and asymmetric Tversky training loss. It does not independently verify the current 300 m DTI definition. That formula here is the user's supplied protocol, implemented by the pinned shared tool and tested against its brute-force oracle. The official competition metric page, USGS/GDR sources and rules PDF could not be independently fetched under the sandbox allowlist. No literature-derived quantitative geological claim is invented to fill that gap.
