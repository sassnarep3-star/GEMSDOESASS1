# GEMS Fieldnotes

An evidence-led executive brief and reproducible raster audit for the DOE GEMS Prize. **Decision: negative. There is no new competition-ready GeoTIFF, no download to submit, no holdout score, and no authorized submission. No competition slot was used.** The run card is [`docs/data/run-card.json`](docs/data/run-card.json).

## Requested objectives

The user asked for an original, unique, range-valid fault-prediction GeoTIFF that might exceed the reported GEMSDOE32 score; a nine-site executive-summary website with source links, upload guidance and an easy download; and a PR merged to `main`. The research protocol requires ranking new geological hypotheses *before* implementation, staying in one assigned method lane, testing on a buffered whole-segment holdout with leakage canaries and the official pooled DTI, checking the full registry before and after placement, independently validating the saved TIFF, and using a separate selector before spending a weekly slot. At most three experiments or two hours were permitted. A negative result is a valid deliverable.

Those conditions cannot honestly be satisfied in this run: the prompt did not identify the required single-method paragraph; the reusable prepared feature cache and complete current registry are missing; the shared template needs upstream fixes; and a pinned registered lattice already rules out the commonly used 37,654-dot budget under the literal overlap criterion. We did not invent a lane, train a model, generate a lookalike TIFF, claim an estimated score or upload anything.

A separate parallel run merged [a synthetic TIFF](docs/downloads/gemsdoesass1-hybrid-blindpiedmont-dispersed-37654-20261027T113459Z-cbceb1d0-zeros.tif) into `main` during this review. It is retained for **research only, DO NOT SUBMIT**. Our independent recheck finds 37,596/37,654 dots (99.85%) within three pixels of the registered lattice and a failure of the conservative outside-footprint mask check. A previous 20.6% comparison against the champion did not establish full-registry uniqueness. Its claimed holdout was not reproduced here. The earlier PR, files and historical reports are preserved; superseded README and HTML text are archived under [`archive/`](archive/).

## What the audit found

- Nine pinned historical mask files (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33 and 36) were compared in [`evidence/focus_audit.json`](evidence/focus_audit.json). The supplied values are **USER-REPORTED, not organizer-confirmed**; there are no hash-bound receipts in the inspected evidence. GEMSDOE32's 0.2778 and its thinning/pruning explanation are plausible claims, not a proven cause or a score for our run.
- All 72 directional historical comparisons exceed the stipulated >70% overlap stop. GEMSDOE25 and 30 have identical masks; GEMSDOE32 B2 equals the GEMSDOE25 mask with a 2-pixel catalogue neighborhood removed. Those relationships say nothing about unseen ground truth or private scoring.
- The pinned reference lattice's 3-pixel halo covers 5,160,724 of 5,167,373 footprint pixels. For 37,654 dots, at least 31,005 (82.34%) must overlap it. This one-reference proof is decisive at that budget, conditional on the literal registry rule; it does not automatically reject every smaller budget or establish that any remaining dot is scientifically meaningful.
- Five later peer candidates and the separate parallel research raster independently failed the same literal stop (99.17%, 99.62%, 99.61%, 100%, 99.78%, and 99.85% overlap); see [`evidence/claimed_candidates_audit.json`](evidence/claimed_candidates_audit.json). Their source-site banners, narrower checks and reported holdouts do not constitute a full-registry clearance. No other run's model or holdout was rerun.
- The official public leaderboard was observed at **0.4544 on 2026-10-27**. This is neither a candidate-bound score nor a private result and can change. No DrivenData account, submission history, or real-time slot quota was queried, and the site never automatically monitors DrivenData.
- Fourteen core/external files were restored from hash-pinned peer mirrors, **not authenticated against organizer-provided originals**. The example mirror has 60,988 positive pixels identical to the supplied label mask, in tension with the organizer's description of a blank sample. Treat its grid/footprint as a provisional reference. Inputs and licensing caveats are in [`evidence/input_recovery.json`](evidence/input_recovery.json); raw files are excluded from this repository.
- The pinned shared evaluator/writer silently binarize positive probabilities ([upstream issue 37](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/37)). The evaluator source matches the hash in the open [empty-truth pooled-FP report](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/41), and the [surface-stage overlap bug](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/42) was reproduced on a synthetic example. This account has read-only access to that template and the inspected repository declares no license; no upstream fix or private fork was made.

The four prospective geological ideas and their data, mimics, costs and limitations are in [`research/hypotheses.md`](research/hypotheses.md). They are not an assigned lane, tested models or a claim of global novelty.

## Website

The static site lives in [`docs/`](docs/index.html): overview and nine-site table, [executive summary / conditional upload guidance](docs/executive-summary.html), and [research, sources and evidence](docs/research.html). The GitHub Pages address is <https://sassnarep3-star.github.io/GEMSDOESASS1/> once the `main` `/docs` deployment is configured and built. Serve it locally (use HTTP, not `file://`, for the JSON feed):

```bash
python -m http.server 8000 --bind 0.0.0.0 --directory docs
```

The site checks the nine **public GitHub heads only** from the reader's browser and compares them to a pinned baseline. GEMSDOE24 changed after the pinned baseline; two of its new research artifacts were checked against the lattice but are not incorporated into the frozen historical score table, and their holdouts were not rerun. Changed, partial, rate-limited and offline cases are visibly distinguished; the last recorded snapshot is labeled as such. A changed head calls for re-audit and never updates score claims or grants permission to submit. The scheduled CI tests the tools; neither the site nor CI monitors DrivenData.

## Reproduce the independent checks

Requires Python 3.11 or newer, Node 20+ for the browser-script unit tests, and `gh` for public GitHub input downloads (authentication may be required for rate limits). Some downloads are large; inspect source licenses and access terms before reuse.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
node --test tests/web.test.js

# Eighteen pinned forensic TIFFs; verifies SHA-256 and caches locally.
python scripts/fetch_audit_inputs.py
python scripts/audit_focus.py
python scripts/audit_claims.py
python scripts/audit_parallel_variants.py
# Rebuild table and synchronize the published evidence copies.
python scripts/render_portfolio.py

# Optional: restore the pinned shared template and 14 owner-mirrored core/external
# inputs (>400 MB) to .cache/. Does not build the missing feature cache or run a model.
python scripts/restore_inputs.py
```

To inspect an actual saved candidate against an **authenticated** template (neither is included here):

```bash
python scripts/validate_tif.py path/to/candidate.tif path/to/official_sample.tif --out local-format-report.json
```

The independent checker fails closed on grid/band/dtype, interior mask, non-finite/out-of-range raw values, outside-footprint nullness and non-self-contained sidecars. It also checks the template against the observed mirror grid `(3730, 3292)`, transform `(100, 0, 243350, 0, -100, 4508550)`; those observed coordinates are not organizer-authenticated. Its additional requirement of finite raw storage *and* an internal mask outside is conservative, not a claim that the organizer's uploader accepts that encoding. A passing local check cannot establish model validity, registry uniqueness, organizer acceptance, or slot permission.

## Official references

[Problem, data, metric and GeoTIFF contract](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [DOE/NLR prize rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf) · [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [DOE GDR INGENIOUS 1391](https://gdr.openei.org/submissions/1391) · [staff: site submission limit governs](https://community.drivendata.org/t/submission-amount-question/11553) · [staff: rolling window](https://community.drivendata.org/t/weekly-submissions/11524). The [research page](docs/research.html#sources) distinguishes primary sources from peer claims and notes access, licensing and uncertainty.
