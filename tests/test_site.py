import json
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from render_site import render  # noqa: E402


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])


def parse(path):
    parser = Links()
    parser.feed(path.read_text(encoding='utf-8'))
    return parser


def test_all_local_site_links_and_anchor_targets_exist():
    for name in ('index.html', 'executive-summary.html', 'research.html', 'sources.html'):
        page = ROOT / name
        p = parse(page)
        assert len(p.ids) == len(set(p.ids)), f'Duplicate id in {name}'
        for link in p.links:
            url = urlparse(link)
            if url.scheme or url.netloc:
                continue
            target = page.parent / unquote(url.path) if url.path else page
            assert target.is_file(), f'{name}: broken {link}'
            if url.fragment and target.suffix == '.html':
                assert url.fragment in parse(target).ids, f'{name}: missing anchor {link}'


def test_index_is_current_render_and_is_fail_closed():
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    assert html == render(), 'Run scripts/render_site.py after changing the source ledger or audit'
    assert html.count('data-site="GEMSDOE') == 9
    assert html.count('>DO NOT SUBMIT</span>') == 9
    assert html.count('>Not estimable</span>') == 9
    assert 'Submission download unavailable' in html
    assert 'USER-REPORTED / UNVERIFIED' in html
    assert 'not our receipt' in html


def test_ledger_manifest_and_audit_are_byte_bound():
    ledger = json.loads((ROOT / 'data/site-summary.json').read_text())
    inputs = {x['id']: x for x in json.loads((ROOT / 'data/inputs.json').read_text())['inputs']}
    audit = json.loads((ROOT / 'evidence/witness-audit.json').read_text())
    for site in ledger['sites']:
        name = site['site']
        assert site['evidence_class'] == 'USER-REPORTED / UNVERIFIED'
        assert site['estimated_leaderboard_score'] is None
        assert site['decision'] == 'DO NOT SUBMIT'
        assert site['artifact_sha256'] == inputs[name]['sha256'] == audit['historical_witnesses'][name]['sha256']
        assert site['repository_head_at_review'] and len(site['repository_head_at_review']) == 40
    assert ledger['leaderboard_observation']['evidence_class'].startswith('PUBLIC LEADERBOARD')
    assert audit['kpl36']['sha256'] == inputs['KPL36']['sha256']


def test_run_card_does_not_convert_missing_evidence_to_a_pass():
    card = json.loads((ROOT / 'evidence/run-card.json').read_text())
    assert card['verdict'] == 'negative'
    assert card['experiment_budget']['experiments_run'] == 0
    assert card['experiment_budget']['weekly_slots_used'] == 0
    assert card['holdout']['holdout_dti'] is None
    assert card['holdout']['confidence_interval_95'] is None
    assert card['raster_sha256'] is None
    assert card['validator']['no_nan_inside_footprint'] is None
    assert card['submission']['okay_to_submit'] is False
    assert card['submission']['name'] is None and card['submission']['note'] is None
