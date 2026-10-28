# SWGB release correction — 2026-10-28

## Decision

**Negative: do not submit the previously advertised SWGB TIFF.** Its original
`evidence/swgb/run_card.json` is historical, not the current decision. It
compared only 17 selected rasters; the frozen nine-site inventory includes a
calibration lattice that this comparison omitted. Applying the inherited,
literal candidate-directed 3-pixel overlap rule to the final SWGB dots and that
one witness gives **0.9987071898389658**, above the **0.70** stop threshold.
This is a registry overlap measurement, not a score. The witness is an input
calibration raster, not necessarily a previous competition submission: treating
it as part of the frozen registry is the existing literal protocol, not a claim
that the TIFFs are identical. `scripts/novelty.py` uses the same scope without
a density exemption. Because the full SWGB field was not re-audited before
placement against this broader registry, the surface gate is also unproven.
The final-dot witness alone is sufficient to stop. This is not a complete new
registry scan, and no rank-correlation maximum is claimed for it.

The local preflight reopens the TIFF and passes all checks in the shared
`vendor/gems57/validate.py`, against the pinned owner-mirrored footprint and
catalogue; the witness script separately verifies exact CRS, shape, transform,
and band count against the mirrored sample. It has no NaN or Inf, values in
[0,1] throughout, and is zero outside the mirrored footprint. Local validation
does not establish portal acceptance or official template authenticity. The
cause of the user's previous rejection is not established. See the full
[receipt](swgb_witness_review.json).

The recorded shipped-emission **HOLDOUT-DTI 0.1401, 95% CI [0.1329, 0.1452]**
(`GEMSASS1-HR-v2-segment`, 60,988 withheld positives) remains a historical
conditional proxy, not a leaderboard estimate. The original run exceeded the
requested three-experiment budget and did not run this broad final-dot witness
or prove the broad surface gate. The earlier claim of clearance and
recommendation to spend a slot are withdrawn. No further experiment, placement,
submission, or generated TIFF was performed in this review.

## Reproduce the witness

The raster is pinned in [the inventory](../registry/focus_inventory.json) and
[the source repository](https://github.com/buffedlizard55-lab/GEMSDOE24/blob/cf093c8c5e9fa77294ecf4c59b79cdade92cbc06/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif).
A GitHub blob download and checksummed local mirrors suffice; no account
credentials are stored:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-lock.txt
mkdir -p .cache
gh api repos/buffedlizard55-lab/GEMSDOE24/git/blobs/81c802618e6d46c6d62289d856ae74439439bbc6 > .cache/witness.json
.venv/bin/python -c 'import base64,json; open(".cache/witness.tif","wb").write(base64.b64decode(json.load(open(".cache/witness.json"))["content"]))'
.venv/bin/python scripts/audit_swgb_witness.py .cache/witness.tif
```

The script rejects incorrect SHA256 or grid metadata and calls the unmodified
shared `dot_overlap` and `validate` functions. It only writes a receipt when
explicitly requested via `--output`; it cannot approve a submission. It applies
the footprint to both supports, as the existing broad audit does. The raster
itself, original narrower run card, and old generator text remain preserved;
the SWGB builder and legacy site generator now exit before imports or writes.

## Review passes and next actions

1. **Inventory:** read project instructions and prior results; discovered the
   contradictory SWGB/BGAC decisions and narrowed the issue to registry scope.
2. **Byte check:** fetched the pinned witness Git blob, checked all input hashes,
   checked exact grids, ran the shared overlap and validator, and withdrew the
   invalid clearance. The witness is a calibration lattice, so whether it should
   be in a future submission-only registry requires an explicit external policy
   decision; excluding it silently would change this run's rules.
3. **Release hardening:** the concurrent main-line review replaced active SWGB pages with blocked notices,
   blocked the old narrow-registry builder before computation, retained old
   pages' source as historical text, and added regression tests. Review the
   [next-session plan](../knowledge/NEXT_STEPS.md) before running anything.

The organizer's [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/),
[leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/),
and [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
are sources for manual review; only the GitHub source was reachable from this
sandbox. Official file hashes, current rules/weekly cap, current leaderboard and
submission receipts remain unverified. The conflict between user-supplied
leaderboard values is unresolved. Public project-site summaries here do not
modify the nine separate source repositories.

This independent review was integrated with the concurrent [main-line review](../knowledge/RELEASE_REVIEW_2026-10-28.md); both witness measurements agree.
