#!/usr/bin/env python3
"""Validate GeoTIFFs against the OFFICIAL GEMS submission-format text (no inference, no repair).

Official text (DrivenData page 967, "Submission format"; NLR rules §3.2):
  * same projected CRS as training data: EPSG:32611
  * same resolution (100 m) and bounds as training data
  * data outside the bounds is null or NaN
  * a single layer, datatype float32, values between 0 and 1

This checker reports every violation it can see; it never clips or fills. A pass here is a format
check only. It is NOT uniqueness clearance, NOT scoring, and NOT portal acceptance.
Usage: python scripts/validate_format.py <tif> [<tif> ...] [--out evidence/x.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]


def check(path: Path, footprint: np.ndarray, grid) -> dict:
    problems = []
    with rasterio.open(path) as s:
        if s.count != 1:
            problems.append(f'band count {s.count} != 1')
        if s.dtypes[0] != 'float32':
            problems.append(f'dtype {s.dtypes[0]} != float32')
        if s.crs is None or s.crs.to_epsg() != 32611:
            problems.append(f'CRS {s.crs} != EPSG:32611')
        if (s.shape, s.transform) != (grid[0], grid[2]):
            problems.append('shape/transform differs from competition grid')
        a = s.read(1).astype(np.float64)
        nodata = s.nodata
    finite = np.isfinite(a)
    inside_nan = int(np.isnan(a[footprint]).sum())
    if inside_nan:
        problems.append(f'{inside_nan} NaN inside the footprint')
    outside_vals = a[~footprint & finite]
    if outside_vals.size and (outside_vals != 0).any():
        problems.append('nonzero finite values outside the footprint')
    vals = a[finite]
    if vals.size and (vals.min() < 0 or vals.max() > 1):
        problems.append(f'values outside [0,1]: min {vals.min()} max {vals.max()}')
    if not vals.size:
        problems.append('no finite values')
    nan_outside = int(np.isnan(a[~footprint]).sum())
    return dict(file=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                nodata=(None if nodata is None or not np.isfinite(nodata) else float(nodata)),
                nan_outside_footprint=nan_outside,
                values_min=float(vals.min()) if vals.size else None,
                values_max=float(vals.max()) if vals.size else None,
                problems=problems, pass_format_check=not problems)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--out')
    args = ap.parse_args()
    with rasterio.open(ROOT / 'data/bridge/sample_submission.tif') as s:
        grid = (s.shape, s.crs, s.transform)
        footprint = np.isfinite(s.read(1))
    results = [check(Path(f), footprint, grid) for f in args.files]
    out = dict(standard='DrivenData GEMS submission format (page 967) + NLR rules §3.2',
               footprint_cells=int(footprint.sum()), results=results)
    text = json.dumps(out, indent=2, allow_nan=False) + '\n'  # NaN/inf are already mapped to null above
    if args.out:
        Path(args.out).write_text(text)
    print(text)


if __name__ == '__main__':
    main()
