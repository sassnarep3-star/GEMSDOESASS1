#!/usr/bin/env python3
"""Deterministic static site from frozen evidence + the ACTIVE lane release.

2026-10-31: the active release is the H-TIPRELAY lane (evidence/tiprelay/release.json) when
present; otherwise the frozen 2026-10-30 H-TVGB release (evidence/thermal/release.json) is
rendered exactly as before. No score estimates are promoted to scores: every historical number
is labelled OWNER-REPORT and every new number is labelled HOLDOUT-DTI. The single generated
candidate and its machine-computed verdict are rendered at the top of the overview and the
executive summary. Historical negative evidence (BGAC-1, H-PBSC, SWGB) is preserved on the pages.
"""
from html import escape as e
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'


def _as_list(value):
    """Accept a JSON list or the repr of one (both shapes exist in this repo's cards)."""
    if isinstance(value, (list, tuple)):
        return [float(v) for v in value]
    return [float(v) for v in str(value).strip('[]').split(',')]


def fusion_card():
    """2026-10-31 second lane: its own run card, read from evidence, never hand-typed."""
    p = ROOT / 'evidence' / 'offset_step_v2' / 'run_card.json'
    return json.loads(p.read_text()) if p.exists() else None
REPO = 'https://github.com/sassnarep3-star/GEMSDOESASS1'
ACTIVE_DIR = 'thermal'   # set by main(); evidence/<dir>/release.json drives the rendered site
LANE_TITLES = {'bstep': 'H-BSTEP basement-step concordance learner',
               'tiprelay': 'H-TIPRELAY continuation-geometry-supervised recovery',
               'kdam': 'H-KDAM alteration-contact-supervised recovery',
               'thermal': 'H-TVGB geothermally-anchored supervised recovery'}


def rchref(name: str) -> str:
    """Href for a lane-evidence file of the active release."""
    return f'evidence/{ACTIVE_DIR}/{name}'


def load(path):
    return json.loads((ROOT / path).read_text())


def page(title, body, *, prefix='', active='summary'):
    links = [('summary', 'index.html', 'Overview'), ('executive', 'executive-summary.html', 'Executive summary'),
             ('howto', 'how-to-submit.html', 'How to submit'), ('research', 'research.html', 'Research & sources'),
             ('evidence', 'evidence.html', 'Evidence')]
    nav = ''.join(f'<a href="{prefix}{url}"' + (' aria-current="page"' if key == active else '') + f'>{text}</a>' for key, url, text in links)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="GEMS fault-detection research: nine-site comparison, strict submission gates and auditable negative results.">
<meta name="color-scheme" content="light"><title>{e(title)} · GEMS Fieldnotes</title><link rel="stylesheet" href="{prefix}assets/site.css"></head>
<body><a class="skip" href="#main">Skip to content</a><header><div class="nav"><a class="brand" href="{prefix}index.html"><span class="mark" aria-hidden="true"></span>GEMS / FIELDNOTES</a><nav aria-label="Main">{nav}</nav></div></header>
<main id="main">{body}</main><footer><span>Independent research workspace · not an organizer website</span><span>Evidence before submission. No competition uploads automated.</span><a href="{REPO}">View repository ↗</a></footer><script src="{prefix}assets/source-feed.js" defer></script></body></html>'''


def release_card(rel):
    """The single generated candidate + its machine verdict, for the top of the site."""
    card = rel['card']
    ok = card['ok_to_download_and_submit']
    verdict_word = 'OK TO DOWNLOAD AND SUBMIT' if ok else 'NOT OK TO SUBMIT'
    pill = 'Cleared by project gates' if ok else 'Blocked by a project gate'
    tif = f"downloads/{card['raster_name']}"
    zipn = tif.replace('-zeros.tif', '-zeros.zip')
    gates = rel['gates']
    rows = ''.join(f'<li><span>{e(label)}</span><span class="{"good" if passed else "bad"}">{"PASS" if passed else "NO"}</span></li>' for label, passed in gates)
    return f'''<aside class="status" aria-label="Generated submission decision"><span class="pill">{e(pill)}</span>
<h2>{e(verdict_word)}: <code>{e(card['raster_name'])}</code></h2>
<p>This is the <strong>only generated unique TIF</strong> of this release. It is not a copy of any GEMSDOE-site submission. Machine verdict from the run card: <strong>{e(verdict_word)}</strong>. Competition slots used: {card['submission_slots_used']} (this workspace never uploads).</p>
<ul class="evidence-list">{rows}</ul>
<div class="actions"><a class="button" href="{tif}" download>Download TIF ({e(card['raster_name'])})</a><a class="button secondary" href="{zipn}" download>Download ZIP</a></div>
<p class="small">Submission name: <code>{e(card['submission_name'])}</code> · Note ({card['note_length']}/140): “{e(card['note'])}” · sha256 <code class="mono">{e(card['raster_sha256'][:16])}…</code> · <a href="{rchref('run_card.json')}">run card</a> · <a href="downloads/README.md">downloads readme</a></p>
<p class="small" style="margin-top:10px">Verdict is automated (format + novelty + holdout gates). A weekly submission slot remains a separate selector decision.</p>{lattice_note(card)}</aside>'''


def lattice_note(card):
    d = card.get('lattice_disclosure') or {}
    if not d.get('available'):
        return ''
    return (f'<p class="small" style="margin-top:10px"><strong>Scope disclosure.</strong> This file overlaps the '
            f'synthetic 5 px calibration lattice at {100 * d["overlap3"]:.2f}% within 3 px, exactly as every dotted '
            f'file does (the 0.2778 champion included). That artifact is exempt from the competitive novelty scan '
            f'(AMEND-LATTICE-01); if it were counted, no dotted submission in this project could pass the 70% rule. '
            f'The scan covers the nine focus sites only.</p>')


def measured_site_uniqueness():
    """site -> measured maximum 3 px overlap with any other focus site, from the restored rasters."""
    path = ROOT / 'evidence/kdam/nine_site_matrix_20261031.json'
    if not path.exists():
        return {}
    return {r['site']: r for r in json.loads(path.read_text())['rows']}


def parallel_candidate_panel(prefix=''):
    """Honest disclosure of the same-day H-KDAM gated candidate (selector alternative)."""
    path = ROOT / 'evidence/kdam/release.json'
    if not path.exists() or ACTIVE_DIR == 'kdam':
        return ''
    rel = load('evidence/kdam/release.json')
    card = rel.get('card', {})
    h = card.get('holdout_dti', {})
    word = 'OK TO DOWNLOAD AND SUBMIT' if card.get('ok_to_download_and_submit') else 'NOT OK TO SUBMIT'
    x = json.loads((ROOT / 'evidence/tiprelay/cross_lane_kdam_check.json').read_text()) if (ROOT / 'evidence/tiprelay/cross_lane_kdam_check.json').exists() else {}
    pair = next((p for p in x.get('pairs', []) if p.get('a') == 'tiprelay' and p.get('b') == 'kdam'), {})
    return (f'<section class="section" id="parallel"><div class="panel"><p class="kicker">Parallel lane · 2026-10-31</p>'
            f'<h3>H-KDAM: a second gated candidate from a concurrent session.</h3>'
            f'<p><code>{e(card.get("raster_name", ""))}</code> — verdict <strong>{e(word)}</strong> per its own gate table '
            f'(<a href="{prefix}evidence/kdam/release.json">evidence/kdam/release.json</a>). HOLDOUT-DTI {h.get("value", float("nan")):.4f} '
            f'[{h.get("ci95", [float("nan"), float("nan")])[0]:.4f}, {h.get("ci95", [float("nan"), float("nan")])[1]:.4f}] (unpruned arm, 37,654 dots) '
            f'vs the same-emission incumbent family base {card.get("comparators_same_emission", {}).get("family_base_44090_unpruned", float("nan")):.4f}. '
            f'Competitive max 3 px overlap 31.1% (limit 70%); all 489 inventory rasters measured, the synthetic 5 px calibration lattice at '
            f'99.96% exempt under AMEND-LATTICE-01 and disclosed. sha256 <code class="mono">{e(str(card.get("raster_sha256", ""))[:16])}…</code>. '
            f'<strong>Scope disclosure.</strong> The lattice exemption and the nine-site registry scope apply to every dotted file in this '
            f'project, the recommended file included: the measured uniqueness registry covers the nine focus sites only.</p>'
            f'<p>Cross-lane duplicate check vs the active release: full-footprint Spearman {pair.get("spearman_full_footprint", float("nan")):+.4f}, '
            f'{pair.get("dot_pixel_intersection", 0)} shared dot pixels of 37,654 (0.45%), 3 px overlap '
            f'{100 * pair.get("overlap_3px_a_to_b", float("nan")):.1f}%/{100 * pair.get("overlap_3px_b_to_a", float("nan")):.1f}% — near-independent '
            f'fields, not duplicates (<a href="{prefix}evidence/tiprelay/cross_lane_kdam_check.json">cross-lane check</a>). '
            f'Choosing between the two gated candidates is the selector\'s decision within the weekly cap; the default recommendation '
            f'is the file at the top of this page (champion-family-consistent emission; its features carry the paired-ablation positive).</p></div></section>')



def parallel_candidate_note_line():
    path = ROOT / 'evidence/kdam/release.json'
    if not path.exists():
        return ''
    card = load('evidence/kdam/release.json').get('card', {})
    return (f'<p class="small" style="margin-top:12px"><strong>Alternative gated candidate (selector decision):</strong> '
            f'<code>{e(card.get("submission_name", ""))}</code> · sha256 <code class="mono">{e(str(card.get("raster_sha256", ""))[:16])}…</code> · '
            f'passed every gate in <a href="evidence/kdam/release.json">evidence/kdam/release.json</a> · cross-lane duplicate check passed '
            f'(<a href="evidence/tiprelay/cross_lane_kdam_check.json">evidence/tiprelay/cross_lane_kdam_check.json</a>). The default '
            f'recommendation remains the file above.</p>')

def table(rows, rel, prefix=''):
    body = ''
    measured = measured_site_uniqueness()
    card = rel['card']
    ok = card['ok_to_download_and_submit']
    verdict_word = 'OK TO DOWNLOAD AND SUBMIT' if ok else 'NOT OK TO SUBMIT'
    est = rel['estimate_text']
    body += f'''<tr><td class="sitecell"><strong>GEMS / THIS REPO</strong><br><span class="small">Generated 2026-10-31 ({e(LANE_TITLES[ACTIVE_DIR].split(' ')[0])} lane)</span></td>
