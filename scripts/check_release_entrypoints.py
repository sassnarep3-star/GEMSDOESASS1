#!/usr/bin/env python3
"""Fail closed if a deployed entry point revives the historical SWGB promotion."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    pages = [ROOT / 'index.html', *(ROOT / 'swgb').glob('*.html')]
    before = {p: p.read_bytes() for p in pages}
    subprocess.run([sys.executable, str(ROOT / 'scripts/swgb_build_site.py')],
                   capture_output=True, text=True, timeout=10, check=True)
    for page in pages:
        text = page.read_text().lower()
        if 'not approved' not in text or 'ok to download and submit' in text or '.tif"' in text:
            raise ValueError(f'unsafe or missing release status: {page}')
        if page.read_bytes() != before[page]:
            raise ValueError(f'generated entry point is stale: {page}')
    print(f'PASS: {len(pages)} entry points blocked and SWGB pages reproducible')


if __name__ == '__main__':
    main()
