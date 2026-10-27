#!/usr/bin/env python3
"""Reuse the pinned shared cache builder; never treat mirror integrity as official provenance."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vendor.gems57.prepare_data import assemble_features, cache_bands, fetch_raw, sha256


def main():
    manifest = json.loads((ROOT / 'registry/upstream_data_manifest.json').read_text())
    receipts = []
    for item in manifest['files']:
        if item['group'] != 'core':
            continue
        target = ROOT / 'data/official' / item['dest']
        if item['id'] == 'training_features':
            if not target.exists() or sha256(target) != item['sha256']:
                assemble_features(ROOT)
        else:
            fetch_raw(item['repo'], item['path'], item['ref'], target, item['sha256'], item['bytes'])
        if sha256(target) != item['sha256'] or target.stat().st_size != item['bytes']:
            raise ValueError('data integrity failure: ' + item['id'])
        receipts.append(dict(id=item['id'], sha256=sha256(target), bytes=target.stat().st_size))
        print('verified', item['id'], flush=True)
    cache_receipt = ROOT / 'evidence/feature_cache.json'
    cache_hit = False
    if cache_receipt.exists():
        cached = json.loads(cache_receipt.read_text())
        cache_hit = (cached['source_sha256'] == sha256(ROOT / 'data/official/training_features.tif')
            and len(cached['bands']) == 19
            and all((ROOT / b['cache_file']).is_file()
                and sha256(ROOT / b['cache_file']) == b['sha256'] for b in cached['bands']))
    if not cache_hit:
        cache_bands(ROOT)
    print('cached feature stack reused' if cache_hit else 'shared builder populated the missing/invalid cache')
    (ROOT / 'evidence/data_receipt.json').write_text(json.dumps(dict(
        files=receipts, provenance='Integrity-verified owner mirror; NOT organizer-authenticated.',
        cache_reused=cache_hit, cache_builder='vendor/gems57/prepare_data.py'), indent=2) + '\n')


if __name__ == '__main__':
    main()
