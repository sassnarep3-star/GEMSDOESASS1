#!/usr/bin/env python3
"""Render the historical table from the checked audit, refusing mismatched pins."""
from __future__ import annotations

from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START, END = "<!-- PORTFOLIO_START -->", "<!-- PORTFOLIO_END -->"


def render_rows(manifest: dict, audit: dict) -> str:
    rows = []
    for item in manifest["sources"]:
        site = item["site"]
        result = audit["site_summary"][site]
        if result["sha256"] != item["sha256"] or result["source"] != item["source"]:
            raise ValueError(f"Unbound audit entry: {site}")
        if result["user_reported_value"] != item["reported_value"]:
            raise ValueError(f"Reported value mismatch: {site}")
        site_url = "https://github.com/" + item["repo"]
        filename = item["path"].split("/")[-1]
        duplicate = result["duplicate_vs_any_other_of_nine"]
        label = "NO · duplicate" if duplicate else "Not established"
        pct = f"{result['worst_fraction_within_3px'] * 100:.2f}%"
        rows.append(
            f'<tr><td><a class="site-name" href="{escape(site_url, quote=True)}">{escape(site)}</a>'
            f'<a class="file" href="{escape(item["source"], quote=True)}">{escape(filename)} ↗</a></td>'
            f'<td><span class="score">{escape(item["reported_value"])}</span><span class="sub">USER-REPORTED · unverified</span></td>'
            f'<td><span class="badge">{label}</span><span class="sub">{pct} vs {escape(result["worst_reference"])}</span></td>'
            '<td><strong>Not estimable</strong><span class="sub">No new file · do not submit</span></td></tr>'
        )
    return "\n".join(rows)


def main() -> None:
    manifest = json.loads((ROOT / "registry" / "focus_sources.json").read_text())
    audit = json.loads((ROOT / "evidence" / "focus_audit.json").read_text())
    page = ROOT / "docs" / "fieldnotes.html"
    text = page.read_text()
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("Expected one pair of portfolio markers")
    before, rest = text.split(START)
    _, after = rest.split(END)
    page.write_text(before + START + "\n" + render_rows(manifest, audit) + "\n" + END + after)
    for src, dst in [
        ("evidence/focus_audit.json", "docs/data/focus_audit.json"),
        ("evidence/claimed_candidates_audit.json", "docs/data/claimed_candidates_audit.json"),
        ("registry/focus_sources.json", "docs/data/focus_sources.json"),
        ("registry/claimed_candidates.json", "docs/data/claimed_candidates.json"),
        ("evidence/input_recovery.json", "docs/data/input_recovery.json"),
        ("evidence/champion_technical_audit.json", "docs/data/champion_technical_audit.json"),
        ("evidence/parallel_variant_audit.json", "docs/data/parallel_variant_audit.json"),
    ]:
        (ROOT / dst).write_bytes((ROOT / src).read_bytes())
    print(f"Rendered {len(manifest['sources'])} historical rows and synchronized evidence.")


if __name__ == "__main__":
    main()
