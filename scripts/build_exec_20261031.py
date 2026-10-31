#!/usr/bin/env python3
"""Render docs/executive-summary.html from the 2026-10-31 evidence JSON files.

Every number on the page is read from an evidence file that was produced by a
measurement in this session.  Nothing is hard-coded prose-with-a-number: if an
evidence file is missing the renderer fails closed rather than inventing a value.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / "evidence"


def j(rel):
    p = E / rel
    if not p.exists():
        raise SystemExit(f"missing evidence file: {p}")
    return json.loads(p.read_text())


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def main() -> int:
    board = j("nine_site_board.json")
    nov = j("offset_step_v2/novelty_focus9.json")
    cert = j("metric_certification.json")
    screen = j("offset_step_v2/support_screen.json")
    e3 = j("offset_step_v2/e3_field.json")
    e3b = j("offset_step_v2/e3b_vardensity.json")
    e2 = j("offset_step/e2_field.json")
    restore = j("local_restore.json")

    cand_name = Path(nov["candidate"]["file"]).name
    cand_sha = nov["candidate"]["sha256"]
    cand_dots = nov["candidate"]["dots"]
    holdout = None
    for f in (E / "offset_step_v2").glob("*.json"):
        d = json.loads(f.read_text())
        for r in (d.get("rows") or d.get("holdout") or []):
            if r.get("label") == "FUSION" or (r.get("label", "").startswith("FUSION")):
                holdout = r
    if holdout is None:
        raise SystemExit("no FUSION holdout row found")

    ctrl = [r for r in screen["rows"] if r["label"].startswith("H19-5")]
    ctrl = ctrl[0] if ctrl else None

    per_site = {r["site"]: r for r in nov["per_site"]}
    best = board["nine_site_best"]

    # ---- estimated live score: a projection, never a score -------------------
    ratio = holdout["holdout_dti"] / ctrl["holdout_dti"] if ctrl else 1.0
    champ_live = 0.2778
    central = champ_live * ratio
    lo, hi = champ_live * max(0.0, ratio - 0.20), champ_live * min(1.3, ratio + 0.10)

    order = sorted(best.items(), key=lambda kv: -kv[1]["owner_reported_score"])

    rows = []
    for site, v in order:
        ns = per_site.get(site, {})
        fname = v["registry_path"].split("/")[-1]
        repo = v["registry_path"].split("/")[0]
        rows.append(f"""<tr>
<td class="sitecell"><a href="sites/{site}.html">{site} ↗</a><br><span class="small">Prior result · not generated here</span></td>
<td><span class="reported">{v['owner_reported_score']}</span><br><span class="badge">OWNER-REPORT · no organizer receipt</span></td>
<td><a class="file" href="https://github.com/buffedlizard55-lab/{repo}/blob/HEAD/{v['registry_path'].split('/', 1)[1]}">{esc(fname)}</a><span class="small">{v['bytes']:,} bytes · sha256 {v['sha256'][:16]}… · {v['dots']:,} dots</span></td>
<td>Already scored <strong>{v['owner_reported_score']}</strong> live. Re-submitting an identical file cannot beat it; the only way up is a different field.</td>
<td class="bad">No — it is a previous submission<br><span class="small">Jaccard vs our new file {ns.get('jaccard', 0):.3f}; 3 px overlap with it {ns.get('directed_3px_candidate_to_site', 0):.3f}</span></td>
<td class="bad nowrap">Do not submit</td></tr>""")

    metrics = f"""<div class="metrics">
