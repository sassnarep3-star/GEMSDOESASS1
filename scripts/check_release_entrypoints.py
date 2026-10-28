#!/usr/bin/env python3
"""Fail closed if an entry point revives the historical SWGB promotion."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/swgb_build_site.py')],
                            capture_output=True, text=True, timeout=10)
    if result.returncode == 0 or 'partial novelty audit' not in result.stderr:
        raise ValueError('legacy SWGB generator must fail closed')
    pages = [ROOT / 'index.html', *(ROOT / 'swgb').glob('*.html')]
    for page in pages:
        text = page.read_text().lower()
        if 'not approved' not in text or 'ok to download and submit' in text:
            raise ValueError(f'unsafe or missing release status: {page}')
    print(f'PASS: legacy generator disabled and {len(pages)} entry points blocked')


if __name__ == '__main__':
    main()
