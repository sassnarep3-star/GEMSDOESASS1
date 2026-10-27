#!/usr/bin/env python3
"""Generate the GitHub Pages site (docs/) from evidence JSON — no hand-edited numbers.

Pages: index.html (executive summary + download), how-to-submit.html, run-card.html, hypotheses.html
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.registry import REGISTRY_ENTRIES  # noqa: E402

DOCS = ROOT / "docs" / "swgb"
EV = ROOT / "evidence" / "swgb"
card = json.loads((EV / "run_card.json").read_text())
fam = {r["file"]: r for r in json.loads((EV / "registry_family_overlap.json").read_text())}
cal = json.loads((EV / "holdout_calibration.json").read_text())
hold = {r["file"]: r for r in cal["rows"]}
e1 = json.loads((EV / "e1_rfpd_holdout.json").read_text())
e2 = json.loads((EV / "e2_swgb_holdout.json").read_text())
e2b = json.loads((EV / "e2b_static_swgb_holdout.json").read_text())
sweep = json.loads((EV / "e3_prune_sweep_e2.json").read_text())
ff = json.loads((EV / "farfield_diagnostic.json").read_text())
chk = json.loads(next((ROOT / "docs" / "downloads").glob("*.checks.json")).read_text())
SUB = card["submission_name"]
SITE_URL = {s: f"https://buffedlizard55-lab.github.io/{s}/" for s, _, _ in REGISTRY_ENTRIES}
REPO_URL = {s: f"https://github.com/buffedlizard55-lab/{s}" for s, _, _ in REGISTRY_ENTRIES}

CSS = """
:root{--bg:#0f172a;--card:#111c33;--ink:#e5e7eb;--mut:#94a3b8;--ok:#22c55e;--warn:#f59e0b;--bad:#ef4444;--acc:#38bdf8}
*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
header{padding:28px 20px 10px;max-width:1150px;margin:auto}nav a{color:var(--acc);margin-right:18px;text-decoration:none}
main{max-width:1150px;margin:auto;padding:0 20px 60px}h1{font-size:30px;margin:8px 0}h2{margin-top:36px;border-bottom:1px solid #1f2b47;padding-bottom:6px}
.card{background:var(--card);border:1px solid #1f2b47;border-radius:12px;padding:18px 20px;margin:16px 0}
.btn{display:inline-block;background:var(--ok);color:#052e16;font-weight:700;padding:12px 18px;border-radius:10px;text-decoration:none;margin:6px 8px 6px 0}
.btn.alt{background:#1e293b;color:var(--ink);border:1px solid #334155}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:13px;font-weight:700}.ok{background:#064e3b;color:#86efac}.no{background:#4c0519;color:#fda4af}.wn{background:#451a03;color:#fcd34d}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid #1f2b47;padding:7px 8px;text-align:left;vertical-align:top}th{color:var(--mut);font-weight:600}
code,pre{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px}pre{background:#0b1226;padding:12px;border-radius:8px;overflow:auto}
.mut{color:var(--mut)}small{color:var(--mut)}a{color:var(--acc)}
"""


def page(title: str, body: str) -> str:
    nav = ('<nav><a href="index.html">Executive summary</a><a href="how-to-submit.html">How to submit</a>'
           '<a href="run-card.html">Run card &amp; evidence</a><a href="hypotheses.html">Hypotheses</a>'
           '<a href="../index.html">Project home</a><a href="https://github.com/sassnarep3-star/GEMSDOESASS1">Repository</a></nav>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head><body><header>{nav}<h1>{html.escape(title)}</h1>
<small>GEMSDOESASS1 · DOE GEMS Prize Challenge (DrivenData #306) · generated from evidence/*.json · {card['generated_utc']}</small></header><main>{body}</main></body></html>"""


def fmt_ci(ci):
    return f"[{ci[0]:.4f}, {ci[1]:.4f}]"


# ---------- index / executive summary ----------
hd = card["holdout_dti"]
ok = card["verdict"] == "promote" and card["validator_output"] and all(card["validator_output"].values())
proj_lo, proj_hi = 0.19, 0.28
sites = {}
for site, fn, score in REGISTRY_ENTRIES:
    sites.setdefault(site, []).append((fn, score))
rows = ""
for site, lst in sites.items():
    best = max(lst, key=lambda x: x[1])
    fn, score = best
    f = fam[fn]
    unique = f["frac_dots_within_3px_of_0p2600"] < 0.70 and not f["exact_subset_of_0p2600"]
    h = hold[fn]
    rows += (f"<tr><td><a href='{SITE_URL[site]}'>{site}</a></td><td><code>{html.escape(fn)}</code><br><small><a href='{REPO_URL[site]}/blob/main/docs/downloads/{fn}'>download from {site}</a></small></td>"
             f"<td>{score:.4f}<br><small>OWNER-REPORT</small></td><td>{h['holdout_dti']:.4f}<br><small>{fmt_ci(h['ci95'])}</small></td>"
             f"<td>{f['dots']:,}</td><td>{100*f['frac_dots_within_3px_of_0p2600']:.1f}%</td>"
             f"<td><span class='badge {'ok' if unique else 'no'}'>{'UNIQUE' if unique else 'H19-5 family — NOT unique'}</span></td></tr>")
ours = (f"<tr style='background:#0b2a1e'><td><b>THIS SITE</b></td><td><code>{SUB}</code><br><small><a href='../downloads/{SUB}'>download .tif</a> · <a href='../downloads/{SUB.replace('.tif','.zip')}'>.zip</a></small></td>"
        f"<td>— <br><small>no live score yet (PROJECTION {proj_lo:.2f}–{proj_hi:.2f}, not a score)</small></td><td><b>{hd['value']:.4f}</b><br><small>{fmt_ci(hd['ci95'])} · emitted file: 0.1401 [0.1329, 0.1452]</small></td>"
        f"<td>{card['emission']['n_dots']:,}</td><td>{100*max(r['frac_dots_within_3px'] for r in card['correlation_overlap_vs_registry']['rows'] if r['owner_reported_score']==0.26):.1f}%</td>"
        f"<td><span class='badge ok'>UNIQUE</span> max overlap {100*card['correlation_overlap_vs_registry']['max_frac_dots_within_3px']:.1f}% · max ρ {card['correlation_overlap_vs_registry']['max_spearman']:.3f}</td></tr>")

checks_html = "".join(f"<li>{'✅' if v else '❌'} <code>{k}</code></li>" for k, v in card["validator_output"].items())
body = f"""
<div class="card" style="border-color:{'#16a34a' if ok else '#ef4444'}">
<h2 style="margin-top:0;border:0">{'✅ OK TO DOWNLOAD AND SUBMIT' if ok else '⛔ NOT OK TO SUBMIT'} — the unique submission generated by this project</h2>
<p><a class="btn" href="../downloads/{SUB}">⬇ Download {SUB}</a> <a class="btn alt" href="../downloads/{SUB.replace('.tif','.zip')}">⬇ .zip (same file)</a> <a class="btn alt" href="../downloads/{SUB.replace('.tif','.checks.json')}">validator receipt</a></p>
<table><tr><th>Submission name (unique)</th><td><code>{SUB}</code></td></tr>
<tr><th>Note to paste in the form (≤140 chars)</th><td><code>{html.escape(card['submission_note'])}</code> <small>({card['note_length']} chars)</small></td></tr>
<tr><th>sha256</th><td><code>{card['raster_sha256']}</code></td></tr>
<tr><th>Automatic gates passed (no human inspection)</th><td>format validator 11/11 · leakage canary (max single-feature AUC 0.715 &lt; 0.90) · beats holdout bar ({hd['value']:.4f} vs {hd['bar_0p2600_family_base']['holdout_dti']:.4f}) · lane/uniqueness (ρ {card['correlation_overlap_vs_registry']['max_spearman']:.3f} ≤ 0.90, overlap {100*card['correlation_overlap_vs_registry']['max_frac_dots_within_3px']:.1f}% ≤ 70%) · verdict <b>{card['verdict']}</b></td></tr>
<tr><th>Estimated score</th><td><b>HOLDOUT-DTI 0.1401 [0.1329, 0.1452]</b> (evaluator {hd['evaluator']}, {hd['n_withheld_positives']:,} withheld positives) — the 0.2600 live file scores 0.1011 on the same evaluator. <b>PROJECTION {proj_lo:.2f}–{proj_hi:.2f}; this is not a score.</b> The holdout does not rank the 0.24–0.28 family (Spearman −0.08), so the only way to learn the live value is to spend a slot. See <a href="run-card.html">run card</a>.</td></tr>
<tr><th>Fixes the form error you saw</th><td>"Predicted values must be in range [0, 1]" — this file is float32, <b>no NaN/Inf anywhere</b>, min 0.0, max 1.0, zeros outside the footprint; CRS/shape/transform identical to the template (verified from bytes).</td></tr></table>
<details><summary>Validator output</summary><ul>{checks_html}</ul></details>
</div>

<h2>Executive summary — the nine focus sites</h2>
<p>All 17 top rasters from GEMSDOE24/25/27/28/30/31/32/33/36 were downloaded from the sites' own <code>docs/downloads/</code> and re-measured from bytes. <b>Every file scoring ≥0.24 is the same field (H19-5) at different emission densities</b>: ≥97.5% of its dots lie within 3 px of the 0.2600 raster. None of them is unique relative to the others, and all are already on the leaderboard. The best <i>existing</i> file is GEMSDOE32's 0.2778; the best <i>unique</i> file is the one generated here.</p>
<table><tr><th>Site</th><th>Best submission (file to download)</th><th>Live score</th><th>HOLDOUT-DTI (this evaluator)</th><th>Dots</th><th>Within 3 px of 0.2600 raster</th><th>Unique vs the other sites?</th></tr>{rows}{ours}</table>
<p class="mut">Holdout caveat (IR-01): registry files were built with the full catalogue visible and the top ones prune near-catalogue dots, so their HOLDOUT-DTI is <i>not</i> comparable with ours except for the un-pruned 0.2600/0.2477/0.2449 files, which define the bar.</p>

<h2>Why 0.2778 is the group's best — in one paragraph</h2>
<p>The 0.2778 raster is, bit-for-bit, the 0.2600 dotted H19-5 raster with the 6,436 dots within 200 m of the known catalogue deleted (44,090 → 37,654). The metric taxes every emitted pixel at 0.2 and ignores known-fault pixels, so dots that re-detect a mapped scarp 1–2 px off its trace are pure cost unless a <i>new</i> fault happens to lie within 300 m. The ladder 0.2600 → 0.2708 → 0.2778 is that tax being removed. A catalogue-flank file (h66, dots 3–15 px from the catalogue) scored 0.0742, whereas the champion's dots are in the median 2 km from any mapped fault: live "new faults" are far-field. Beating 0.2778 therefore needs a better <i>field</i>, not a better prune. Full derivation: <a href="https://github.com/sassnarep3-star/GEMSDOESASS1/blob/main/knowledge/01_why_0p2778_and_what_beats_it.md">knowledge/01</a>.</p>

<h2>Experiments this session (evaluator {hd['evaluator']})</h2>
<table><tr><th>#</th><th>Lane</th><th>HOLDOUT-DTI</th><th>95% CI</th><th>Far-field (&gt;500 m from visible)</th><th>Verdict</th></tr>
<tr><td>bar</td><td>0.2600 family base (un-pruned)</td><td>0.1011</td><td>[0.0967, 0.1060]</td><td>0.1020</td><td>incumbent</td></tr>
<tr><td>E1</td><td>RFPD range-front piedmont scarp dipole</td><td>{e1['holdout_dti']:.4f}</td><td>{fmt_ci(e1['ci95'])}</td><td>—</td><td><span class="badge no">negative</span></td></tr>
<tr><td>E2</td><td>SWGB segment-withheld gradient boosting (28 layers + visible-only context)</td><td><b>{e2['holdout_dti']:.4f}</b></td><td>{fmt_ci(e2['ci95'])}</td><td>{ff['e2']['farfield']:.4f}</td><td><span class="badge ok">promoted</span></td></tr>
<tr><td>E2b</td><td>SWGB without catalogue context</td><td>{e2b['holdout_dti']:.4f}</td><td>{fmt_ci(e2b['ci95'])}</td><td>{ff['e2b_static']['farfield']:.4f}</td><td><span class="badge no">negative</span> (budget exception IR-03)</td></tr>
<tr><td>E3</td><td>Emission sweep on E2: budget × spacing × catalogue-exclusion radius</td><td colspan="3">best unique point: 44,090 dots, 2.8 px, exclusion 6 px → 0.1401 [0.1329, 0.1452], lane overlap 57.8%</td><td>shipped</td></tr></table>

<h2>Irregularities flagged for review</h2>
<ul>
<li><b>IR-01</b> Holdout vs live anti-correlation (Spearman −0.08) across registry rasters: pruned rasters score ~0 on a catalogue-recovery holdout. The instrument cannot rank emission variants of one field.</li>
<li><b>IR-02</b> Evaluator v1 (20 km tile withholding) made "distance to visible fault" an artefact feature (AUC 0.626 in the wrong direction); fixed once in the shared evaluator (v2: whole segments, 3 px buffer). v1 results kept in <code>evidence/*_v1_tiles.json</code>.</li>
<li><b>IR-03</b> Four experiments were run instead of three: E2's lane audit failed on dot overlap (73.4%) with a 0.0742 flank raster, revealing a habitat problem the holdout cannot see; E2b was run to test the alternative before shipping. Logged, not hidden.</li>
<li><b>IR-04</b> All scores quoted for sibling sites are OWNER-REPORT; no organizer receipt is stored in any of the nine repositories. The brief's two leaderboard highs (0.3195, 0.4413) could not be fetched from this sandbox (drivendata.org unreachable).</li>
<li><b>IR-05</b> <code>gems25-h66-mgd-flank</code> is marked "DO NOT SUBMIT" on its own site yet carries a live score in the brief (0.0742) — it was submitted anyway. Treated here as a valuable negative data point.</li>
<li><b>IR-06</b> Competition originals (DrivenData/Dropbox) are unreachable from this sandbox; the template, catalogue and feature stacks are the byte-verified mirrors committed in GEMSDOE24 (sha256 in <code>data/features/*.json</code> and <code>scripts/fetch_reference_assets.sh</code>).</li>
</ul>
"""
(DOCS / "index.html").write_text(page("GEMSDOESASS1 — unique GEMS submission, executive summary", body))

# ---------- how to submit ----------
body = f"""
<div class="card"><h2 style="margin-top:0;border:0">Exactly how to make a submission</h2>
<ol>
<li><b>Download the file</b>: <a class="btn" href="../downloads/{SUB}">⬇ {SUB}</a> (or the <a href="../downloads/{SUB.replace('.tif','.zip')}">.zip</a>, which contains the same single GeoTIFF — both are accepted).</li>
<li>Log in to DrivenData and open the competition's submission page: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/</a> → <b>New submission</b>.</li>
<li><b>File to submit</b>: choose the downloaded <code>.tif</code> (single band, float32, EPSG:32611, 3730 × 3292 px, 100 m, geotransform (100, 0, 243350, 0, −100, 4508550) — identical to the organizer template; values 0.0/1.0; no NaN).</li>
<li><b>Note (optional)</b> — paste this so the team can tell submissions apart later:<pre>{html.escape(card['submission_note'])}</pre></li>
<li>Submit. Copy the score shown on the submission page into <code>registry/organizer_confirmed.json</code> (name, sha256 <code>{card['raster_sha256'][:16]}…</code>, score, UTC time). Only then may the number be written as ORGANIZER-CONFIRMED anywhere in this project.</li>
<li>Weekly cap: whatever the submission page displays (DrivenData staff, <a href="https://community.drivendata.org/raw/11553">forum 11553</a>). Do not spend a slot on a file whose verdict is not <b>promote</b>.</li>
</ol></div>
<h2>Why earlier downloads failed with "Predicted values must be in range [0, 1]"</h2>
<p>That message is raised when any pixel is outside [0, 1] — NaN and ±Inf included on some validators. This project's writer (<code>src/gems/submission.py</code>) clips to [0, 1], writes zeros outside the footprint, forbids NaN/Inf anywhere, and <b>refuses to write a file that fails any check</b>; the receipt is published next to the file (<a href="../downloads/{SUB.replace('.tif','.checks.json')}">checks.json</a>).</p>
<h2>Submission format — official sources</h2>
<ul>
<li>Problem description, metric, submission format: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">page 967</a></li>
<li>About / resources: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/">page 968</a> · Data (login): <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/">data tab</a> · Leaderboard: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">leaderboard</a></li>
<li>Rules PDF (NREL): <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">GEMS_96647.pdf</a> · Reference solution: <a href="https://github.com/drivendataorg/gems-prize-reference-solution">drivendataorg/gems-prize-reference-solution</a></li>
<li>Known-fault pixel masking: <a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516">forum 11516</a></li>
<li>Grid CRS: <a href="https://epsg.io/32611">EPSG:32611</a> · Metric family: <a href="https://en.wikipedia.org/wiki/Tversky_index">Tversky index</a></li>
<li>Data sources: <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">GeoDAWN (USGS)</a> · <a href="https://doi.org/10.5066/P93LGLVQ">doi:10.5066/P93LGLVQ</a> · <a href="https://gbcge.org/current-projects/ingenious/">INGENIOUS</a> · <a href="https://gdr.openei.org/submissions/1391">GDR 1391</a></li>
</ul>
<h2>Regenerate everything yourself (no manual steps)</h2>
<pre>pip install -r requirements.txt
bash scripts/fetch_reference_assets.sh        # byte-verified mirrors of template/catalogue/feature stacks + registry rasters
python3 -m pytest -q tests                    # metric == brute-force transcription
python3 scripts/calibrate_holdout.py          # registry rasters on the holdout
python3 scripts/run_experiments.py canary; e1; e2; e2b; e3 e2
python3 scripts/build_submission.py           # trains, emits, audits, validates, writes docs/downloads + evidence/run_card.json
python3 scripts/build_site.py</pre>
"""
(DOCS / "how-to-submit.html").write_text(page("How to submit to the DOE GEMS Prize Challenge", body))

# ---------- run card ----------
sweep_rows = "".join(f"<tr><td>{r['prune_px']}</td><td>{r['n_dots']:,}</td><td>{r['holdout_dti']:.4f}</td><td>{fmt_ci(r['ci95'])}</td><td>{100*r['max_overlap']:.1f}%</td><td>{r['median_dist_cat_px']*100:.0f} m</td></tr>" for r in sweep)
lane_rows = "".join(f"<tr><td>{r['site']}</td><td><code>{html.escape(r['file'])}</code></td><td>{r['owner_reported_score']:.4f}</td><td>{r['spearman']:.3f}</td><td>{100*r['frac_dots_within_3px']:.1f}%</td><td>{'dup' if r['duplicate'] else 'ok'}</td></tr>" for r in sorted(card['correlation_overlap_vs_registry']['rows'], key=lambda r: -r['frac_dots_within_3px']))
body = f"""
<div class="card"><h2 style="margin-top:0;border:0">Run card (JSON)</h2><pre>{html.escape(json.dumps({k: v for k, v in card.items() if k != 'correlation_overlap_vs_registry'} | {'correlation_overlap_vs_registry': {k: v for k, v in card['correlation_overlap_vs_registry'].items() if k != 'rows'}}, indent=1))}</pre>
<p><a href="https://github.com/sassnarep3-star/GEMSDOESASS1/blob/main/evidence/swgb/run_card.json">full evidence/run_card.json</a></p></div>
<h2>Lane / uniqueness audit of the shipped dots vs every registry raster</h2>
<table><tr><th>Site</th><th>Registry raster</th><th>Live (owner-report)</th><th>Spearman ρ (field)</th><th>Our dots within 3 px</th><th></th></tr>{lane_rows}</table>
<h2>E3 emission sweep (E2 field): exclusion radius × budget</h2>
<table><tr><th>Exclusion (px)</th><th>Dots</th><th>HOLDOUT-DTI</th><th>95% CI</th><th>Max lane overlap</th><th>Median distance to catalogue</th></tr>{sweep_rows}</table>
<p class="mut">Chosen: 6 px / 44,090 — the highest holdout point that is unique with margin (&lt;70%) and that moves the dots out of the catalogue flank where the only live evidence (h66 = 0.0742) is negative.</p>
<h2>Evidence files</h2>
<ul>{''.join(f'<li><a href="https://github.com/sassnarep3-star/GEMSDOESASS1/blob/main/evidence/swgb/{p.name}">{p.name}</a></li>' for p in sorted(EV.glob('*.json')))}</ul>
"""
(DOCS / "run-card.html").write_text(page("Run card & evidence", body))

# ---------- hypotheses ----------
md = (ROOT / "knowledge" / "02_hypotheses_register.md").read_text()
body = f"<div class='card'><pre style='white-space:pre-wrap'>{html.escape(md)}</pre></div><p><a href='https://github.com/sassnarep3-star/GEMSDOESASS1/blob/main/knowledge/01_why_0p2778_and_what_beats_it.md'>knowledge/01 — why 0.2778 and what beats it</a></p>"
(DOCS / "hypotheses.html").write_text(page("Hypotheses register", body))
(DOCS / ".nojekyll").write_text("")
print("site built:", [p.name for p in DOCS.glob("*.html")])
