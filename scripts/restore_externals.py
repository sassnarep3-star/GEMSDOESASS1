#!/usr/bin/env python3
"""Fetch the external u8 feature stacks + GDR point CSVs pinned in registry/upstream_data_manifest.json.

Everything comes from the owner GitHub mirrors (allowlisted host). Each byte range is verified
against the manifest sha256 and size. Provenance remains 'integrity-verified owner mirror;
NOT organizer-authenticated' (see manifest notes). Files land where src/gems/features.py and the
thermal lane expect them:
  data/features/<name>_u8.tif      (lidar_scarp_features_u8, geodawn_rad_u8, geodawn_extensions_u8)
  data/external/<name>             (GDR CSV/ZIP point data)
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'registry/upstream_data_manifest.json').read_text())

# dest -> final placement
PLACE = {
    'external/lidar_scarp_features_u8.tif': ROOT / 'data/features/lidar_scarp_features_u8.tif',
    'external/geodawn_rad_u8.tif': ROOT / 'data/features/geodawn_rad_u8.tif',
    'external/geodawn_extensions_u8.tif': ROOT / 'data/features/geodawn_extensions_u8.tif',
    'external/gdr_wellspring_in_footprint.csv': ROOT / 'data/external/gdr_wellspring_in_footprint.csv',
    'external/gdr_volcanic_vents_in_footprint.csv': ROOT / 'data/external/gdr_volcanic_vents_in_footprint.csv',
    'external/gdr_qfaults_traces.csv': ROOT / 'data/external/gdr_qfaults_traces.csv',
    'external/paleo_geothermal_regional.zip': ROOT / 'data/external/paleo_geothermal_regional.zip',
    'external/2m_temperature_probe_INGENIOUS_regional_data.zip': ROOT / 'data/external/2m_temperature_probe_INGENIOUS_regional_data.zip',
}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(item: dict, dest: Path) -> None:
    if dest.exists() and sha256(dest.read_bytes()) == item['sha256'] and dest.stat().st_size == item['bytes']:
        print('cached', dest.name, flush=True)
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ['gh', 'api', f"repos/{item['repo']}/contents/{item['path']}?ref={item['ref']}",
         '-H', 'Accept: application/vnd.github.raw'],
        capture_output=True, check=True, timeout=600)
    b = result.stdout
    if len(b) != item['bytes'] or sha256(b) != item['sha256']:
        raise ValueError(f"integrity failure for {item['id']}: bytes={len(b)} sha={sha256(b)[:16]}")
    tmp = dest.with_suffix(dest.suffix + '.partial')
    tmp.write_bytes(b)
    tmp.replace(dest)
    print('verified', item['id'], dest, flush=True)


def main() -> int:
    wanted = {k.split('/')[-1] for k in PLACE}
    n = 0
    for item in MANIFEST['files']:
        dest = PLACE.get(item.get('dest', ''))
        if dest is None:
            continue
        fetch(item, dest)
        n += 1
    print(f'done: {n} files')
    return 0 if n == len(PLACE) else 1


if __name__ == '__main__':
    sys.exit(main())