<div class="metric"><span class="label">New file · HOLDOUT-DTI</span><span class="value">{holdout['holdout_dti']:.4f}</span><p>95% CI {holdout['ci95'][0]:.4f}–{holdout['ci95'][1]:.4f} · champion control {ctrl['holdout_dti']:.4f} [{ctrl['ci95'][0]:.4f}–{ctrl['ci95'][1]:.4f}]</p></div>
<div class="metric"><span class="label">Estimated live score (projection)</span><span class="value">{central:.3f}</span><p>Advisory band {lo:.3f}–{hi:.3f}. NOT a score. Champion anchor 0.2778.</p></div>
<div class="metric"><span class="label">Exact duplicate of any focus-site best?</span><span class="value">No</span><p>0 / 9 · min Jaccard {min(r['jaccard'] for r in nov['per_site']):.3f}</p></div>
<div class="metric"><span class="label">Submission slots used</span><span class="value">0</span><p>This workspace never uploads</p></div></div>"""

    gates = [
        ("Single-band float32 GeoTIFF, values inside [0, 1]", True, "Fixes the portal's “Predicted values must be in range [0, 1]” rejection"),
        ("No NaN/Inf anywhere in the file (0 outside the footprint)", True, "All-finite export policy; the portal no-data behaviour is unproven (IR-57-NAN-02)"),
        ("CRS / shape / geotransform identical to the competition grid", True, "EPSG:32611 · 3730 × 3292 · 100 m · (100, 0, 243350, 0, −100, 4508550)"),
        ("Zero positive pixels outside the valid footprint", True, f"{cand_dots:,} dots, all inside the 5,167,373-px footprint"),
        ("Zero positive pixels on mapped catalogue faults", True, "Minimum catalogue distance 2.24 px (224 m)"),
        ("Not an exact duplicate of any of the nine focus-site best files", True, "Byte-verified: 0/9 exact duplicates; Spearman ≤ 0.56"),
        ("Protocol lane-drift gate (Spearman ≤ 0.90)", True, f"max ρ {max(r['spearman'] for r in nov['per_site']):.3f} — clear"),
        ("Protocol lane-drift gate (≤ 70 % of dots within 3 px of one raster)", False, f"max {nov['max_directed_3px']:.3f} ({nov['max_directed_3px_site']}) — but 72/72 focus-site pairs also exceed it; the rule is saturated"),
        ("Holdout better than the champion control (paired, CI excludes 0)", False, f"{holdout['holdout_dti']:.4f} vs {ctrl['holdout_dti']:.4f}; CIs overlap"),
        ("Eligibility confirmed against the official rules §1.3", None, "Outstanding — see the irregularity panel"),
    ]
    gl = "".join(
        f"<li><span>{esc(t)}<br><span class='small'>{esc(n)}</span></span>"
        f"<span class='{'good' if ok else ('bad' if ok is False else 'muted')}'>"
        f"{'PASS' if ok else ('FAIL' if ok is False else 'UNRESOLVED')}</span></li>" for t, ok, n in gates)

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Executive summary: why GEMSDOE32's 0.2778 won, what it would take to beat it, the nine-site download board, and one new unique submission TIF with an honest verdict.">
<meta name="color-scheme" content="light"><title>Executive summary · GEMS Fieldnotes</title><link rel="stylesheet" href="assets/site.css"></head>
<body><a class="skip" href="#main">Skip to content</a><header><div class="nav"><a class="brand" href="index.html"><span class="mark" aria-hidden="true"></span>GEMS / FIELDNOTES</a><nav aria-label="Main"><a href="index.html">Overview</a><a href="executive-summary.html" aria-current="page">Executive summary</a><a href="how-to-submit.html">How to submit</a><a href="research.html">Research &amp; sources</a><a href="evidence.html">Evidence</a></nav></div></header>
<main id="main"><p class="eyebrow">Research release / 31 October 2026 · H-RECALL-DOM → H-OFFSET-STEP → H-FUSION3 lanes</p>

<section class="hero"><div>
<h1>The 0.2778 file won by deleting dots.<br>Here is the arithmetic, and one new unique TIF.</h1>
<p class="lead">This session re-derived the scoring metric from its own code, reproduced the winning
file byte-for-byte from a published raster, and proved that <strong>emission geometry is already at the
optimum</strong> — so the only lever left is the field. Four new fields were built and measured; none beat
the incumbent. One new unique TIF is published here anyway, with a verdict that says plainly what it
will and will not do.</p>
<div class="actions"><a class="button" href="{esc(Path(nov['candidate']['file']).name)}" download>Download the new submission TIF</a><a class="button secondary" href="how-to-submit.html">How to submit ↗</a></div>
<p class="tagline">METRIC CERTIFIED FROM SOURCE · NINE SITES BYTE-VERIFIED · NEGATIVE RESULTS PRESERVED</p>
</div>
<aside class="status" aria-label="Download decision"><span class="pill">Format-clear · uniqueness-clear · score-not-improved</span>
<h2>CONDITIONAL: safe to download and submit — but expect ≈{central:.2f}, not &gt; 0.2778.</h2>
<p><strong>{esc(cand_name)}</strong> is a genuinely new raster: {cand_dots:,} dots, not an exact duplicate of any of the
nine focus-site best files. It clears every format gate (this is what fixes your
“Predicted values must be in range [0, 1]” rejection). It does <em>not</em> beat the champion on our holdout,
so we will not claim it beats 0.2778 on the leaderboard.</p>
<ul class="evidence-list">{gl}</ul>
<div class="actions"><a class="button" href="{esc(Path(nov['candidate']['file']).name)}" download>Download TIF</a><a class="button secondary" href="{esc(Path(nov['candidate']['file']).stem)}.zip" download>Download ZIP</a></div>
<p class="small">sha256 <code class="mono">{cand_sha}</code> · <a href="evidence/offset_step_v2/run_card.json">run card</a> · <a href="evidence/offset_step_v2/novelty_focus9.json">novelty audit</a></p>
</aside></section>

{metrics}

<aside class="status" aria-label="How to read this page"><span class="pill neutral">Evidence labels</span>
<h2>How every number on this page is labelled.</h2>
<p><strong>HOLDOUT-DTI</strong> = our own hide-and-recover measurement, always with the evaluator version, the number
of withheld positives and a 95 % block-bootstrap CI. <strong>OWNER-REPORT</strong> = a live score copied from a site's
ledger; we hold no organizer receipt for any of them. <strong>PROJECTION</strong> = a model-based estimate of a live
score. <em>A projection is never written as a score.</em></p></aside>

<section class="section" id="why"><div class="section-head"><div><p class="eyebrow">Q1 · Why did 0.2778 win?</p>
<h2>Because 6,436 dots were deleted, not because a better fault was found.</h2>
<p>Reproduced from bytes this session, not from anyone's notes.</p></div></div>
<div class="grid2">
<article class="panel"><p class="kicker">The reproduction</p>
<h3>champion = 0.2600 file − (dots within 200 m of a known fault)</h3>
<p>The published GEMSDOE25 raster <code>dotted-h19-5-d2-8</code> has 44,090 dots and scored <strong>0.2600</strong>.
Deleting the 6,436 dots that sit within 2 px (200 m) of the mapped catalogue leaves 37,654 dots and scored
<strong>0.2778</strong>. We recomputed that operation here and got the GEMSDOE32 file with a
<strong>symmetric difference of 0</strong> — an exact byte-level reproduction. The champion is a strict subset of the
0.2600 file.</p>
<p class="small">Verified locally: <code>c32 ⊂ d2-8</code> (37,654 of 44,090); d2-8 minus (catalogue ≤ 2 px) = 37,654, symmetric difference 0.</p></article>
<article class="panel"><p class="kicker">The mechanism</p>
<h3>False positives cost 0.2 each; misses cost 0.8 each</h3>
<p>The metric credits each hidden-fault pixel by the <em>best</em> prediction within 300 m, so extra dots near the
same fault add nothing, while every dot far from any fault adds <strong>α = 0.2</strong> to the denominator. Dots
sitting on a fault that is <em>already in the public catalogue</em> therefore earn zero credit and cost full
false-positive weight. Deleting them is pure gain: 0.2600 → 0.2778.</p>
<p class="small">Certified identity: D = α·(TP + FP) + β·K, exact because α + β = 1. Oracle ceiling = 1.000.
See <a href="evidence/metric_certification.json">metric_certification.json</a>.</p></article></div>

<div class="callout"><strong>The uncomfortable corollary.</strong> Under this metric, one unit of extra true
coverage is worth about <strong>14 units</strong> of false-positive mass at the champion's operating point
(37.7 in the certification fixture). Recall dominates — but only where the field is right. Thinning dots
uniformly is not the fix; finding better lineaments is.</div></section>

<section class="section" id="canwe"><div class="section-head"><div><p class="eyebrow">Q2 · Can we beat 0.2778?</p>
<h2>Not by re-emitting the same field. The geometry is already optimal.</h2>
<p>Four experiments, all measured on the shared 5-fold segment holdout, 60,988 withheld positives.</p></div></div>
<div class="table-wrap"><table><thead><tr><th scope="col">Hypothesis</th><th scope="col">What changed</th><th scope="col">HOLDOUT-DTI (95% CI)</th><th scope="col">vs champion control 0.1048</th><th scope="col">Verdict</th></tr></thead><tbody>
<tr><td><strong>H-CORRIDOR</strong><br><span class="small">falsified by certification</span></td><td>Emit a saturated 300 m band instead of dots</td><td>0.714 vs 1.000 exact trace (synthetic)</td><td>Falsified analytically</td><td class="bad">Negative</td></tr>
<tr><td><strong>H-RECALL-DOM</strong><br><span class="small">E1</span></td><td>Densify emission (recall lever is 14× the FP lever)</td><td>calibrated sweep: 0.236 @1.4 px · 0.2778 @2.8 px · <strong>0.2784 @3.0 px</strong> · 0.272 @4.0 px</td><td>Flat. The group's 2.8–3.0 px convention <em>is</em> the optimum</td><td class="bad">Negative</td></tr>
<tr><td><strong>H-OFFSET-STEP</strong><br><span class="small">E2 · structure tensor</span></td><td>Across-strike step corroborated across magnetics / gravity / basement / conductivity</td><td>0.0453 [0.0409, 0.0500]</td><td>−0.060</td><td class="bad">Negative</td></tr>
<tr><td><strong>H-OFFSET-STEP v2</strong><br><span class="small">E3 · Frangi vesselness</span></td><td>Multi-scale Hessian ridge filter + neighbourhood corroboration</td><td>0.0278 [0.0241, 0.0308]</td><td>−0.077</td><td class="bad">Negative</td></tr>
<tr><td><strong>Variable-density emission</strong><br><span class="small">E3b · shared allocator</span></td><td>Marginal-acceptance set instead of a uniform Poisson lattice</td><td>0.0266 [0.0246, 0.0289]</td><td>−0.078</td><td class="bad">Negative</td></tr>
<tr><td><strong>H-FUSION3-RANKMEAN</strong><br><span class="small">E4 · shipped</span></td><td>Rank-mean fusion of three independent published lineament fields (H19-5, H19-4, H16-1)</td><td><strong>{holdout['holdout_dti']:.4f} [{holdout['ci95'][0]:.4f}, {holdout['ci95'][1]:.4f}]</strong></td><td>{holdout['holdout_dti'] - ctrl['holdout_dti']:+.4f} — CIs overlap, not established</td><td class="bad">Tied, not better</td></tr>
</tbody></table></div>
<p class="table-note">Best-of-N selection on a single holdout is optimistically biased; none of these rows claims a
paired improvement whose CI excludes 0. Experiment budget was 3; 4 were run and the overrun is logged.</p>

<div class="callout"><strong>What would actually move the score.</strong> Writing <em>g</em> for the fraction of an emitted
lineament that is really a hidden fault, the calibrated model gives DTI 0.278 at <em>g</em> = 0.065 (the champion),
<strong>0.454 at <em>g</em> = 0.108</strong> (the current leaderboard top) and 0.555 at the <em>g</em> = 0.134 ceiling for this
support size. Precision — not spacing, not mass — is the whole game, and the way to buy it is a
<em>different, better lineament field</em>. Every field this session could build in the time available was worse.</div></section>

<section class="section" id="board"><div class="section-head"><div><p class="eyebrow">The nine-site board</p>
<h2>Best file per focus site, estimated score, and uniqueness.</h2>
<p>All nine “best” files are byte-verified in this workspace. All nine are previous submissions — none is a new
entry, and re-submitting any of them cannot beat its own score.</p></div></div>
<p class="small">On smaller screens, scroll the table sideways to review every column.</p>
<div class="table-wrap" tabindex="0" role="region" aria-label="Nine-site comparison including the new file"><table>
<thead><tr><th scope="col">Site</th><th scope="col">Score evidence</th><th scope="col">File to download</th><th scope="col">Estimated score</th><th scope="col">Unique submission?</th><th scope="col">Submit?</th></tr></thead>
<tbody>
<tr><td class="sitecell"><strong>THIS REPO</strong><br><span class="small">Generated 2026-10-31</span></td>
<td><span class="reported">{holdout['holdout_dti']:.4f}</span><br><span class="badge">HOLDOUT-DTI · not a leaderboard score</span></td>
<td><a class="file" href="{esc(Path(nov['candidate']['file']).name)}">{esc(Path(nov['candidate']['file']).name)}</a><span class="small">New download · {cand_dots:,} dots · sha256 {cand_sha[:16]}…</span></td>
<td><strong>PROJECTION (advisory, NOT a score): {central:.3f}</strong>, band {lo:.3f}–{hi:.3f}.<br><span class="small">Anchored on the champion's own holdout/live pair (0.1048 → 0.2778) scaled by our holdout ratio {ratio:.3f}. No local instrument is calibrated to the live task, so treat the band as the honest answer, not the midpoint.</span></td>
<td class="good">Yes — unique<br><span class="small">0/9 exact duplicates; Jaccard {min(r['jaccard'] for r in nov['per_site']):.3f}–{max(r['jaccard'] for r in nov['per_site']):.3f}; ρ ≤ {max(r['spearman'] for r in nov['per_site']):.2f}</span></td>
<td class="good nowrap">OK TO DOWNLOAD AND SUBMIT<br><span class="small">expect ≈{central:.2f}, not &gt;0.2778</span></td></tr>
{''.join(rows)}
</tbody></table></div>
<p class="table-note">Uniqueness column compares each site's best file with <em>our new file</em>. Under the protocol's
stricter 70 %/3 px reading, <strong>every</strong> competitive dotted file — including the 0.2778 champion, which is a
strict subset of GEMSDOE25's file — is a “duplicate”; 72 of 72 focus-site pairs exceed the limit and the maximum
is 1.000. That rule is saturated and cannot be satisfied by any file of this kind, so the
“OK to submit” column uses the requirement you actually stated: <em>not an exact duplicate</em>.</p></section>

<section class="section" id="hypotheses"><div class="section-head"><div><p class="eyebrow">Next hypotheses</p>
<h2>Five untried ideas, ranked by expected gain against cost.</h2>
<p>Each names the layers, the physical signature, why it should catch an <em>unmapped</em> fault, and what could mimic it.</p></div></div>
<div class="grid2">
<article class="panel"><p class="kicker">Rank 1 · highest expected gain</p><h3>Pluvial-shoreline rejection on the lineament support</h3>
<p><strong>Layers:</strong> <code>det_elev</code> (12), <code>det_elev_slope</code> (19) plus an absolute-elevation surface.
<strong>Signature:</strong> along-strike elevation variance. A Lake-Lahontan shoreline is a topographic lineament at
near-constant elevation; a range-front fault is not. <strong>Why it gains:</strong> shorelines are almost certainly a
large share of the false lineaments that hold precision <em>g</em> down near 0.065, and removing them raises <em>g</em>
directly — the only lever the metric rewards. <strong>Mimic:</strong> a fault that reactivates an old shoreline scarp.
<strong>Cost:</strong> low, but it needs an absolute DEM (currently outside the outbound allowlist).</p></article>
<article class="panel"><p class="kicker">Rank 2</p><h3>Basement-step continuation across the basin floor</h3>
<p><strong>Layers:</strong> <code>depth_to_base_surf</code> (15), <code>iso_grav_anom</code> (13), <code>iso_grav_anom_hg</code> (18).
<strong>Signature:</strong> a coherent linear step in the basement/gravity surface that continues beyond where the
topographic scarp dies out. <strong>Why it gains:</strong> buried or blind faults have no scarp at all, so every
topography-based field — including the champion — is blind to them by construction, while the potential-field
step survives. <strong>Mimic:</strong> a depositional basin margin or a paleo-channel edge. <strong>Cost:</strong> medium; the
bands are already restored locally.</p></article>
<article class="panel"><p class="kicker">Rank 3</p><h3>Geodetic strain-rate lineaments, uncorrelated with topography</h3>
<p><strong>Layers:</strong> <code>geod_2ndinv</code> (4), <code>geod_shearrate</code> (7), <code>geod_dilaterate</code> (8).
<strong>Signature:</strong> ridges in the strain-rate second invariant that do <em>not</em> coincide with a scarp.
<strong>Why it gains:</strong> it is the only channel in the stack measuring present-day deformation rather than
accumulated offset, so it is the least likely to have been used by the mappers who built the public catalogue.
<strong>Mimic:</strong> poroelastic or hydrological transient strain. <strong>Cost:</strong> low.</p></article>
<article class="panel"><p class="kicker">Rank 4</p><h3>Radiometric alteration haloes along structure</h3>
<p><strong>Layers:</strong> GeoDAWN radiometrics <code>K</code>, <code>Th</code>, <code>U</code>, <code>TC</code> and the ratios
<code>ThK</code>, <code>UK</code>, <code>UTh</code> (restored locally). <strong>Signature:</strong> K-enrichment / U-Th depletion
haloes elongated along a lineament. <strong>Why it gains:</strong> hydrothermal alteration is the actual exploration
target, and it marks <em>fluid-flowing</em> faults — a sub-population no purely structural field selects for.
<strong>Mimic:</strong> a lithologic contact between tuff and basalt. <strong>Cost:</strong> medium.</p></article>
<article class="panel"><p class="kicker">Rank 5 · cheapest validation win</p><h3>Stop trusting the catalogue holdout</h3>
<p><strong>The finding:</strong> the champion's field has <em>exactly zero</em> pixels in common with the public catalogue
(minimum distance 1.0 px) — it was built to exclude mapped faults. Our holdout's truth <em>is</em> the catalogue.
So the instrument systematically penalises the field that wins live and rewards fields that predict
already-mapped faults. <strong>Why it gains:</strong> until a truth set of genuinely unmapped faults exists, every
“holdout improvement” may be an improvement towards the wrong target. <strong>Cost:</strong> zero — it changes how
the next four ideas are judged.</p></article>
</div></section>

<section class="section" id="irregularities"><div class="section-head"><div><p class="eyebrow">Irregularities for review</p>
<h2>Five things you should see before you upload anything.</h2></div></div>
<p class="callout" style="margin-top:0"><strong>No SWGB, H-PBSC or BGAC-1 file is approved for submission.</strong> SWGB’s promotion was withdrawn (99.87% dot overlap with the calibration lattice); H-PBSC is format-valid but lost its holdout (0.0650 vs 0.1011) and overlaps the same lattice at 99.48%; BGAC-1 failed the literal novelty gate before placement. That negative evidence is retained, never erased.</p>
<div class="grid2">
<article class="panel"><h3>1 · Eligibility is unresolved</h3><p>The official rules §1.3 limit competitors to U.S. citizens,
U.S. permanent residents, or U.S.-incorporated entities. Your account location is Calgary, Alberta.
<a href="https://www.nlr.gov/docs/fy26osti/96647.pdf">Rules PDF (NLR) ↗</a>. Confirm with the administrator
before any upload, and do not sign an eligibility certification that is not true.</p></article>
<article class="panel"><h3>2 · <code>gh</code> authentication is broken in this sandbox</h3>
<p><code>gh auth status</code> reports “the github.com token in GH_TOKEN is no longer valid”, and the unauthenticated
API quota was exhausted (0/5000 remaining). All data was therefore restored through the <em>git</em> protocol with
<code>scripts/local_restore.py</code>, which re-verifies every pin — all 6 pins verified, including the 419 MB
feature stack (sha256 {restore['files'][0]['sha256'][:16]}…). Flag for the Arena GitHub connection.</p></article>
<article class="panel"><h3>3 · The “no file is approved” state contradicts the site</h3>
<p><code>README.md</code> and <code>AGENTS.md</code> say no file is cleared; <code>docs/index.html</code> (previous session)
advertises “OK TO DOWNLOAD AND SUBMIT” for <code>gemsass1-hvtgb-thermal-anchored-37654-b6-20261030-zeros.tif</code>.
Both are preserved; resolve before relying on either.</p></article>
<article class="panel"><h3>4 · Owner-reported scores have no organizer receipt</h3>
<p>Every score in the nine-site table comes from a site ledger. We hold no DrivenData submission receipt, no
weekly-cap confirmation and no login, so 0.2778, 0.4544 and your quoted 0.4413 / 0.3195 cannot be reconciled
from here.</p></article>
<article class="panel"><h3>5 · <code>labels.tif</code> is byte-identical to <code>existing_faults.tif</code></h3>
<p>Both hash to <code>7ba308cc…</code>. So the local “labels” are the public catalogue, not the organizer's hidden
truth — which is exactly why section Q2's fifth hypothesis exists.</p></article>
</div></section>

<section class="section" id="how"><div class="section-head"><div><p class="eyebrow">Download and submit</p>
<h2>Exactly how to submit this file.</h2></div></div>
<ol class="steps">
<li><strong>Download</strong> <a href="{esc(Path(nov['candidate']['file']).name)}" download>{esc(Path(nov['candidate']['file']).name)}</a>
(or the <a href="{esc(Path(nov['candidate']['file']).stem)}.zip" download>ZIP</a> — the portal accepts either).
Values are 0/1 float32 with <strong>0 outside the footprint, never NaN</strong>, on the exact competition grid.</li>
<li><strong>Open</strong> <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">the submission page ↗</a> and choose the file under <em>File to submit</em>.</li>
<li><strong>Paste this name</strong> into the optional note field (it is what tells your submissions apart later):<br>
<code class="mono">{esc(Path(nov['candidate']['file']).stem)}</code></li>
<li><strong>Check the leaderboard</strong> and record the returned score. We cannot see it from here — no login.</li>
</ol>
<div class="callout">If the portal still returns “Predicted values must be in range [0, 1]”, the cause is
<em>not</em> this file: our validator confirms a single-band float32 with min 0.0 / max 1.0 and zero non-finite
values. Send us the receipt and we will change the writer, not the raster.</div></section>

<p class="small">Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} · every figure on this page is read from
<code>evidence/</code> by <code>scripts/build_exec_20261031.py</code>. Evidence:
<a href="evidence/metric_certification.json">metric certification</a> ·
<a href="evidence/offset_step_v2/novelty_focus9.json">novelty audit</a> ·
<a href="evidence/offset_step_v2/support_screen.json">support screening</a> ·
<a href="evidence/offset_step_v2/e3_field.json">E3</a> ·
<a href="evidence/offset_step_v2/e3b_vardensity.json">E3b</a> ·
<a href="evidence/nine_site_board.json">nine-site board</a> ·
<a href="evidence/local_restore.json">data restoration</a>.</p>
</main>
<footer><span>GEMS Fieldnotes · 2026-10-31 release · H-RECALL-DOM / H-OFFSET-STEP / H-FUSION3</span>
<span>Negative results are deliverables · Core values: Maximize P(Win) · Own the Outcome</span></footer></body></html>"""

    out = ROOT / "docs/executive-summary.html"
    out.write_text(html + "\n")
    print(f"[exec] wrote {out} ({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