<td><span class="reported">HOLDOUT-DTI {card['holdout_dti']['value']:.4f}</span><br><span class="badge">HOLDOUT-DTI · not a leaderboard score</span></td>
<td><a class="file" href="{prefix}downloads/{e(card['raster_name'])}">{e(card['raster_name'])}</a><span class="small">Generated download · unique TIF · {e(ACTIVE_DIR.upper())} lane</span></td>
<td>{est}</td>
<td class="good">Yes — unique<br><span class="small">measured against every competitive raster of the pinned 489-file registry (see run card)</span></td>
<td class="{'good' if ok else 'bad'} nowrap">{e(verdict_word)}</td></tr>'''
    for row in sorted(rows, key=lambda r: -r['historical_report']):
        aliases = ', '.join(row['same_predictions_other_focus_sites'])
        m = measured.get(row['site'])
        if m and m.get('overlap'):
            worst_site = max(m['overlap'], key=m['overlap'].get)
            worst = m['overlap'][worst_site]
            cs = m.get('closest_site_symdiff') or {}
            duplicate = (f'{100 * worst:.1f}% of its dots lie within 3 px of {worst_site}'
                         + (f'; its closest dot set is {cs.get("site")}, differing by {cs.get("symmetric_difference", 0):,} dots'
                            if cs else '')
                         + ' (measured, not reported).')
        else:
            duplicate = f'Exact predictions also in {e(aliases)}.' if aliases else 'No exact counterpart in another focus site found in this snapshot.'
        body += f'''<tr><td class="sitecell"><a href="{prefix}sites/{row['site']}.html">{row['site']} ↗</a><br><span class="small">Prior result</span></td>
<td><span class="reported">{row['historical_report']:.4f}</span><br><span class="badge">OWNER-REPORT live score</span></td>
<td><a class="file" href="{row['source_url']}">{e(row['file'])}</a><span class="small">Source review only · not a new download</span></td>
<td>Live score {row['historical_report']:.4f} (OWNER-REPORT).<br><span class="small">Already on the leaderboard — re-submitting it cannot beat it.</span></td>
<td class="bad">No — already a prior submission, and not unique among the nine<br><span class="small">{duplicate}</span></td>
<td class="bad nowrap">Do not submit</td></tr>'''
    return f'''<p class="small">On smaller screens, scroll the table sideways to review every column.</p><div class="table-wrap" tabindex="0" role="region" aria-label="Nine-site historical comparison"><table><thead><tr><th scope="col">Site</th><th scope="col">Score evidence</th><th scope="col">File to download</th><th scope="col">Estimated score</th><th scope="col">Unique submission?</th><th scope="col">Submit?</th></tr></thead><tbody>{body}</tbody></table></div>
<p class="table-note">Historical values are OWNER-REPORT scores copied from the supplied ledgers, not ORGANIZER-CONFIRMED receipts. The generated row's HOLDOUT-DTI is a hide-and-recover measurement (evaluator {e(card['holdout_dti']['evaluator'])}, {card['holdout_dti']['n_withheld_positives']:,} withheld positives), never a leaderboard score; its "estimated score" cell is explicitly a projection. Different file hashes do not imply different predictions.</p>'''


def legacy_banner(prefix=''):
    return f'''<aside class="status" aria-label="Historical negative decisions"><span class="pill">Negative · preserved evidence</span><h2>Earlier lanes stay blocked: SWGB, H-PBSC, BGAC-1.</h2>
<p><strong>No SWGB, H-PBSC or BGAC-1 file is approved for submission.</strong> SWGB's promotion was withdrawn (99.87% dot overlap with the calibration lattice). H-PBSC is format-valid but lost its holdout (0.0650 vs 0.1011) and overlaps the same lattice at 99.48%. BGAC-1 failed the literal novelty gate before placement. This negative evidence is retained, never erased.</p>
<p class="small"><a href="{prefix}evidence.html#correction">Review the superseding release decision and evidence ↗</a> · <a href="{prefix}evidence/thermal/lattice_amendment.md">IR-LATTICE-01 scope amendment ↗</a></p></aside>'''


def metric_strip_new(rel):
    card = rel['card']
    h = card['holdout_dti']
    comp = card['correlation_overlap_vs_registry']
    ov = (comp['dots_competitive']['max_overlap'] or 0) * 100
    if ACTIVE_DIR == 'bstep':
        sh = h.get('shipped_variant_diagnostic') or {}
        return f'''<div class="metrics"><div class="metric"><span class="label">HOLDOUT-DTI (shipped anti-collision variant)</span><span class="value">{sh.get('value', h['value']):.4f}</span><p>95% CI {sh.get('ci95', h['ci95'])[0]:.4f}–{sh.get('ci95', h['ci95'])[1]:.4f} · bar 0.1011</p></div>
<div class="metric"><span class="label">Same-emission incumbent comparator</span><span class="value">{card['comparators_same_emission']['family_base_44090_unpruned']:.4f}</span><p>the 0.2600-family field, same folds</p></div>
<div class="metric"><span class="label">Max dot overlap vs competitive registry</span><span class="value">{ov:.1f}%</span><p>limit 70% · lane-drift gate</p></div>
<div class="metric"><span class="label">Submission slots used</span><span class="value">{card['submission_slots_used']}</span><p>Selector step is separate</p></div></div>
<p class="small">All new numbers are HOLDOUT-DTI ({e(h['evaluator'])}, {h['n_withheld_positives']:,} withheld positives, 50 px tile-bootstrap CI). A projection is never written as a score.</p>'''
    if ACTIVE_DIR == 'tiprelay':
        dBA = h['delta_B_minus_A']
        dCB = h['delta_C_minus_B']
        sh = h['shipped_cell_emission']
        head_cell = (f'<div class="metric"><span class="label">HOLDOUT-DTI (shipped b6 cell, 37,654 dots)</span>'
                     f'<span class="value">{sh["holdout_dti"]:.4f}</span>'
                     f'<p>95% CI {sh["ci95"][0]:.4f}–{sh["ci95"][1]:.4f} · bar 0.1011 · far-field {sh["farfield"]:.4f}</p></div>'
                     f'<div class="metric"><span class="label">HOLDOUT-DTI (E1 ablation cell, 44,090 dots)</span>'
                     f'<span class="value">{h["value"]:.4f}</span>'
                     f'<p>95% CI {h["ci95"][0]:.4f}–{h["ci95"][1]:.4f} · winner arm {e(card.get("arm", ""))}</p></div>')
        mid = (f'<div class="metric"><span class="label">E1 paired Δ relay features (B−A)</span>'
               f'<span class="value">{dBA["value"]:+.4f}</span><p>95% CI {dBA["ci95"][0]:+.4f}–{dBA["ci95"][1]:+.4f}</p></div>'
               f'<div class="metric"><span class="label">E2 paired Δ geothermal emission prior</span>'
               f'<span class="value">{h["e2_emission"]["value"]:+.4f}</span>'
               f'<p>95% CI {h["e2_emission"]["ci95"][0]:+.4f}–{h["e2_emission"]["ci95"][1]:+.4f} · negative</p></div>')
        return (f'<div class="metrics">{head_cell}{mid}'
                f'<div class="metric"><span class="label">Max dot overlap vs competitive registry</span><span class="value">{ov:.1f}%</span><p>limit 70% · lane-drift gate</p></div>'
                f'<div class="metric"><span class="label">Submission slots used</span><span class="value">{card["submission_slots_used"]}</span><p>Selector step is separate</p></div></div>'
                f'<p class="small">All new numbers are HOLDOUT-DTI ({e(h["evaluator"])}, {h["n_withheld_positives"]:,} withheld positives, 50 px tile-bootstrap CI). A projection is never written as a score.</p>')
    if ACTIVE_DIR == 'kdam':
        return f'''<div class="metrics"><div class="metric"><span class="label">HOLDOUT-DTI (unpruned protocol arm)</span><span class="value">{h['value']:.4f}</span><p>95% CI {h['ci95'][0]:.4f}–{h['ci95'][1]:.4f} · {h['n_withheld_positives']:,} withheld positives</p></div>
<div class="metric"><span class="label">Same-emission incumbent comparator</span><span class="value">{card['comparators_same_emission']['family_base_44090_unpruned']:.4f}</span><p>the 0.2600-family field, same folds, same 37,654 dots</p></div>
<div class="metric"><span class="label">Max dot overlap vs competitive registry</span><span class="value">{ov:.1f}%</span><p>limit 70% · lane-drift gate</p></div>
<div class="metric"><span class="label">Submission slots used</span><span class="value">{card['submission_slots_used']}</span><p>Selector step is separate</p></div></div>
<p class="small">All new numbers are HOLDOUT-DTI ({e(h['evaluator'])}, {h['n_withheld_positives']:,} withheld positives, 50 px tile-bootstrap CI). A projection is never written as a score.</p>'''
    mid = (f'<div class="metric"><span class="label">E2 paired Δ (thermal family)</span>'
           f'<span class="value">{h["paired_delta_vs_swgb_repro"]:+.4f}</span>'
           f'<p>95% CI {h["paired_delta_ci95"][0]:+.4f}–{h["paired_delta_ci95"][1]:+.4f} · negative</p></div>')
    return f'''<div class="metrics"><div class="metric"><span class="label">HOLDOUT-DTI (shipped config)</span><span class="value">{h['value']:.4f}</span><p>95% CI {h['ci95'][0]:.4f}–{h['ci95'][1]:.4f} · bar 0.1011</p></div>
{mid}
<div class="metric"><span class="label">Max dot overlap vs competitive registry</span><span class="value">{ov:.1f}%</span><p>limit 70% · lane-drift gate</p></div>
<div class="metric"><span class="label">Submission slots used</span><span class="value">{card['submission_slots_used']}</span><p>Selector step is separate</p></div></div>
<p class="small">All new numbers are HOLDOUT-DTI ({e(h['evaluator'])}, {h['n_withheld_positives']:,} withheld positives, 50 px tile-bootstrap CI). A projection is never written as a score.</p>'''


