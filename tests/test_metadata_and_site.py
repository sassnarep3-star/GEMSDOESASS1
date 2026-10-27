import json
from pathlib import Path
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest
import refresh_sources

from fetch_audit_inputs import destination, validate_unique_destinations
from refresh_sources import build_feed
from render_portfolio import render_rows

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads((ROOT / path).read_text())


def test_fetch_destinations_unique_and_cannot_escape(tmp_path):
    focus = read_json("registry/focus_sources.json")
    claims = read_json("registry/claimed_candidates.json")
    entries = focus["sources"] + focus["auxiliary"] + claims["entries"]
    validate_unique_destinations(entries, tmp_path)
    # The historical and later candidate share a site but not a local filename.
    historic = next(e for e in entries if e.get("site") == "GEMSDOE36" and "id" not in e)
    newer = next(e for e in entries if e.get("id") == "GEMSDOE36_kpl36")
    assert destination(historic, tmp_path) != destination(newer, tmp_path)
    with pytest.raises(ValueError, match="Duplicate local destination"):
        validate_unique_destinations([historic, historic], tmp_path)
    with pytest.raises(ValueError, match="Unsafe local identifier"):
        destination({"id": "../escape"}, tmp_path)


def test_source_feed_is_explicit_on_changes_and_failure():
    baseline = {
        "checked_utc": "2026-10-27T00:00:00+00:00",
        "refs": {
            "same": {"repo": "org/same", "ref": "a" * 40},
            "changed": {"repo": "org/changed", "ref": "a" * 40},
            "broken": {"repo": "org/broken", "ref": "a" * 40},
            "bad-sha": {"repo": "org/bad", "ref": "a" * 40},
        },
    }
    def fetch(repo):
        if repo.endswith("broken"):
            raise OSError("no network")
        return {"org/same": "a" * 40, "org/changed": "b" * 40, "org/bad": "not-a-sha"}[repo]
    feed = build_feed(baseline, fetch=fetch)
    assert feed["status"] == "partial"
    by_site = {row["site"]: row for row in feed["sites"]}
    assert by_site["same"]["status"] == "unchanged"
    assert by_site["changed"]["status"] == "changed"
    assert by_site["broken"]["status"] == by_site["bad-sha"]["status"] == "unavailable"
    assert by_site["broken"]["current_ref"] is None
    assert "not a score" in feed["scope"]


def test_feed_cli_can_fail_on_partial_and_still_write_result(tmp_path, monkeypatch):
    import sys
    baseline = tmp_path / 'baseline.json'
    baseline.write_text('{}')
    feed = {'status': 'partial', 'sites': [{'status': 'unavailable'}]}
    monkeypatch.setattr(refresh_sources, 'HEADS', baseline)
    monkeypatch.setattr(refresh_sources, 'build_feed', lambda _: feed)
    out = tmp_path / 'feed.json'
    monkeypatch.setattr(sys, 'argv', ['refresh_sources.py', '--require-complete', '--out', str(out)])
    assert refresh_sources.main() == 1
    assert json.loads(out.read_text()) == feed


def test_historical_table_is_generated_and_bound_to_pins():
    manifest = read_json("registry/focus_sources.json")
    audit = read_json("evidence/focus_audit.json")
    html = (ROOT / "docs/index.html").read_text()
    expected = render_rows(manifest, audit)
    between = html.split("<!-- PORTFOLIO_START -->")[1].split("<!-- PORTFOLIO_END -->")[0].strip()
    assert expected == between
    assert len(re.findall(r"<tr>", expected)) == 9
    assert "USER-REPORTED" in expected and "do not submit" in expected
    audit["site_summary"]["GEMSDOE32"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="Unbound audit"):
        render_rows(manifest, audit)


def test_published_data_copies_are_not_stale():
    for path in ["focus_audit.json", "claimed_candidates_audit.json", "input_recovery.json", "champion_technical_audit.json"]:
        assert (ROOT / "docs/data" / path).read_bytes() == (ROOT / "evidence" / path).read_bytes()
    for path in ["focus_sources.json", "claimed_candidates.json"]:
        assert (ROOT / "docs/data" / path).read_bytes() == (ROOT / "registry" / path).read_bytes()


def test_negative_run_card_has_no_fabricated_submission():
    card = read_json("docs/data/run-card.json")
    assert card["verdict"] == "negative"
    assert card["experiments_run"] == card["competition_slots_used"] == 0
    assert card["holdout_dti"]["value"] is None
    assert card["raster_sha256"] is None and card["submission_name"] is None
    assert card["validator_output"]["status"] == "not_run_no_candidate"
    assert not card["ok_to_submit"] and not card["ok_to_download_submission"]
    assert len(card["note"]) <= 140


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"duplicate id {attrs['id']}"
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])


def test_internal_links_and_fragments_resolve():
    docs = ROOT / "docs"
    pages = {}
    for html in docs.glob("*.html"):
        parser = LinkParser()
        parser.feed(html.read_text())
        pages[html] = parser
    for page, parser in pages.items():
        for link in parser.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                continue
            target = (page.parent / parts.path).resolve() if parts.path else page
            assert target.is_file(), f"{page.name} links to missing {link}"
            if parts.fragment and target.suffix == ".html":
                assert target in pages and parts.fragment in pages[target].ids, f"{page.name} links to missing {link}"
