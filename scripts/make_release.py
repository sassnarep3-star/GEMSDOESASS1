#!/usr/bin/env python3
"""Fail-closed release verifier for a generated submission.

Runs AFTER a lane's `final` step (default: the active 2026-10-31 H-TIPRELAY lane; pass the
evidence directory, e.g. `evidence/thermal`, to re-verify an older release). Re-validates the
on-disk TIFF (the run card holds the writer's receipt), re-checks the sha256 and the
exact-duplicate scan against the 414-raster registry and this repo's prior submission TIFFs,
folds the results into <evidence-dir>/run_card.json + release.json (same key layout that
scripts/build_site.py consumes), and exits 2 with reason strings if any gate blocks.

2026-10-31 template fix (reported per protocol item 2): the exact-duplicate scan joined the
inventory's `local` paths onto `registry/` instead of the repo root, so it silently scanned
zero registry files. Fixed to `ROOT / rec['local']` and now fails loudly when registry files
are absent rather than passing an empty scan.

Release gates (all must pass; the run card keeps the full table):
  1. format validator: single-band GeoTIFF, exact competition grid, values in [0,1], no NaN;
  2. not an exact duplicate of any registry raster or prior repo submission;
  3. lane-drift novelty gates on surface + final dots (per-raster thresholds,
     IR-LATTICE-01 readings reported both ways in the run card);
  4. HOLDOUT-DTI above the 0.2600-family bar (0.1011);
  5. zero positive mass on mapped catalogue faults;
  6. no weekly submission slot used by this workspace.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from gems.grid import CRS as GRID_CRS, SHAPE as GRID_SHAPE  # noqa: E402
from gems.submission import validate  # noqa: E402

BAR = {'holdout_dti': 0.1011}


def strict_json(path):
    def _c(o):
        if isinstance(o, dict):
            return {k: _c(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_c(v) for v in o]
        if isinstance(o, float) and (np.isnan(o) or np.isinf(o)):
            raise ValueError(f'non-finite number in {path}')
        return o
    return _c(json.loads(Path(path).read_text()))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence-dir', default='evidence/tiprelay',
                    help='lane evidence directory holding run_card.json + release.json')
    args = ap.parse_args()
    OUT = ROOT / args.evidence_dir
    card = strict_json(OUT / 'run_card.json')
    rel = strict_json(OUT / 'release.json')
    blockers = []
    tif = ROOT / 'docs' / 'downloads' / card['raster_name']
    if not tif.exists():
        print(f'BLOCKED: {card["raster_name"]} missing from docs/downloads')
        return 2
    sha = sha256_file(tif)
    if sha != card['raster_sha256']:
        print(f'BLOCKED: sha256 mismatch ({sha} vs card {card["raster_sha256"]})')
        return 2

    # 1. format validator, from the bytes on disk
    foot = np.isfinite(rasterio.open(ROOT / 'data/bridge/sample_submission.tif').read(1))
    cat = rasterio.open(ROOT / 'data/bridge/existing_faults.tif').read(1) == 1
    v = validate(tif, foot, cat)
    card['validator_output'] = v
    rel['validator'] = v
    if not v['all_checks_passed']:
        blockers.append('format validator failed: ' + repr({k: bool(x) for k, x in v['checks'].items()}))

    # 2. exact-duplicate scan vs registry raster set + repo prior submissions
    cand = np.nan_to_num(rasterio.open(tif).read(1), nan=0.0)
    with rasterio.open(tif) as ds:
        transform_ok = str(ds.crs) == GRID_CRS and (ds.height, ds.width) == tuple(GRID_SHAPE)
    if not transform_ok:
        blockers.append('competition grid mismatch')
    cand_sha = hashlib.sha256(np.ascontiguousarray(cand.astype(np.float32)).tobytes()).hexdigest()
    exact = []
    inv = strict_json(ROOT / 'registry/focus_inventory.json')
    missing_registry = 0
    for rec in inv['rasters']:
        p = ROOT / rec['local']
        if not p.exists():
            missing_registry += 1
            continue
        with rasterio.open(p) as ds:
            arr = np.nan_to_num(ds.read(1), nan=0.0).astype(np.float32)
        if hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest() == cand_sha:
            exact.append(str(p.relative_to(ROOT)))
    for pat in ('docs/downloads/*.tif', 'docs/downloads/**/*.tif', 'archive/**/*.tif'):
        for p in ROOT.glob(pat):
            if p == tif or not p.is_file():
                continue
            try:
                with rasterio.open(p) as ds:
                    arr = np.nan_to_num(ds.read(1), nan=0.0).astype(np.float32)
                if hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest() == cand_sha:
                    exact.append(str(p.relative_to(ROOT)))
            except Exception:
                continue
    if exact:
        blockers.append(f'exact prediction duplicate of {exact}')
    rel['exact_duplicate_scan'] = dict(scanned_registry=len(inv['rasters']),
                                       present_on_disk=len(inv['rasters']) - missing_registry,
                                       missing_from_disk=missing_registry, duplicates=exact)
    if missing_registry:
        blockers.append(f'registry incomplete on disk: {missing_registry} of {len(inv["rasters"])} rasters missing')

    # 3-6. novelty / holdout / catalogue-mass / slots gates from the run card
    comp = card['correlation_overlap_vs_registry']
    gates = [
        ('Validator: values in [0,1], no NaN anywhere, exact competition grid', bool(v['all_checks_passed'])),
        ('Not an exact duplicate of any registry raster or prior repo file', not exact),
        ('Lane-drift gate vs competitive registry (Spearman ≤ 0.90, 3 px overlap ≤ 70%)',
         not comp['lane_drift_duplicate']),
        (f"HOLDOUT-DTI beats the 0.2600-family bar (0.1011): {card['holdout_dti']['value']}",
         bool(card['holdout_dti']['value'] > BAR['holdout_dti'])),
        ('Zero positive mass on mapped catalogue faults',
         bool(v['checks'].get('zero_mass_on_known_catalogue_pixels', False))),
        ('No weekly submission slot used by this workspace', card['submission_slots_used'] == 0),
    ]
    if comp['lane_drift_duplicate']:
        blockers.append('lane-drift gate failed (see correlation_overlap_vs_registry in the run card)')
    if not card['holdout_dti']['value'] > BAR['holdout_dti']:
        blockers.append(f"HOLDOUT-DTI {card['holdout_dti']['value']} does not beat bar 0.1011")

    ok = not blockers
    card['ok_to_download_and_submit'] = bool(ok and all(g[1] for g in gates))
    rel['card'] = card
    rel['gates'] = gates
    rel['ok_to_download_and_submit'] = card['ok_to_download_and_submit']
    (OUT / 'run_card.json').write_text(json.dumps(card, indent=2, default=str))
    (OUT / 'release.json').write_text(json.dumps(rel, indent=2, default=str))
    if ok:
        print('RELEASE OK: every gate passed')
        print(json.dumps({'raster_name': card['raster_name'], 'raster_sha256': sha,
                          'ok_to_download_and_submit': card['ok_to_download_and_submit']}))
        return 0
    print('RELEASE BLOCKED:')
    for b in blockers:
        print(' -', b)
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