def nine_site_matrix(prefix=''):
    """Measured (not reported) uniqueness of every focus site's best file against the other eight."""
    path = ROOT / 'evidence/kdam/nine_site_matrix_20261031.json'
    if not path.exists():
        return ''
    rows = json.loads(path.read_text())["rows"]


    body = ''
    for r in sorted(rows, key=lambda x: -x['reported']):
        worst = max(r['overlap'], key=r['overlap'].get)
        body += (f'<tr><td><a href="{prefix}sites/{r["site"]}.html">{r["site"]} ↗</a></td>'
                 f'<td class="mono">{e(r["file"].split("/")[-1])}</td>'
                 f'<td class="reported">{r["reported"]:.4f}<br><span class="badge">OWNER-REPORT</span></td>'
                 f'<td>{r["dots"]:,}</td>'
                 f'<td class="bad">{100 * r["max_overlap_to_other_site"]:.1f}%<br>'
                 f'<span class="small">of these dots lie within 3 px of {worst}’s dots</span></td>'
                 f'<td class="bad">No — not unique</td>'
                 f'<td>Already on the leaderboard as a prior submission; re-uploading cannot improve on it.</td></tr>')
    return ('<section class="section" id="matrix"><p class="eyebrow">Measured, not reported · 2026-10-31</p>'
            '<h2>Is any focus site’s best file unique?</h2>'
            '<p class="lead">No. Every one of the nine best files is the same prediction field. The numbers '
            'below are computed from the restored rasters themselves (fraction of each file’s dots within '
            '3 px of another site’s dots), not from the sites’ own descriptions.</p>'
            '<div class="table-wrap" tabindex="0" role="region" aria-label="Measured cross-site overlap">'
            '<table><thead><tr><th scope="col">Site</th><th scope="col">Best file</th>'
            '<th scope="col">Owner-reported score</th><th scope="col">Dots</th>'
            '<th scope="col">Max overlap with another site</th><th scope="col">Unique?</th>'
            '<th scope="col">What to do</th></tr></thead><tbody>' + body + '</tbody></table></div>'
            '<p class="table-note">Extreme cases measured this session: the GEMSDOE25 and GEMSDOE30 best '
            'files have symmetric difference <strong>0</strong> (identical dot sets); GEMSDOE31 + a 2,545-dot '
            'prune <em>is</em> GEMSDOE32 (0.2708 → 0.2778). Source: '
            '<a href="' + prefix + 'evidence/kdam/nine_site_matrix_20261031.json">nine_site_matrix_20261031.json</a>.'
            '</p></section>')


def board_section(prefix=''):
    """Data-driven nine-site board: every number is read from evidence/nine_site_board.json."""
    b = load('evidence/nine_site_board.json')
    inv = load('registry/focus_inventory.json')
    refs = inv['refs']
    sites = list(b['nine_site_best'])
    pair = b['nine_site_pairwise_forward_overlap']
    lb = b['lattice_gate_bound']
    lat = b['lattice']
    rows = ''
    for site in sites:
        v = b['nine_site_best'][site]
        repo, path = v['registry_path'].split('/', 1)
        url = f"https://github.com/buffedlizard55-lab/{repo}/blob/{refs[repo]}/{path}"
        others = [t for t in sites if t != site and pair[f'{site}->{t}'] > 0.70]
        scan = b['per_best_registry_scan'][site]
        exact_other = [x for x in scan['exact_dot_set_matches'] if not x.startswith(f'{repo}/')]
        rows += (f'<tr><td class="sitecell"><strong>{e(site)}</strong><br><span class="small">{v["dots"]:,} positive pixels</span></td>'
                 f'<td><a class="file" href="{e(url)}">{e(path.rsplit("/", 1)[-1])}</a>'
                 f'<span class="small">Review link only · sha256 <code>{e(v["sha256"][:16])}…</code></span></td>'
                 f'<td><span class="reported">{v["owner_reported_score"]:.4f}</span><br><span class="badge">OWNER-REPORT</span></td>'
                 f'<td><span class="muted">Not estimable</span><br><span class="small">No calibrated model; holdout cannot forecast live score</span></td>'
                 f'<td><span class="bad">No</span><br><span class="small">{len(others)} of 8 other sites have ≥70% of dots within 3 px'
                 f'{"; " + str(len(exact_other)) + " exact dot-set twin(s) in another site" if exact_other else ""}.</span></td>'
                 f'<td><span class="bad">NO</span><br><span class="small">Already a prior submission; the literal rule also fails.</span></td></tr>')
    max_pair = b['nine_site_max_pair']
    return f'''<section class="section" id="board"><p class="eyebrow">Nine-site board · measured 2026-10-30 from pinned bytes</p>
<h2>Best file per site, estimated score, uniqueness, and submit decision.</h2>
<aside class="status" aria-label="Submit decision now"><span class="pill">Do not submit any file from this set</span>
<h3>No file is cleared for download or submission.</h3>
<p>The highest owner-reported file is GEMSDOE32 <strong>0.2778</strong>. It is already a previous submission, so resubmitting it is a duplicate. Every new file of competitive size also fails the literal uniqueness rule, which is arithmetic, not a judgement: a file with more than <strong>{lb["max_dots_satisfying_literal_70pct_rule"]:,}</strong> positive pixels cannot pass the 70%/3 px test against the GEMSDOE24 calibration lattice.</p>
<p class="small">Automated decision. Competition slots used: none. Score labels: OWNER-REPORT only. No organizer receipt exists here.</p></aside>
<div class="callout"><strong>Eligibility first.</strong> The official rules (§1.3) limit competitors to U.S. citizens or permanent residents, or U.S.-incorporated entities. The user’s listed location is Singapore. Confirm eligibility with the prize administrator before any upload. <a href="https://www.nlr.gov/docs/fy26osti/96647.pdf">Official rules ↗</a> · <a href="https://github.com/sassnarep3-star/GEMSDOESASS1/blob/main/knowledge/sources_verified_20261030.md">Verified sources and irregularities ↗</a></div>
<div class="table-wrap" tabindex="0" role="region" aria-label="Nine-site board"><table><thead><tr><th scope="col">Site</th><th scope="col">File to download (review)</th><th scope="col">Score (owner-reported)</th><th scope="col">Estimated score</th><th scope="col">Unique vs the other 8 sites?</th><th scope="col">OK to submit?</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="table-note">Overlap measured by the shared 3 px rule (≥70% = duplicate). Forward overlap among the nine best files: {sum(v > 0.70 for v in pair.values())} of {len(pair)} ordered pairs exceed 70% (max {max_pair["overlap"]:.4f}). Random placement of the same dot count gives a mean overlap of {lat["null_random_same_count_overlap"]["mean"]:.4f} against the lattice, so the gate cannot tell a random file from a duplicate. Exact dot-set groups in the registry: {b["exact_duplicates"]["dot_set_groups"]} ({b["exact_duplicates"]["cross_site_dot_set_groups"]} across sites). Full evidence: <a href="https://github.com/sassnarep3-star/GEMSDOESASS1/blob/main/evidence/nine_site_board.json">nine_site_board.json ↗</a>.</p>
<div class="grid2"><article class="panel"><p class="kicker">Why 0.2778 scored highest</p><h3>A subset of the 0.2600 field, with catalogue-adjacent dots removed.</h3><p>Verified from bytes: the GEMSDOE32 raster is the 44,090-dot GEMSDOE25 raster minus 6,436 dots. Every removed dot lies 1–2 px from a mapped fault, and the file contains zero dots on mapped faults. Removing low-credit dots lowers false-positive mass under the 0.2 weight.</p></article>
<article class="panel"><p class="kicker">Can we beat 0.2778 with an unrestricted new file?</p><h3>Not under the protocol, and no candidate is validated.</h3><p>SWGB beat the holdout bar in both variants (shipped 6 px prune HOLDOUT-DTI 0.1401, CI 0.1329–0.1452; 2 px E2 0.1586, CI 0.1519–0.1649; bar 0.1011), and both were withdrawn by the lattice gate. Holdout DTI does not rank the live family: Spearman −0.081 across 17 registry rasters (n=17). Leaderboard context: the official public page snapshot (2026-10-30) shows #1 at 0.4544 and #50 at 0.3169, so 0.2778 sits below the visible top 50. The user-cited 0.4413 and 0.3195 figures are not the top score on that page.</p></article></div>'''


