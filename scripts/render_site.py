#!/usr/bin/env python3
"""Render the static comparison table from the pinned audit and claims ledger."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def esc(value):
    return html.escape(str(value), quote=True)


def render() -> str:
    ledger = json.loads((ROOT / 'data/site-summary.json').read_text(encoding='utf-8'))
    audit = json.loads((ROOT / 'evidence/witness-audit.json').read_text(encoding='utf-8'))
    sites = ledger['sites']
    if len(sites) != 9 or len({s['site'] for s in sites}) != 9:
        raise ValueError('Expected nine distinct sites')
    if (audit['submission_ready'] is not False or not audit['historical_nine_pairwise']['all_72_fail_overlap']
            or not audit['parallel_research_artifact']['overlap_with_lattice']['duplicate']
            or not audit['kpl36']['overlap_with_lattice']['duplicate']):
        raise ValueError('Static negative decision no longer matches audit evidence')
    rows = []
    for site in sorted(sites, key=lambda x: float(x['reported_value']), reverse=True):
        name = site['site']
        comp = audit['historical_nine_pairwise']['by_site'][name]
        if not comp['fails_against_at_least_one'] or site['estimated_leaderboard_score'] is not None:
            raise ValueError(f'Unexpected decision or estimated score: {name}')
        reference = comp['closest_reference'].replace('GEMSDOE', 'G')
        pct = 100 * comp['max_overlap_fraction']
        number = name.replace('GEMSDOE', '')
        rows.append(f'''        <tr data-site="{esc(name)}" data-review-head="{esc(site['repository_head_at_review'])}">
          <td data-label="Site"><a class="site-name" href="{esc(site['site_url'])}">GEMSDOE<span class="site-number">{esc(number)}</span> ↗</a><span class="status-line" data-source-status>Snapshot only</span></td>
          <td data-label="Research file"><a class="file-name" href="{esc(site['download_url'])}">{esc(site['filename'])} ↗</a><span class="cell-sub">Research only · pinned owner mirror</span></td>
          <td data-label="Claimed result"><span class="reported">{esc(site['reported_value'])}</span><span class="cell-sub">USER-REPORTED / UNVERIFIED</span></td>
          <td data-label="Score estimate"><span class="muted-value">Not estimable</span></td>
          <td data-label="Unique vs peers?"><strong>Duplicate</strong><span class="cell-sub">{pct:.2f}% within 3 px vs {esc(reference)}</span></td>
          <td data-label="Decision"><span class="badge badge-blocked">DO NOT SUBMIT</span></td>
        </tr>''')
    template = (ROOT / 'templates/index.html').read_text(encoding='utf-8')
    replacement = {
        '{{SITE_ROWS}}': '\n'.join(rows),
        '{{BEST_CLAIM}}': max(sites, key=lambda s: float(s['reported_value']))['reported_value'],
        '{{LEADER_VALUE}}': ledger['leaderboard_observation']['value'],
        '{{KPL_PERCENT}}': f"{100 * audit['kpl36']['overlap_with_lattice']['fraction']:.2f}",
        '{{PARALLEL_PERCENT}}': f"{100 * audit['parallel_research_artifact']['overlap_with_lattice']['fraction']:.2f}",
    }
    for key, val in replacement.items():
        if template.count(key) != 1:
            raise ValueError(f'Expected exactly one occurrence of {key}')
        template = template.replace(key, val)
    if '{{' in template:
        raise ValueError('Unexpanded site template variable')
    return template


def main():
    (ROOT / 'index.html').write_text(render(), encoding='utf-8')
    print('Rendered index.html from the evidence and historical claims ledger.')


if __name__ == '__main__':
    main()
