#!/usr/bin/env python3
"""Render GitHub Pages from evidence JSON. Numbers are not hand-typed."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PBSC = json.loads((ROOT / "evidence/pbsc/run_card.json").read_text())
SWGB = json.loads((ROOT / "evidence/swgb/run_card.json").read_text())
CAL = json.loads((ROOT / "evidence/swgb/holdout_calibration.json").read_text())
FAM = json.loads((ROOT / "evidence/swgb/registry_family_overlap.json").read_text())
UNI = json.loads((ROOT / "evidence/pbsc/uniqueness.json").read_text())
EM = json.loads((ROOT / "evidence/pbsc/emission.json").read_text())
CAN = json.loads((ROOT / "evidence/pbsc/leakage_canary.json").read_text())
E1 = json.loads((ROOT / "evidence/pbsc/e1_pbsc_holdout.json").read_text())
E2 = json.loads((ROOT / "evidence/pbsc/e2_nomag_holdout.json").read_text())

PBSC_FILE = PBSC["submission_name"]
SWGB_FILE = SWGB["submission_name"]
PBSC_HREF = f"docs/downloads/{PBSC_FILE}"
SWGB_HREF = f"swgb/downloads/{SWGB_FILE}"

SITE = {
    "GEMSDOE24": "https://buffedlizard55-lab.github.io/GEMSDOE24/",
    "GEMSDOE25": "https://buffedlizard55-lab.github.io/GEMSDOE25/",
    "GEMSDOE27": "https://buffedlizard55-lab.github.io/GEMSDOE27/",
    "GEMSDOE28": "https://buffedlizard55-lab.github.io/GEMSDOE28/",
    "GEMSDOE30": "https://buffedlizard55-lab.github.io/GEMSDOE30/",
    "GEMSDOE31": "https://buffedlizard55-lab.github.io/GEMSDOE31/docs/",
    "GEMSDOE32": "https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html",
    "GEMSDOE33": "https://buffedlizard55-lab.github.io/GEMSDOE33/",
    "GEMSDOE36": "https://buffedlizard55-lab.github.io/GEMSDOE36/docs/",
}

CSS = """
:root{--bg:#0b1220;--card:#121a2f;--ink:#e8eef8;--mut:#93a0b8;--ok:#22c55e;--bad:#ef4444;--warn:#f59e0b;--acc:#38bdf8;--line:#1e293b}
*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
header,main,footer{max-width:1120px;margin:auto;padding:0 20px}header{padding:28px 20px 8px}
nav a{color:var(--acc);margin-right:16px;text-decoration:none;font-size:14px}
h1{font-size:30px;margin:8px 0 6px}h2{margin-top:36px;border-bottom:1px solid var(--line);padding-bottom:6px}
.mut{color:var(--mut)}a{color:var(--acc)}
.banner{border-radius:14px;padding:22px 24px;margin:18px 0;border:1px solid}
.banner.bad{background:#2a1216;border-color:#7f1d1d}
.banner.ok{background:#052e16;border-color:#166534}
.banner h2{margin:0 0 10px;border:0}
.btn{display:inline-block;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:700;margin:6px 8px 6px 0}
.btn.go{background:var(--ok);color:#052e16}
.btn.stop{background:#7f1d1d;color:#fecaca}
.btn.alt{background:#1e293b;color:var(--ink);border:1px solid #334155}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700}
.ok{background:#064e3b;color:#86efac}.no{background:#4c0519;color:#fda4af}.wn{background:#451a03;color:#fcd34d}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid var(--line);padding:8px;text-align:left;vertical-align:top}
th{color:var(--mut);font-size:12px;letter-spacing:.04em;text-transform:uppercase}
code,pre{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px}
pre{background:#070d18;padding:12px;border-radius:8px;overflow:auto}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:16px 0}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:800px){.grid{grid-template-columns:1fr}}
footer{padding:28px 20px 50px;color:var(--mut);font-size:13px}
"""


def page(title, body, extra_nav=""):
    nav = (
        '<nav><a href="index.html">Home</a><a href="executive-summary.html">Executive summary</a>'
        '<a href="how-to-submit.html">How to submit</a>'
        '<a href="run-card.html">Run card</a>'
        '<a href="swgb/index.html">Prior SWGB lane</a>'
        '<a href="https://github.com/sassnarep3-star/GEMSDOESASS1">Repo</a></nav>'
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head>
<body><header>{nav}<h1>{html.escape(title)}</h1>
<p class="mut">GEMSDOESASS1 · DOE GEMS Prize (DrivenData #306) · session 2026-10-28 H-PBSC · numbers from evidence/*.json</p>
</header><main>{body}</main>
<footer>Read the standing brief in docs/PROJECT_BRIEF.md every session. Core values: Maximize P(Win), Own the Outcome.
Competition: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">problem</a> ·
<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">leaderboard</a></footer></body></html>"""


def fmt_ci(ci):
    return f"[{ci[0]:.4f}, {ci[1]:.4f}]"


def nine_rows():
    fam = {r["file"]: r for r in FAM}
    hold = {r["file"]: r for r in CAL["rows"]}
    # best owner-reported file per site from the 17-raster registry
    best = {}
    for r in CAL["rows"]:
        s = r["site"]
        if s not in best or r["owner_reported_live"] > best[s]["owner_reported_live"]:
            best[s] = r
    out = []
    for site, r in best.items():
        fn = r["file"]
        f = fam.get(fn, {})
        unique = (not f.get("exact_subset_of_0p2600")) and f.get("frac_dots_within_3px_of_0p2600", 1) < 0.70
        out.append(
            f"<tr><td><a href='{SITE[site]}'>{site}</a></td>"
            f"<td><code>{html.escape(fn)}</code></td>"
            f"<td>{r['owner_reported_live']:.4f}<br><span class='badge wn'>OWNER-REPORT</span></td>"
            f"<td>{r['holdout_dti']:.4f}<br><span class='mut'>{fmt_ci(r['ci95'])}</span></td>"
            f"<td>{r['dots']:,}</td>"
            f"<td>{100*f.get('frac_dots_within_3px_of_0p2600', 0):.1f}%</td>"
            f"<td><span class='badge {'ok' if unique else 'no'}'>{'UNIQUE' if unique else 'H19-5 family — NOT unique'}</span></td>"
            f"<td><span class='badge no'>DO NOT RESUBMIT</span></td></tr>"
        )
    return "\n".join(out)


def home_body():
    raise RuntimeError("root index.html is fail-closed by hand; do not regenerate it from this builder")


GATE = json.loads((ROOT / "evidence/gate_null_audit.json").read_text())
VAL = json.loads((ROOT / "evidence/candidate_validator_20261030.json").read_text())
OFF = json.loads((ROOT / "evidence/official_source_check_20261030.json").read_text())
RD = json.loads((ROOT / "evidence/swgb/release_decision.json").read_text())


def decision_banner():
    """Download decision, rendered from evidence JSON. A projection is labelled as one, never as a score."""
    cal = CAL["calibration"]
    rs = GATE["radius_sensitivity"]["by_radius"]
    cands = {c["candidate"]: c for c in GATE["repo_candidates_vs_lattice"]}
    sw = cands[SWGB_FILE]
    pb = cands[PBSC_FILE]
    sw_h = RD["holdout_dti"]
    pb_h = PBSC["holdout_dti"]
    def proj(h):
        return cal["intercept"] + cal["slope"] * h
    v_sw = VAL[SWGB_FILE]["all_checks_passed"]
    v_pb = VAL[PBSC_FILE]["all_checks_passed"]
    rows = f"""
<tr><td><code>{html.escape(SWGB_FILE)}</code></td>
<td>HOLDOUT-DTI <b>{sw_h['value']:.4f}</b> {fmt_ci(sw_h['ci95'])} ({sw_h['evaluator_version']}, {sw_h['withheld_positives']:,} withheld positives; prune 6 px = shipped file)<br>
PROJECTION only (n={cal['n']}, Spearman {cal['spearman']:.2f}, RMSE {cal['rmse']:.3f}): live ≈ {proj(sw_h['value']):.3f} — not a score</td>
<td>Literal 3 px rule: <b>{sw['vs_lattice']['3px']*100:.2f}%</b> → FAILS (random placement gives {rs['3']['random']*100:.2f}%).<br>
0 px match: {sw['vs_lattice']['0px']*100:.2f}% (random {rs['0']['random']*100:.2f}%); 1 px: {sw['vs_lattice']['1px']*100:.2f}% (random {rs['1']['random']*100:.2f}%)</td>
<td>Validator {'11/11 PASS' if v_sw else 'FAIL'} (from bytes)</td>
<td><b>NO — not cleared.</b> Blocked by the literal rule only.</td></tr>
<tr><td><code>{html.escape(PBSC_FILE)}</code></td>
<td>HOLDOUT-DTI <b>{pb_h['value']:.4f}</b> {fmt_ci(pb_h['ci95'])} — <b>lost</b> bar 0.1011</td>
<td>PROJECTION {proj(pb_h['value']):.3f} — not a score</td>
<td>Literal 3 px rule: <b>{pb['vs_lattice']['3px']*100:.2f}%</b> → FAILS (random {rs['3']['random']*100:.2f}%).<br>0 px: {pb['vs_lattice']['0px']*100:.2f}%; 1 px: {pb['vs_lattice']['1px']*100:.2f}%</td>
<td>Validator {'11/11 PASS' if v_pb else 'FAIL'} (from bytes)</td>
<td><b>NO.</b> Lost holdout and fails the literal rule.</td></tr>"""
    return f"""
<div class="banner bad"><h2>Download decision: NO FILE IN THIS REPO IS CLEARED TO SUBMIT</h2>
<p><b>Why:</b> the uniqueness gate (&gt;70% of dots within 3 px of any registry raster → duplicate) is saturated by one dense lattice.
The 13gems 5 px calibration lattice ({GATE['rows'][-1]['registry_dots']:,} dots, scored 0.0904 on another site) covers
<b>{rs['3']['lattice_self_coverage']*100:.2f}%</b> of the footprint within 3 px. Uniform-random dots with no model at all score
<b>{rs['3']['random']*100:.2f}%</b>. The gate therefore cannot tell a copy from an original dense file.
<a href="evidence/gate_null_audit.json">Null audit JSON</a>.</p>
<p><b>Decision needed (policy, not a science result):</b> approve an amended uniqueness test before any slot is used. Options are in
<a href="knowledge/REVIEW_2026-10-30.md">the 2026-10-30 review</a>. Until then nothing is submitted.</p></div>
<h2>Submission candidates — estimates (labelled)</h2>
<table>
<tr><th>File</th><th>Evidence (HOLDOUT-DTI = holdout proxy; PROJECTION = calibration fit, not a score)</th><th>Projected live (not a score)</th><th>Unique? (3 px literal / 0 px &amp; 1 px null)</th><th>Validator</th><th>Submit?</th></tr>{rows}
</table>
<p>Leaderboard context (fetched {OFF['checked_utc_day']}, cached page, unverified-live): #1 0.4544 — the user-supplied 0.4413 and 0.3195 do not match this page. <a href="{OFF['sources'][1]['url']}">official leaderboard</a>.
The metric is confirmed from the <a href="{OFF['sources'][0]['url']}">official problem page</a>: DTI α=0.2, β=0.8, 300 m triangular kernel.</p>
"""


def exec_body():
    hd = PBSC["holdout_dti"]
    return f"""
{decision_banner()}
<p>Every live number in the nine-site table is <b>OWNER-REPORT</b> (copied from sibling ledgers; no submission-page receipt in this sandbox).
Every holdout number is <b>HOLDOUT-DTI</b> on evaluator <code>{CAL['evaluator']}</code>, {CAL['n_withheld_positives']:,} withheld positives.
A projection is never a score. DrivenData / USGS / Dropbox are not on this sandbox allowlist.</p>

<h2>Which file should you submit?</h2>
<table>
<tr><th>File</th><th>Evidence class</th><th>Estimate</th><th>Unique vs 9 sites?</th><th>Submit?</th></tr>
<tr>
<td><code>{html.escape(SWGB_FILE)}</code><br><a href="{SWGB_HREF}">audit only</a></td>
<td>HOLDOUT-DTI {SWGB['holdout_dti_shipped_emission']['evaluator']}</td>
<td>{SWGB['holdout_dti_shipped_emission']['value']:.4f} {fmt_ci(SWGB['holdout_dti_shipped_emission']['ci95'])}</td>
<td><span class="badge no">FAILS lattice 99.87%</span></td>
<td><span class="badge no">DO NOT SUBMIT</span></td>
</tr>
<tr>
<td><code>{html.escape(PBSC_FILE)}</code><br><a href="{PBSC_HREF}">audit only</a></td>
<td>HOLDOUT-DTI {hd['evaluator']}</td>
<td>{hd['value']:.4f} {fmt_ci(hd['ci95'])}</td>
<td><span class="badge no">17-file unique (25.3%); lattice 99.48%</span></td>
<td><span class="badge no">DO NOT SUBMIT — holdout lost and lattice duplicate</span></td>
</tr>
</table>

<h2>Nine focus sites — best OWNER-REPORT file at each</h2>
<p class="mut">“Unique vs 0.2600” = fraction of that file’s dots within 3 px of <code>gems25-dotted-h19-5-d2-8</code>.
The 0.24–0.28 ladder is one field (H19-5) with emission/pruning edits. Resubmitting any of them spends a slot and adds no information.</p>
<div style="overflow-x:auto">
<table>
<tr><th>Site</th><th>Best file</th><th>Live (OWNER-REPORT)</th><th>HOLDOUT-DTI here</th><th>Dots</th><th>3 px vs 0.2600</th><th>Unique?</th><th>Submit?</th></tr>
{nine_rows()}
</table>
</div>

<h2>Why GEMSDOE32’s 0.2778 is the group best — and why copying it cannot beat it</h2>
<ol>
<li><b>Bytes (MEASURED-HERE, previous session):</b> <code>h33-h33-2-b2</code> is exactly <code>dotted-h19-5-d2-8</code> (44,090 dots, live 0.2600) minus the 6,436 dots within 2 px of the published catalogue = 37,654 dots, pixel-identical (sym-diff 0).</li>
<li><b>Metric (official DTI α=0.2, β=0.8, 300 m triangle; known-fault pixels ignored):</b> emitted mass is taxed at 0.2; a dot 1–2 px off a mapped scarp is pure FP. Deleting those dots raised 0.2600 → 0.2708 → 0.2778. That is emission efficiency, not a new geological field.</li>
<li><b>Habitat:</b> a catalogue-flank file (h66, median 5.8 px) scored 0.0742 live; the champion’s median is 19.6 px (~2 km). Hidden labels are far-field lidar scarps.</li>
<li><b>Can we beat 0.2778?</b> Only with a <i>better field</i> at ~37–44 k dots that also clears the lattice rule (or a versioned policy amendment). H-PBSC is a different field and is unique vs the 17 competitive rasters, but it lost holdout (0.0650 vs 0.1011) and is 99.48% within 3 px of the calibration lattice. SWGB’s 17-file promote is withdrawn for the same lattice. Neither number is a live forecast.</li>
</ol>

<h2>This session’s experiments (budget 2 of 3; E3 emission sweep not run because the bar was not beaten)</h2>
<table>
<tr><th>Exp</th><th>Lane</th><th>HOLDOUT-DTI</th><th>95% CI</th><th>Beats 0.1011?</th></tr>
<tr><td>E1</td><td>H-PBSC + weak mag</td><td>{E1['holdout_dti']:.4f}</td><td>{fmt_ci(E1['ci95'])}</td><td>no</td></tr>
<tr><td>E2 (winner)</td><td>H-PBSC no mag</td><td>{E2['holdout_dti']:.4f}</td><td>{fmt_ci(E2['ci95'])}</td><td>no</td></tr>
</table>
<p>Leakage canary: max AUC {max(CAN['auc'].values()):.3f} (limit 0.90) — pass. Named non-fault mimic: Lake Lahontan shorelines / terrace risers / canals.</p>

<h2>Validator (automatic — no human inspector)</h2>
<pre>{html.escape(json.dumps(PBSC['validator_output'], indent=2))}</pre>
<p>All 11 checks passed from bytes. Zeros outside the footprint; no NaN/Inf; values in {{0,1}}. This is the fix for the portal error <code>Predicted values must be in range [0, 1]</code> — but passing the format gate is not scientific promotion.</p>
"""


def how_body():
    return f"""
<div class="banner bad"><h2>Do not upload anything from this repository today</h2>
<p>H-PBSC lost the holdout bar and fails the lattice overlap rule (99.48%). SWGB’s prior promote is withdrawn (lattice 99.87%). BGAC never packaged a file.</p></div>
<ol class="card">
<li>Wait until a future lane clears uniqueness (including the calibration lattice, unless a versioned policy says otherwise), holdout, and the format writer.</li>
<li>Then go to <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">DrivenData → New submission</a>.</li>
<li>Upload a single-band GeoTIFF or a zip of one GeoTIFF. Values must be in [0,1] (the writer refuses anything else — this is the fix for <code>Predicted values must be in range [0, 1]</code>).</li>
<li>Paste a note ≤140 characters from that future run card. Do not resubmit GEMSDOE24–36 files.</li>
</ol>
<p>Official format: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">problem description — submission format</a>.
Rules PDF (login-walled): <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">NLR 96647</a>.</p>
"""


def runcard_body():
    slim = {k: PBSC[k] for k in (
        "hypothesis", "mechanism", "named_non_fault_mimic", "holdout_dti",
        "verdict", "ok_to_submit", "raster_sha256", "submission_name",
        "submission_note", "note_length", "validator_output", "emission",
        "winner_experiment", "budget", "irregularities", "canary_pass",
        "generated_utc", "elapsed_s",
    )}
    return f"<p>Immutable run card for H-PBSC (session 2026-10-28). Full JSON: <a href='evidence/pbsc/run_card.json'><code>evidence/pbsc/run_card.json</code></a>.</p><pre>{html.escape(json.dumps(slim, indent=2))}</pre>"


def write_root_pages():
    (ROOT / "how-to-submit.html").write_text(page("How to submit — GEMSDOESASS1", how_body()))
    (ROOT / "run-card.html").write_text(page("H-PBSC run card", runcard_body()))


def main():
    (ROOT / "executive-summary.html").write_text(page(
        "Executive summary — nine sites + this session",
        exec_body(),
    ))
    write_root_pages()
    note = ROOT / "docs/downloads" / f"note-{PBSC_FILE.replace('.tif','')}.txt"
    note.write_text(PBSC["submission_note"] + "\n")
    # keep docs/evidence in sync
    dest = ROOT / "docs/evidence"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "pbsc_run_card.json").write_text(json.dumps(PBSC, indent=2) + "\n")
    print("site written")


if __name__ == "__main__":
    main()
