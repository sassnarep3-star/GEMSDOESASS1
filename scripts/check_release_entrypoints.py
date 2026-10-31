#!/usr/bin/env python3
"""Fail closed if a deployed entry point revives the historical SWGB promotion.

2026-10-30 scope update (documented): the root entry point may now present the *generated*
H-TVGB candidate and its machine verdict; the SWGB pages remain strictly revoked. 2026-10-31
update: the approved file is read from the ACTIVE lane release (evidence/tiprelay then
evidence/thermal). The checks below keep the original fail-closed intent (SWGB never revived,
no stray raw raster links) while allowing exactly the run-card-approved file to be linked from
the root page.
"""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    pages = [ROOT / 'index.html', *(ROOT / 'swgb').glob('*.html')]
    before = {p: p.read_bytes() for p in pages}
    subprocess.run([sys.executable, str(ROOT / 'scripts/swgb_build_site.py')],
                   capture_output=True, text=True, timeout=10, check=True)
    # Active release first (2026-10-31): the current-release pointer wins, then the newest
    # lane release directory.
    card = {}
    pointer_path = ROOT / 'evidence/current_release.json'
    if pointer_path.exists():
        ptr = json.loads(pointer_path.read_text())
        cp = ROOT / ptr['run_card']
        if cp.exists():
            card = json.loads(cp.read_text())
    for candidate in ('bstep', 'tiprelay', 'thermal'):
        if card:
            break
        cp = ROOT / 'evidence' / candidate / 'run_card.json'
        if cp.exists():
            card = json.loads(cp.read_text())
    approved_name = card.get('raster_name') if card.get('ok_to_download_and_submit') else None
    for page in pages:
        text = page.read_text()
        low = text.lower()
        is_swgb_page = page.parent.name == 'swgb'
        if 'not approved' not in low:
            raise ValueError(f'missing revocation status: {page}')
        if is_swgb_page:
            # SWGB pages: strictly revoked, never a download portal.
            if 'do not submit' not in low or 'downloads/' in text or 'ok to download and submit' in low:
                raise ValueError(f'unsafe or missing release status: {page}')
        else:
            # Root entry point: historical lanes stay 'DO NOT SUBMIT'; any approval phrase must
            # name exactly the run-card-approved raster; only docs/downloads links are allowed.
            if 'do not submit' not in low:
                raise ValueError(f'root page must keep the historical DO NOT SUBMIT banner: {page}')
            if 'ok to download and submit' in low:
                if not approved_name or approved_name not in text:
                    raise ValueError(f'approval phrase without the run-card-approved raster: {page}')
            for href in re.findall(r'href="([^"]+\.tif)"', text):
                if not href.startswith('docs/downloads/'):
                    raise ValueError(f'raw raster link outside docs/downloads: {page}: {href}')
                if approved_name is None or not href.endswith(approved_name):
                    raise ValueError(f'raster link is not the run-card-approved file: {page}: {href}')
        if page.read_bytes() != before[page]:
            raise ValueError(f'generated entry point is stale: {page}')
    print(f'PASS: {len(pages)} entry points checked; SWGB pages blocked; root verdict consistent with run card')


if __name__ == '__main__':
    main()
