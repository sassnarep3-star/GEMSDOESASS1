#!/usr/bin/env python3
"""Publish a fail-closed notice on legacy SWGB URLs; do not regenerate approval claims.

The old generator is preserved as historical text under archive/swgb-pre-review/.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'swgb'

NOTICE = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SWGB · submission blocked</title><link rel="stylesheet" href="../docs/assets/site.css"></head>
<body><main class="section" style="max-width:850px;margin:auto;padding:2rem">
<p class="eyebrow">Research evidence · release correction</p><h1>Do not submit the SWGB TIFF.</h1>
<div class="callout"><strong>Duplicate under the literal protocol.</strong> An independent byte-level audit found 99.8707% of its dots within 3 pixels of a pinned registry lattice, above the 70% limit. The original 17-raster check omitted this witness. No broader pre-placement clearance is available.</div>
<p>The retained TIFF is research evidence only. Local format checks passed against a mirrored template, not organizer acceptance. The prior promotion and uniqueness claims are superseded; no weekly slot is authorized.</p>
<p><a class="button" href="../docs/executive-summary.html">Executive summary and nine-site review</a>
<a class="button secondary" href="../evidence/swgb_witness_review.json">Witness receipt</a></p>
<p><a href="https://github.com/sassnarep3-star/GEMSDOESASS1/blob/main/evidence/swgb-review.md">Reproduce the review and limitations ↗</a></p>
</main></body></html>'''


def main():
    OUT.mkdir(exist_ok=True)
    for name in ('index.html', 'how-to-submit.html', 'run-card.html', 'hypotheses.html'):
        (OUT / name).write_text(NOTICE)
    print('Legacy SWGB URLs now show the blocked decision; no TIFF was generated.')


if __name__ == '__main__':
    main()
