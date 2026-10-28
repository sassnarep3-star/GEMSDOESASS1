#!/usr/bin/env python3
"""Audit the existing SWGB artifact against a pinned, previously omitted focus-site raster.

Usage: python scripts/audit_swgb_lattice.py --lattice /path/to/pinned.tif
Retrieve blob 81c802618e6d46c6d62289d856ae74439439bbc6 from the
GEMSDOE24 pinned commit and verify its SHA256 before invoking this script.
No new prediction or competition upload is made.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / 'swgb/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif'
TEMPLATE = ROOT / 'data/bridge/sample_submission.tif'
LATTICE_SHA = 'b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2'
CANDIDATE_SHA = 'f98c20df5bc67a482de6debd4abef9d3d104498bda0aacf464d693e271287729'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(lattice, candidate=CANDIDATE, template=TEMPLATE):
    if sha(lattice) != LATTICE_SHA or sha(candidate) != CANDIDATE_SHA:
        raise ValueError('pinned lattice or candidate SHA256 mismatch')
    with rasterio.open(template) as src:
        footprint = np.isfinite(src.read(1))
        grid = (src.crs, src.shape, src.transform)
    with rasterio.open(candidate) as src:
        if (src.crs, src.shape, src.transform) != grid:
            raise ValueError('candidate grid differs from template')
        dots = (src.read(1) > 0) & footprint
    with rasterio.open(lattice) as src:
        if (src.crs, src.shape, src.transform) != grid:
            raise ValueError('lattice grid differs from template')
        prior = (src.read(1) > 0) & footprint
    if not dots.any() or not prior.any():
        raise ValueError('empty candidate or prior support')
    distances = distance_transform_edt(~prior)
    nearby = int(np.count_nonzero(distances[dots] <= 3.0))
    total = int(dots.sum())
    return dict(candidate_sha256=CANDIDATE_SHA, prior_sha256=LATTICE_SHA,
                prior='GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif',
                prior_positive_pixels=int(prior.sum()), candidate_dots=total,
                candidate_dots_within_3px=nearby, fraction_within_3px=nearby/total,
                threshold=0.70, duplicate=nearby/total > 0.70,
                approved_for_submission=False,
                conclusion='Negative: stop. Existing format-valid TIFF is NOT approved for submission.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lattice', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.lattice)
    print(json.dumps(result, indent=2))
    if not result['duplicate']:
        raise SystemExit('Unexpected non-duplicate: review before updating frozen evidence')