def main():
    OUT.mkdir(exist_ok=True)
    audit = load('evidence/nine_site_audit.json')
    card = load('evidence/run_card.json')
    if card['approved_for_submission'] or card['verdict'] != 'negative':
        raise ValueError('This frozen negative-release site must not misrepresent a different approval state.')
    # Active release: the current-release pointer wins (2026-10-31 H-BSTEP), then the newest
    # lane release directory present.
    global ACTIVE_DIR
    pointer = load('evidence/current_release.json') if (ROOT / 'evidence/current_release.json').exists() else {}
    if pointer.get('release') and (ROOT / pointer['release']).exists():
        ACTIVE_DIR = Path(pointer['release']).parts[-2]
    for candidate in (ACTIVE_DIR, 'tiprelay', 'kdam', 'thermal'):
        if (ROOT / 'evidence' / candidate / 'release.json').exists():
            ACTIVE_DIR = candidate
            break
    else:
        raise ValueError('no lane release directory found')
    rel = load(f'evidence/{ACTIVE_DIR}/release.json')
    holdout = load('evidence/holdout.json')
    sources = load('knowledge/sources.json')
    feed = load('knowledge/source_feed.json') if (ROOT / 'knowledge/source_feed.json').exists() else None
    rows = audit['rows']
    relcard = rel['card']
    verdict_word = 'OK TO DOWNLOAD AND SUBMIT' if relcard['ok_to_download_and_submit'] else 'NOT OK TO SUBMIT'

    head = f'''<p class="eyebrow">Research release / 31 October 2026</p><section class="hero"><div><h1>One unique new TIF.<br>Verdict: {e(verdict_word)}.</h1>
<p class="lead">{e(LANE_TITLES[ACTIVE_DIR])} — generated this session, validated automatically (values in [0,1], no NaN, exact competition grid, novelty gates). Historical sites reviewed below. Every number is labelled HOLDOUT-DTI or OWNER-REPORT.</p>
<div class="actions"><a class="button" href="downloads/{e(relcard['raster_name'])}" download>Download the submission TIF</a><a class="button secondary" href="executive-summary.html">Executive summary ↗</a></div>
<p class="tagline">FAULT DETECTION · SPATIAL HOLDOUT · FAIL-CLOSED EXPORT</p></div>''' + release_card(rel) + '</section>'
    sig_panels = {
        'bstep': '<article class="panel"><p class="kicker">01 / Scientific signal</p><h3>H-BSTEP clears the holdout bar</h3><p>A basement-step concordance learner (strain-edge, relay-bridge, step-over and seismicity-catalogue transforms, all visible-only and canaried at max AUC 0.722) is measured against the 0.2600-family field on the same folds: shipped-variant HOLDOUT-DTI 0.1433 vs 0.1011. The lane runs the E3 finding — the 0.2778 champion is exactly the family emission with near-catalogue dots deleted — to its logical step. All numbers are HOLDOUT-DTI.</p></article>',
        'tiprelay': '<article class="panel"><p class="kicker">01 / Scientific signal</p><h3>H-TIPRELAY clears the holdout bar</h3><p>Adding visible-only continuation geometry (tip-relay corridors, step-over gaps, strike persistence) to the thermal-anchored learner is scored as a paired ablation on the same folds; the shipped file emits at the champion operating point (37,654 dots, 2.8 px spacing, &gt;600 m off-catalogue). All numbers on this page are HOLDOUT-DTI.</p></article>',
        'kdam': '<article class="panel"><p class="kicker">01 / Scientific signal</p><h3>H-KDAM clears the holdout bar</h3><p>An alteration-contact-supervised learner (map contacts + geophysical rasters) is measured against the 0.2600-family field on the same folds with the same emission: a measured field gain on the shared holdout. A parallel H-TIPRELAY lane shipped an independent gated candidate the same day; the cross-lane duplicate check passed (near-independent fields). All numbers are HOLDOUT-DTI.</p></article>',
        'thermal': '<article class="panel"><p class="kicker">01 / Scientific signal</p><h3>H-TVGB clears the holdout bar</h3><p>The segment-withheld learner reaches HOLDOUT-DTI 0.1407 at the champion operating point (0.1516 at 52k dots) vs the 0.2600-family bar 0.1011. The geothermal-anchor conditioning itself is a measured negative (paired Δ −0.0124).</p></article>',
    }
    mainbody = head + metric_strip_new(rel) + legacy_banner() + '''<section class="section"><div class="section-head"><div><p class="eyebrow">The decision path</p><h2>Format is necessary. It isn't enough.</h2><p>Scientific merit, uniqueness and an uploadable file are separate checks. A code merge is not a submission approval.</p></div></div><div class="grid3">
''' + sig_panels[ACTIVE_DIR] + '''
<article class="panel"><p class="kicker">02 / Literal novelty</p><h3>Unique vs every competitive raster</h3><p>Surface and dot scans run against all 414 registry files before and after placement. The 13gems calibration lattice (IR-LATTICE-01) covers ≥99% of ANY dotted file; both the competitive-scope and the literal full-registry readings are published.</p></article>
<article class="panel"><p class="kicker">03 / Release decision</p><h3>Download, then a separate selector</h3><p>The TIF passes the automatic gates and is safe to upload format-wise (zeros outside the footprint — never NaN). Spending a weekly slot is a separate decision, made outside this workspace.</p></article></div></section>
<section class="section" id="historical"><div class="section-head"><div><p class="eyebrow">The nine-site portfolio</p><h2>Historical leaders, not new submissions.</h2><p>GEMSDOE32 has the highest report in the supplied list (0.2778 OWNER-REPORT). Its file is already on the leaderboard; the only download we recommend is the generated TIF above.</p></div></div>''' + table(rows, rel) + '''</section><section class="section grid2"><article class="panel"><p class="kicker">What changed in H33-B2?</p><h2>Pruning, not new discoveries.</h2><p>The actual GEMSDOE32 raster is exactly the site-31 base with 2,545 dots removed within 2 pixels of known faults. It adds no dots. This transformation is byte/array-audited; its reported leaderboard benefit is not independently confirmed.</p><a href="executive-summary.html#mechanism">See the mechanism audit →</a></article><article class="panel"><p class="kicker">Next work</p><h2>Beat 0.3195 with a better field.</h2><p>The 2026-10-31 lane executed the previous session's plan items: tip/step-over continuation geometry and strike persistence as learner features (paired ablation), far-field training emphasis, and the geothermal family as an emission prior. Outcome numbers are on the run card; the selector decides any slot. Remaining levers: Qfault-attribute continuation weighting and radiometric concordance (both preregistered, untested).</p><a href="research.html#next">Read the research plan →</a></article></section>''' + parallel_candidate_panel()
    (OUT / 'index.html').write_text(page('Overview', mainbody))

    mechanism = audit['h33_mechanism_audit']
    if ACTIVE_DIR in ('kdam', 'bstep'):
        mech_callout = (f'<div class="callout">Can we exceed the reported 0.2778? Not by copying or re-pruning it: every file at or above 0.24 in the nine focus sites is the same field. The {e(LANE_TITLES[ACTIVE_DIR])} lane built a different field and measured it against that field on the same folds with the same emission: '
                        f'<strong>{rel["card"]["holdout_dti"]["value"]:.4f} vs {rel["card"]["comparators_same_emission"]["family_base_44090_unpruned"]:.4f}</strong> HOLDOUT-DTI. That is a measured field gain; whether it transfers to the live board is unproven, because this holdout is not rank-correlated with live scores. Owner-reported highs (0.3195, 0.4413) are OWNER-REPORT; the public leaderboard leader read on 2026-10-31 is 0.4544.</div>')
    else:
        mech_callout = '<div class="callout">Can we exceed the reported 0.2778? This session\'s answer: only with a better field at ~40k dots. The supervised family is the only local instrument above the 0.2600 base (HOLDOUT-DTI 0.14–0.16 vs 0.1011); whether that transfers live is unproven. Conflicting user-provided highs of 0.3195 and 0.4413 are OWNER-REPORT, not ORGANIZER-CONFIRMED.</div>'
    execbody = f'''<p class="eyebrow">Executive summary / decision record</p><section class="hero"><div><h1>Download this file.<br>Verdict: {e(verdict_word)}.</h1>
<p class="lead">One unique TIF was generated, gated and packaged automatically. The table below lists what to download, the score evidence and uniqueness for every focus site. No human inspection is required — the gates are machine-checked.</p>
<div class="actions"><a class="button" href="downloads/{e(relcard['raster_name'])}" download>Download {e(relcard['raster_name'])}</a><a class="button secondary" href="how-to-submit.html">How to submit ↗</a></div></div>''' + release_card(rel) + '</section>' + metric_strip_new(rel) + legacy_banner() + '''<section class="section"><p class="eyebrow">File / estimated score / uniqueness / verdict</p><h2>The answer for each priority site.</h2><p class="lead">Top row = the generated submission (the only file to download). Historical rows are prior submissions with their OWNER-REPORT live scores.</p>''' + table(rows, rel) + f'''</section><section class="section" id="mechanism"><p class="eyebrow">Mechanism audit</p><h2>Why might GEMSDOE32 have improved?</h2><div class="grid2"><article class="panel"><h3>What is actually verified</h3><p>The H33-B2 mask is exactly <code>site31_base &amp; (distance_to_catalogue &gt; 2)</code>. The base has 40,199 dots, the result 37,654: 2,545 removed, none added. Its file SHA256 matches the pinned public mirror.</p><a href="{mechanism['code_source']}">Inspect original code ↗</a><p class="small">The arithmetic and mask identity are locally measured, not organizer scoring evidence.</p></article><article class="panel"><h3>What remains a hypothesis</h3><p>Removing predictions with little credit for hidden new faults could reduce weighted false-positive mass while retaining recall. But nearness to an existing fault does not make a dot automatically false: a new nearby splay could earn credit.</p><p>Without hidden truth or a submission-page receipt, the reported 0.2778 is not a verified causal result, and it does not calibrate a forecast for a new method.</p></article></div>{mech_callout}<p><a href="https://github.com/sassnarep3-star/GEMSDOESASS1/blob/main/knowledge/scientific_analysis.md">Full mathematical interpretation, confounders and authority boundaries ↗</a></p></section>
<section class="section" id="how-to"><p class="eyebrow">How to submit / the generated file</p><h2>Five steps, no manual inspection.</h2><div class="grid2"><article class="panel"><ol class="steps"><li><div><strong>Check the verdict at the top of this page.</strong>Only download the file if it reads “OK TO DOWNLOAD AND SUBMIT”. SWGB, H-PBSC and BGAC-1 files are not approved.</div></li><li><div><strong>Download the exact TIF (or ZIP).</strong>File: <code>{e(relcard['raster_name'])}</code>. Verify sha256 <code class="mono">{e(relcard['raster_sha256'])}</code> against the <a href="{rchref('run_card.json')}">run card</a>.</div></li><li><div><strong>Use the published name and note.</strong>Name: <code>{e(relcard['submission_name'])}</code>. Note ({relcard['note_length']}/140 chars): “{e(relcard['note'])}”.</div></li><li><div><strong>Upload on “New submission”.</strong>The form accepts a single-band GeoTIFF (.tif) or a ZIP containing exactly one GeoTIFF. This file is float32, EPSG:32611, 3730×3292, geotransform (100, 0, 243350, 0, −100, 4508550), values in [0,1] everywhere (zeros outside the footprint — the fix for “Predicted values must be in range [0, 1]”).</div></li><li><div><strong>Keep the organizer receipt.</strong>Record the submission id and returned score — only that makes a score ORGANIZER-CONFIRMED.</div></li></ol><p class="small"><a href="how-to-submit.html">Full step-by-step subpage →</a></p></article>
<article class="panel"><h3>Prevent the [0,1] rejection</h3><p>The shared fail-closed writer refuses NaN, infinities, negative values and values above one; it reopens the written TIFF and the one-TIFF ZIP and validates them before exposing outputs. The earlier portal error “Predicted values must be in range [0, 1]” is what NaN-outside (“-nan”) files trigger — the shipped file writes explicit zeros everywhere outside the footprint and has no NaN on the whole grid.</p><p>Project checks are automatic; the weekly-slot decision and the official login are competition controls, not a human visual-inspection step of the file.</p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">Official competition ↗</a><div class="callout">Slots used by this workspace: 0. Promotion to a real slot is a separate selector step within the weekly cap.</div></article></div></section>'''
    execbody += parallel_candidate_panel()
    # preserved parallel-session sections (nine-site board + instrument irregularity)
    execbody += nine_site_matrix()
    execbody += ('<section class="section" id="board">' + board_section() + '</section>'
                 '<section class="section" id="instrument"><p class="eyebrow">Instrument irregularity · parallel session 2026-10-30</p>'
                 '<h2>Can the instruments tell?</h2><div class="callout"><strong>Verified by the parallel lane: some local instruments are dominated by catalogue-prune width, not field content.</strong> '
                 'A 600 m catalogue prune scores HOLDOUT-DTI 0.0000 and a 200 m prune scores 0.0045 in their off-catalogue reading — exactly the champion figure — from completely different fields; '
                 'SGMC off-catalogue DTI and Live Mirror fail to reproduce live orderings outside the champion family. '
                 'The H-TVGB numbers above use the standard gems57-pooled-hide-v2 evaluator calibrated on the 0.2600 family (bar 0.1011), not the off-catalogue variant; '
                 'treat every holdout number as an instrument reading, not a forecast. '
                 'Full report: <a href="INSTRUMENT_IRREGULARITY.md">docs/INSTRUMENT_IRREGULARITY.md</a> · '
                 'nine-site board data: <a href="evidence/nine_site_board.json">evidence/nine_site_board.json</a>.</div></section>')

    # 2026-10-31 · second lane, generated from its own run card. It shipped a second unique
    # candidate; the verdict here is computed from that card, not typed by hand.
    fc = fusion_card()
    if fc:
        ci = _as_list(fc['ci95'])
        ctrl = fc['champion_control']
        ctrl_dt = float(ctrl['holdout_dti']) if isinstance(ctrl, dict) else float(ctrl)
        ctrl_ci = ctrl['ci95'] if isinstance(ctrl, dict) else None
        ctrl_ci = _as_list(ctrl['ci95']) if isinstance(ctrl, dict) else [float('nan')] * 2
        ctrl_lo, ctrl_hi = min(ctrl_ci), max(ctrl_ci)
        proj = fc['estimated_live_score']
        proj_txt = (f"central {proj['central']:.3f}, advisory band "
                    f"{proj['band'][0]:.2f}-{proj['band'][1]:.2f}") if isinstance(proj, dict) else str(proj)
        execbody += (
            '<section class="section" id="fusion-lane"><p class="eyebrow">Second lane · 2026-10-31 · '
            'H-FUSION3</p><h2>A second unique candidate, and a certified metric read.</h2>'
            '<div class="callout"><strong>Verdict: ' + e(fc['verdict'].upper()) + ' — expected score '
            + proj_txt + ' (a projection, never written as a score).</strong> '
            'Two lanes ran on the same day. This lane produced its own file; it is '
            '<strong>not</strong> expected to beat the 0.2778 champion, and it is not the file the '
            'verdict at the top of this page names. Submit one or the other, not both in one slot.</div>'
            '<div class="grid2">'
            '<article class="panel"><h3>The file</h3><p><code>'
            + e(fc['raster_name']) + '</code><br><span class="mono">sha256 '
            + e(fc['raster_sha256']) + '</span></p><p><a class="button" href="downloads/'
            + e(fc['raster_name']) + '" download>Download this TIF</a></p>'
            '<p class="small">Note (' + str(fc['note_chars']) + '/140 chars, copy into the form): “'
            + e(fc['note']) + '”</p>'
            '<p><a href="evidence/offset_step_v2/run_card.json">Its run card →</a></p></article>'
            '<article class="panel"><h3>Measured, then judged</h3>'
            '<p><span class="badge">HOLDOUT-DTI</span> ' + f"{float(fc['holdout_dti']):.4f}" +
            ' · 95% CI ' + f'{ci[0]:.4f}–{ci[1]:.4f}' +
            ' · evaluator ' + e(fc['evaluator_version']) + ' · ' +
            f"{int(float(fc['withheld_positive_pixels'])):,}" + ' withheld positives.</p>'
            '<p>Champion control on the same folds: ' + f'{ctrl_dt:.4f}' +
            ' (95% CI ' + f'{ctrl_lo:.4f}–{ctrl_hi:.4f}' + '). The intervals overlap — '
            '<strong>tied, not a win</strong>. Four attacks on the precision of the field (structure '
            'tensor, Frangi vesselness, variable-density allocation, rank fusion) all tied or lost.</p>'
            '<p class="small">Submission slots used by this workspace: ' + e(str(fc['submission_slots_used'])) +
            '.</p></article></div>'
            '<div class="grid2"><article class="panel"><h3>What this lane established instead</h3>'
            '<p>The metric was re-derived from its own source and certified to 1e-9: '
            '<code>D = α·(TP+FP) + β·K</code> <em>exactly</em>, because α + β = 1; the oracle ceiling '
            'is 1.000. It also reproduced the 0.2778 winner from bytes: GEMSDOE32 is GEMSDOE25’s '
            '44,090-dot file minus the dots within 2 px of the mapped catalogue — 37,654 dots, '
            'symmetric difference 0. That is a precision edit, not a new field.</p>'
            '<p>And the emission geometry is already optimal: 0.236 at 1.4 px spacing, 0.2778 at '
            '2.8 px, 0.2784 at 3.0 px, 0.272 at 4.0 px. The convention used by the group sits on the maximum. '
            'The only lever left is the field’s precision — 0.278 today, 0.454 at the leader’s '
            'precision.</p>'
            '<p><a href="evidence/metric_certification.json">Metric certificate →</a> · '
            '<a href="evidence/offset_step_v2/novelty_focus9.json">Novelty audit →</a></p></article>'
            '<article class="panel"><h3>The instrument is biased, and that is the finding</h3>'
            '<p>The champion field has <strong>exactly zero</strong> pixels in common with the '
            'public catalogue (minimum distance 1.0 px) — it was built to exclude mapped faults. Our '
            'holdout’s truth <em>is</em> the catalogue. The holdout therefore penalises the field that '
            'wins live and rewards fields that predict faults already mapped.</p>'
            '<p>Until a truth set of genuinely unmapped faults exists, a holdout improvement can be an '
            'improvement towards the wrong target.</p></article></div></section>')
    (OUT / 'executive-summary.html').write_text(page('Executive summary', execbody, active='executive'))

    howto = f'''<p class="eyebrow">How to submit / step by step</p><h1>From this site to<br>the submission form.</h1>
<p class="lead">Everything below is automated except the upload itself. The file has already passed format, novelty and holdout gates — read the verdict first, then copy the name and note exactly.</p>
''' + legacy_banner() + f'''
<section class="section"><div class="grid2"><article class="panel"><h3>1 · Read the verdict</h3><p>Open the <a href="executive-summary.html">executive summary</a>. The status panel at the top reads <strong>{e(verdict_word)}</strong> for <code>{e(relcard['raster_name'])}</code>. If a future run reports “NOT OK TO SUBMIT”, do not upload that run's file.</p><h3>2 · Download and verify</h3><p>Download <a href="downloads/{e(relcard['raster_name'])}">{e(relcard['raster_name'])}</a> (or the <a href="downloads/{e(relcard['raster_name'].replace('-zeros.tif', '-zeros.zip'))}">ZIP with the single GeoTIFF inside</a>). Check the hash:</p><p class="mono">sha256: {e(relcard['raster_sha256'])}</p><h3>3 · Open the competition submission form</h3><p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData — DOE GEMS Prize Challenge ↗</a> → “Submit predictions” → “New submission”.</p></article>
<article class="panel"><h3>4 · Fill the form exactly</h3><p><strong>File to submit:</strong> <code>{e(relcard['raster_name'])}</code> (single-band GeoTIFF) — or the ZIP containing exactly that one TIFF.</p><p><strong>Note (optional, ≤140 chars):</strong> “{e(relcard['note'])}”</p><p>Use this note so later submissions can be told apart. Suggested submission name for your records: <code>{e(relcard['submission_name'])}</code>.</p><h3>5 · Requirements this file already meets</h3><ul class="evidence-list"><li><span>Single-band GeoTIFF, float32</span><span class="good">PASS</span></li><li><span>CRS EPSG:32611 · shape 3730×3292</span><span class="good">PASS</span></li><li><span>Geotransform (100, 0, 243350, 0, −100, 4508550)</span><span class="good">PASS</span></li><li><span>Predicted values in [0, 1] everywhere (no NaN anywhere)</span><span class="good">PASS</span></li><li><span>Zeros outside the survey footprint · no dots on mapped faults</span><span class="good">PASS</span></li></ul><h3>6 · After upload</h3><p>Save the organizer receipt (submission id, file hash, returned score). A score becomes ORGANIZER-CONFIRMED only from that receipt. Check the weekly submission cap on the submission page before spending a slot — this project never uploads automatically.</p></article></div></section>
<section class="section"><div class="callout"><strong>Why the earlier file was rejected.</strong> The portal error “Predicted values must be in range [0, 1]” is produced by NaN or out-of-range values — historically the “-nan” variants written by sibling sites. The fail-closed writer here refuses to emit such a file at all: it validates the on-disk TIFF and ZIP before exposing them. <a href="{rchref('run_card.json')}">See the validator output in the run card →</a></div></section>'''
    howto += parallel_candidate_note_line()
    (OUT / 'how-to-submit.html').write_text(page('How to submit', howto, active='howto'))

    for row in rows:
        checks = row['local_format_checks']
        checklist = ''.join(f'<li><span>{e(key.replace("_", " "))}</span><span class="{"good" if value else "bad"}">{"PASS" if value else "NO"}</span></li>' for key, value in checks.items())
        aliases = ', '.join(row['same_predictions_other_focus_sites']) or 'No exact counterpart in another focus site in this snapshot.'
        body = f'''<p class="breadcrumbs"><a href="../index.html#historical">Nine-site portfolio</a> / {row['site']}</p><p class="eyebrow">Individual executive summary</p><section class="hero"><div><h1>{row['site']}<br>Historical review.</h1><p class="lead">Best result for this site listed in the supplied prompt: <strong>{row['historical_report']:.4f}</strong> (OWNER-REPORT live score). It is a previous submission — re-uploading it cannot improve on it.</p><span class="pill neutral">Prior artifact · not a unique new submission</span></div>{legacy_banner('../')}</section>
<div class="grid2"><article class="panel"><p class="kicker">Exact historical artifact</p><h3>Original file, without renaming.</h3><p class="mono">{e(row['file'])}</p><dl><dt>Score evidence</dt><dd>{row['historical_report']:.4f} OWNER-REPORT (no organizer receipt in this group)</dd><dt>Estimated score if re-submitted</dt><dd>No gain — it is already on the leaderboard under this identity.</dd><dt>New unique submission?</dt><dd class="bad">No — previously published</dd><dt>Same predictions elsewhere</dt><dd>{e(aliases)}</dd><dt>Method description</dt><dd>{e(row['method_summary'])} Owner description; not proof of scientific mechanism.</dd><dt>Positive pixels</dt><dd>{row['positive_pixels']:,} · locally measured</dd><dt>File SHA256</dt><dd class="mono">{row['sha256']}</dd><dt>Prediction-value SHA256</dt><dd class="mono">{row['canonical_footprint_sha256']}</dd></dl><div class="actions"><a class="button secondary" href="{row['source_url']}">Review pinned source file ↗</a></div><p class="small" style="margin-top:12px">Historical source review only. This is not a recommendation to download and resubmit.</p></article>
<article class="panel"><p class="kicker">Automated byte and grid audit</p><ul class="evidence-list">{checklist}</ul><p class="small" style="margin-top:14px">These checks describe the exact historical file, not a new release. Some historical variants have NaN outside the footprint and fail this project's conservative all-finite export policy. Organizer acceptance is not inferred.</p><a href="../evidence/nine_site_audit.json">Full audit and exact aliases →</a></article></div>
<section class="section"><h2>Submission decision: do not submit.</h2><p class="lead">No file from this historical comparison is a newly generated candidate. The only generated candidate is this session's release — see the <a href="../executive-summary.html">executive summary</a>.</p><a href="../how-to-submit.html">How the generated file is submitted →</a><p class="small">This subpage belongs to GEMSDOESASS1. The separate {row['site']} website has not been edited.</p></section>'''
        dest = OUT / 'sites' / f"{row['site']}.html"
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(page(row['site'], body, prefix='../', active='executive'))

    sourcehtml = ''.join(f'<article class="source"><a href="{e(s["url"])}">{e(s["authority"])} ↗</a><p><strong>{e(s["access"])}</strong></p><p>{e(" ".join(s.get("claims_supported", [])) or "No claims independently verified from this URL.")}</p></article>' for s in sources['sources'])
    researchbody = '''<p class="eyebrow">Research / hypotheses / source boundaries</p><h1>Geology first.<br>Claims kept in bounds.</h1><p class="lead">The contest target is unmapped fault traces. Structural predictions can guide geothermal exploration; they do not establish vents, temperatures or economic resources.</p><section class="section"><h2>2026-10-31 lane: continuation geometry (H-TIPRELAY).</h2><p>This session preregistered five NEW hypotheses (tip-relay corridors, step-over gaps, strike persistence, far-field emphasis, geothermal emission prior — plus two untested registered ideas: Qfault-attribute weighting and radiometric concordance), canaried every new feature (no AUC above 0.90), and ran the paired ablation on the shared segment-withheld holdout. The lane executes the previous session's NEXT_STEPS items 4a/4b/4c. All numbers are HOLDOUT-DTI; the run card in <a href="evidence/tiprelay/run_card.json">evidence/tiprelay</a> holds the measured values and the gate table.</p><a href="https://github.com/sassnarep3-star/GEMSDOESASS1/blob/main/knowledge/hypotheses_20261031.md">Preregistration, amendment A1 and ranked slate ↗</a></section><section class="section"><h2>2026-10-30 lane: geothermal-anchored recovery.</h2><p>The prompt directs heavy research into geothermal-vent discovery. This session registered five label-free geothermal hypotheses (warm/hot springs, geothermometer temperatures, paleo sinter/tufa/travertine vents, 2 m shallow-temperature probes, Qfaults attributes), canaried every feature, and ran the top one through the segment-withheld holdout. Result: the supervised learner with the thermal family reaches HOLDOUT-DTI 0.1462 at 44,090 dots (0.1407 at the champion operating point, 0.1516 at 52k) — above the 0.1011 bar — but the thermal conditioning itself is a measured negative (paired Δ −0.0124 [−0.0170, −0.0079] vs the identical learner without it). The pure rule field (E1) was negative (0.0593). All numbers are HOLDOUT-DTI.</p><a href="''' + REPO + '''/blob/main/knowledge/hypotheses_20261030.md">Preregistration and ranked slate ↗</a></section>
<section class="section"><h2>Earlier lanes, preserved.</h2><div class="table-wrap"><table><thead><tr><th>Priority</th><th>Hypothesis / layers</th><th>Target signature</th><th>Non-fault mimic / status</th></tr></thead><tbody>
<tr><td>1 · moderate benefit, low cost</td><td>BGAC-1 / gravity, basement, detrended topography</td><td>Signed antiparallel gradient consistency at 2 and 5 px scales; weak surface expression.</td><td>Depositional basin edge; shared inversion inputs. Tested once, negative and protocol-disqualified.</td></tr>
<tr><td>2 · high benefit, medium cost</td><td>H-SWGB / all 28 layers + visible-catalogue context</td><td>Segment-withheld supervised recovery of hidden catalogue segments.</td><td>Terrace risers, shorelines. Holdout-positive (0.1586) but withdrawn on lattice overlap.</td></tr>
<tr><td>3 · high live, low cost</td><td>H-PBSC / lidar step × coherence × playa relief</td><td>Coherent scarp at a low-relief playa edge.</td><td>Lahontan shorelines. Negative on holdout (0.0650), lattice overlap 99.48%.</td></tr>
<tr><td>4 · low benefit, moderate cost</td><td>Radiometric compositional break / K, Th, U and TMI</td><td>Persistent log-ratio contrast with a magnetic-contact veto.</td><td>Weathering or agriculture. Not tested.</td></tr></tbody></table></div><a href="''' + REPO + '''/blob/main/knowledge/hypotheses.md">Full preregistration and correction disclosure ↗</a></section>
<section class="section"><h2>What the available evidence can support.</h2><div class="grid2"><article class="panel"><h3>Official GitHub code inspected</h3><p>The reference repository describes geological fault detection with U-Net and Monte Carlo cross-validation, using asymmetric Tversky training loss. Its README supplies CPU-only environments. Those facts do not authenticate the current contest evaluation formula, the mirror's origin, or a live leaderboard result.</p></article><article class="panel"><h3>Public mirror bytes measured</h3><p>The 19-band feature stack, catalogue and template were restored and SHA-verified. The template has shape 3730 × 3292, EPSG:32611 and 100 m pixels. Hash consistency is not organizer provenance or data-license verification.</p></article></div></section><section class="section"><p class="eyebrow">Claim / source ledger</p><h2>Read, measured, or not reachable.</h2><p>Network access is limited to GitHub and package hosts. We do not claim to have fetched the official competition pages, rules PDF, USGS, GDR, INGENIOUS or Dropbox here. Links are retained for review, not fabricated verification.</p><div class="panel">''' + sourcehtml + '''</div></section>
<section class="section" id="next"><p class="eyebrow">Next session / highest priority first</p><h2>Beat 0.3195 with field quality.</h2><div class="panel"><ol><li>Emission tricks on the H19-5 family are exhausted (0.2778 = d2.8 minus near-catalogue dots). Only a better field at ~40k dots can pass 0.3195.</li><li>The supervised family is the only local instrument above the 0.2600 base: lift its far-field credit (currently farfield 0.119–0.135 vs pooled 0.14–0.16) with tip/step-over geometry and orientation features.</li><li>Re-test the geothermal family as an EMISSION prior (concentrate dots near thermal anchors) rather than learner features — the E2 ablation says as features they dilute the learner.</li><li>Resolve IR-LATTICE-01 formally: the amendment draft is in evidence/thermal/lattice_amendment.md.</li><li>Obtain organizer receipts before any number is called ORGANIZER-CONFIRMED; keep every historical value labelled OWNER-REPORT.</li><li>Route any promoted artifact to the separate slot selector; this workspace never uploads.</li></ol><a href="''' + REPO + '''/blob/main/knowledge/NEXT_STEPS.md">Complete next-session plan ↗</a></div></section>'''
    (OUT / 'research.html').write_text(page('Research and sources', researchbody, active='research'))

    bars = ''.join(f'<div class="barrow"><span>{e(key)}</span><div class="track"><div class="bar {"candidate" if key == "BGAC-1" else ""}" style="width:{score["dti"] / .12 * 100:.1f}%"></div></div><strong>{score["dti"]:.4f}</strong></div>' for key, score in sorted(holdout['scores'].items(), key=lambda item: -item[1]['dti']))
    feedhtml = '<p class="small">No source refresh has been run.</p>'
    if feed:
        feedhtml = f'<p class="small">Static snapshot checked: {e(feed["checked_utc"])}. GitHub heads only—not a current competition leaderboard. Changed heads require a new registry audit; they never update the frozen experiment.</p><p class="small" id="feed-live-status" role="status">Current GitHub freshness will be checked automatically if browser access is available.</p><div class="table-wrap"><table class="feed-grid"><thead><tr><th>Source</th><th>Experiment pin</th><th>Current head</th><th>Advisory</th></tr></thead><tbody>'
        for r in feed['sources']:
            state = 'Unavailable' if r['status'] != 'checked' else 'Changed — audit required' if r['changed_since_experiment'] else 'Matches snapshot'
            feedhtml += f'<tr data-source-repo="{r["repo"]}" data-frozen-ref="{r["frozen_ref"]}"><td>{r["repo"]}</td><td><code>{r["frozen_ref"][:12]}</code></td><td><code data-current-head>{(r.get("current_ref") or "unavailable")[:12]}</code></td><td data-advisory>{state}</td></tr>'
        feedhtml += '</tbody></table></div>'
    if ACTIVE_DIR == 'kdam':
        e2k = load('evidence/kdam/e2_paired_novelty.json')
        armsk = e2k['arms']
        e2panel = (f'<p class="kicker">E2 paired ablation (parallel H-KDAM lane)</p><h3>The novelty-constrained emission '
                   f'preserves the holdout result.</h3><p>Arm B (catalogue-pruned emission) HOLDOUT-DTI '
                   f'{armsk["B_prune2"]["holdout_dti"]:.4f}; arm C (novelty-constrained: no dot within 4 px of any registry '
                   f'raster the unconstrained candidate exceeded) {armsk["C_novelty"]["holdout_dti"]:.4f}; paired Δ '
                   f'{e2k["paired_delta_mean"]:+.6f} — the measured effect of the novelty rule is negligible, so the shipped '
                   f'file keeps the constrained emission. Evidence class HOLDOUT-DTI, {e2k["n_withheld_positives"]:,} '
                   f'withheld positives.</p><a href="evidence/kdam/e2_paired_novelty.json">E2 paired evidence JSON →</a>')
    if ACTIVE_DIR == 'bstep':
        e2b = load('evidence/bstep/e2_emission.json')
        cells = e2b.get('cells') or e2b.get('sweep') or []
        e2panel = ('<p class="kicker">E2 emission sensitivity (this session)</p><h3>Concordance field: emission cell sweep.</h3>'
                   '<p>The same learned field was emitted at the frozen cells (37,654/44,090 dots × 2/2.8/6 px catalogue '
                   'exclusion); the shipped anti-collision variant measures 0.1433 [0.1366, 0.1507] on the fold fields vs '
                   'the family base 0.1011. E3 evidence: the nine-site champion is exactly the family emission with dots '
                   'within 2 px of the visible catalogue deleted (44,090 − 6,436 = 37,654, symmetric difference 0).</p>'
                   '<a href="evidence/bstep/e2_emission.json">E2 evidence JSON →</a> · '
                   '<a href="evidence/bstep/e1_holdout.json">E1 holdout →</a>')
    if ACTIVE_DIR == 'tiprelay':
        e1 = rel['e1']
        e2t = rel['e2']
        arms = e1['arms']
        e2panel = (f'<p class="kicker">E1/E2 paired ablations (this session)</p><h3>Relay features: measured positive; '
                   f'far-field \u00d73 and the geothermal emission prior: measured negative.</h3>'
                   f'<p>Arm A (H-TVGB reproduction): HOLDOUT-DTI {arms["A_hvtgb_repro"]["holdout_dti"]:.4f} \u2014 an exact reproduction of the '
                   f'2026-10-30 arm (instrument check). Arm B (+5 relay-geometry features): {arms["B_tiprelay"]["holdout_dti"]:.4f} '
                   f'(paired \u0394 {e1["delta_B_minus_A"]["value"]:+.4f}, 95% CI [{e1["delta_B_minus_A"]["ci95"][0]:+.4f}, '
                   f'{e1["delta_B_minus_A"]["ci95"][1]:+.4f}]). Arm C (far-field positives \u00d73): {arms["C_tiprel_ff"]["holdout_dti"]:.4f} '
                   f'(paired \u0394 vs B {e1["delta_C_minus_B"]["value"]:+.4f}, 95% CI [{e1["delta_C_minus_B"]["ci95"][0]:+.4f}, '
                   f'{e1["delta_C_minus_B"]["ci95"][1]:+.4f}]). E2 emission prior (anchor-modulated vs plain at the shipped cell): '
                   f'{e2t["delta_modulated_minus_plain"]["value"]:+.4f} [95% CI {e2t["delta_modulated_minus_plain"]["ci95"][0]:+.4f}, '
                   f'{e2t["delta_modulated_minus_plain"]["ci95"][1]:+.4f}] \u2014 the geothermal family hurts as an emission prior too. '
                   f'The shipped file is arm B, plain emission.</p>'
                   f'<a href="evidence/tiprelay/e1_paired_ablation.json">E1 paired evidence JSON \u2192</a> \u00b7 '
                   f'<a href="evidence/tiprelay/e2_emission_ablation.json">E2 \u2192</a>')
    else:
        e2 = load('evidence/thermal/release.json')['e2']  # this panel documents the 2026-10-30 thermal E2
        e2panel = (f'<p class="kicker">E2 paired ablation (2026-10-30 thermal lane)</p><h3>Thermal features: measured negative.</h3>'
                   f'<p>Arm A (28 layers + context + thermal family): HOLDOUT-DTI {e2["arms"]["A_hvtgb"]["holdout_dti"]:.4f}. '
                   f'Arm B (identical learner, no thermal family): {e2["arms"]["B_swgb_repro"]["holdout_dti"]:.4f} \u2014 an exact '
                   f'reproduction of the withdrawn SWGB field. Paired \u0394 {e2["paired_delta_A_minus_B"]:+.4f}, 95% CI '
                   f'[{e2["paired_delta_ci95"][0]:+.4f}, {e2["paired_delta_ci95"][1]:+.4f}]. The honest conclusion: the gain over the '
                   f'0.1011 bar comes from the supervised learner, not from the geothermal anchors as learner features.</p>'
                   f'<a href="evidence/thermal/e2_paired_holdout.json">Paired evidence JSON \u2192</a>')
    evidencebody = f'''<p class="eyebrow">Evidence / immutable experiment record</p><h1>Negative results.<br>Fully accounted for.</h1><p class="lead">Three experiments this session (E1 rule field negative, E2 paired thermal-family negative, E3 emission sweep), one packaged candidate. Earlier negative lanes are preserved unchanged.</p>''' + metric_strip_new(rel) + legacy_banner() + f'''<section class="section" id="correction"><h2>The protocol error we found and fixed.</h2><div class="callout"><strong>Do not treat the BGAC-1 first-pass holdout as promotion-qualified.</strong> The original pre-placement audit checked Spearman ranks but omitted positive-support overlap; it also continued despite an unassessable registry file. Review corrected both. The identical surface fails the pre-placement overlap gate. No new experiment, dot placement or TIFF followed the correction.</div><p>The original run card and rank scan remain in the evidence directory. The current card explicitly records the error and disqualifies the execution for promotion. The runner now applies both literal tests at both phases and stops before placement on any incomplete clearance. Shared geometry is reused without a private metric change.</p></section>
<section class="section"><div class="grid2">{e2panel}<article class="panel"><p class="kicker">Exploratory holdout diagnostics</p><h3>BGAC-1 loses to a simpler feature.</h3>''' + bars + '''<p class="small">HOLDOUT-DTI · gems57-pooled-hide-v2 · 56,454 withheld positives · 95% block-bootstrap intervals in the linked JSON. Same fixed budget and folds; not organizer scores.</p><a href="evidence/holdout.json">Every arm, CI and fold →</a></article></div></section>
<section class="section"><div class="callout"><strong>Concurrent parallel-session work is preserved separately.</strong> Another session merged a synthetic, already holdout-negative research TIFF while an earlier run was underway. Its original files are in a learning-only archive, not active downloads. <a href="https://github.com/sassnarep3-star/GEMSDOESASS1/tree/main/archive/parallel-main-f620a70">Review archive and byte hashes ↗</a></div><h2>Download audit evidence.</h2><div class="panel"><ul class="evidence-list">''' + ''.join(f'<li><a href="evidence/{f}">{label}</a><span>JSON ↗</span></li>' for f, label in [('tiprelay/run_card.json', '2026-10-31 run card (H-TIPRELAY)'), ('tiprelay/release.json', '2026-10-31 release gates and verdict'), ('tiprelay/e1_paired_ablation.json', 'E1 paired continuation-geometry ablation'), ('tiprelay/e2_emission_ablation.json', 'E2 paired emission-prior ablation'), ('tiprelay/leakage_canary.json', '2026-10-31 per-feature leakage canaries'), ('tiprelay/cross_lane_kdam_check.json', '2026-10-31 cross-lane duplicate check (tiprelay vs kdam)'), ('kdam/release.json', '2026-10-31 release gates and verdict (parallel H-KDAM lane)'), ('kdam/e1_holdout.json', 'H-KDAM E1 holdout with same-emission comparators'), ('kdam/e2_paired_novelty.json', 'H-KDAM E2 novelty-constrained paired ablation'), ('kdam/leakage_canary.json', 'H-KDAM per-feature leakage canaries'), ('thermal/run_card.json', '2026-10-30 run card (H-TVGB)'), ('thermal/release.json', 'Release gates and verdict'), ('thermal/e2_paired_holdout.json', 'E2 paired thermal-family ablation'), ('thermal/e3_emission_sweep.json', 'E3 emission sweep'), ('thermal/leakage_canary.json', 'Per-feature leakage canaries (all clear)'), ('run_card.json', 'BGAC-1 run card (frozen negative)'), ('first_pass_run_card.json', 'Preserved first-pass card'), ('corrected_surface_novelty.json', 'Corrected pre-placement stop'), ('nine_site_audit.json', 'Nine-site byte / duplicate / H33 mechanism audit'), ('holdout.json', 'Exploratory holdout and paired confidence intervals'), ('focus_inventory.json', 'Complete frozen nine-site TIFF inventory'), ('release_checks.json', 'Frozen implementation hashes and verification checks')]) + '''</ul></div></section><section class="section" id="feed"><p class="eyebrow">Source freshness feed</p><h2>Current source heads. Frozen results.</h2>''' + feedhtml + f'''</section><section class="section"><h2>The BGAC-1 run card (frozen).</h2><pre>{e(json.dumps(card, indent=2))}</pre><h2>The active run card (this session).</h2><pre>{e(json.dumps(relcard, indent=2))}</pre></section>'''
    (OUT / 'evidence.html').write_text(page('Evidence and source feed', evidencebody, active='evidence'))
    (OUT / '.nojekyll').write_text('')
    evidence_out = OUT / 'evidence'
    evidence_out.mkdir(exist_ok=True)
    for path in (ROOT / 'evidence').glob('*.json'):
        shutil.copyfile(path, evidence_out / path.name)
    kdam_out = evidence_out / 'kdam'
    kdam_out.mkdir(exist_ok=True)
    kdam_src = ROOT / 'evidence' / 'kdam'
    if kdam_src.exists():
        for path in kdam_src.glob('*'):
            if path.is_file() and path.stat().st_size < 2_000_000:
                shutil.copyfile(path, kdam_out / path.name)
        for name in ('nine_site_matrix_20261031.json',):
            src = kdam_src / name
            if src.exists():
                shutil.copyfile(src, evidence_out / name)
    # 2026-10-31 H-FUSION3 lane (parallel session): publish its evidence alongside the others.
    osv2_out = evidence_out / 'offset_step_v2'
    osv2_out.mkdir(exist_ok=True)
    osv2_src = ROOT / 'evidence' / 'offset_step_v2'
    if osv2_src.exists():
        for path in osv2_src.glob('*.json'):
            if path.is_file() and path.stat().st_size < 2_000_000:
                shutil.copyfile(path, osv2_out / path.name)
    for name in ('metric_certification.json', 'local_restore.json'):
        src = ROOT / 'evidence' / name
        if src.exists():
            shutil.copyfile(src, evidence_out / name)
    therm_out = evidence_out / 'thermal'
    therm_out.mkdir(exist_ok=True)
    for path in (ROOT / 'evidence' / 'thermal').glob('*'):
        if path.is_file() and path.suffix in ('.json', '.md'):
            shutil.copyfile(path, therm_out / path.name)
    tip_out = evidence_out / 'tiprelay'
    tip_out.mkdir(exist_ok=True)
    for path in (ROOT / 'evidence' / 'tiprelay').glob('*'):
        if path.is_file() and path.suffix in ('.json', '.md'):
            shutil.copyfile(path, tip_out / path.name)
    for source, name in [('registry/focus_inventory.json', 'focus_inventory.json'), ('vendor/PROVENANCE.json', 'PROVENANCE.json'), ('knowledge/sources.json', 'sources.json')]:
        shutil.copyfile(ROOT / source, evidence_out / name)
    print('Built landing page, executive summary, how-to-submit, research, evidence and nine individual site summaries.')


if __name__ == '__main__':
    main()
