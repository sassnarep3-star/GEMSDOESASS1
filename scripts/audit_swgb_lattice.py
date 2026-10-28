#!/usr/bin/env python3
"""Reproduce the frozen SWGB duplicate finding; never changes or releases a TIFF.

Obtain the pinned lattice via GitHub into data/review/lattice.tif, then run this
script. Its expected digest and grid are checked before calculating overlap.
"""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vendor.gems57.uniqueness import dot_overlap  # shared literal gate
CANDIDATE = ROOT / 'swgb/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif'
LATTICE = ROOT / 'data/review/lattice.tif'
EXPECTED = ('f98c20df5bc67a482de6debd4abef9d3d104498bda0aacf464d693e271287729',
            'b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def compare(candidate, prior):
    with rasterio.open(candidate) as a, rasterio.open(prior) as b:
        if a.count != 1 or b.count != 1 or (a.shape, a.crs, a.transform) != (b.shape, b.crs, b.transform):
            raise ValueError('single-band grid mismatch')
        x, y = a.read(1), b.read(1)
        if not np.isfinite(x).all() or (x < 0).any() or (x > 1).any():
            raise ValueError('candidate contains invalid values')
        # Lattice has NaN outside footprint, not positive predictions there.
        dots, prior_dots = x > 0, np.isfinite(y) & (y > 0)
        if not dots.any() or not prior_dots.any():
            raise ValueError('empty positive support')
        count = int(dots.sum())
        within = int((distance_transform_edt(~prior_dots)[dots] <= 3).sum())
        shared_overlap = dot_overlap(x, y)
        if not np.isclose(shared_overlap, within / count, rtol=0, atol=1e-15):
            raise ValueError('shared overlap disagrees with independent distance calculation')
        return {'candidate_dots': count, 'within_3_pixels': within,
                'directed_overlap': within / count, 'duplicate': within / count > 0.70,
                'candidate_finite_all': True, 'candidate_range': [float(x.min()), float(x.max())],
                'single_band_grid_match_to_lattice': True}


def main():
    hashes = (digest(CANDIDATE), digest(LATTICE))
    if hashes != EXPECTED:
        raise ValueError('input digest mismatch')
    result = compare(CANDIDATE, LATTICE)
    print(json.dumps(dict(candidate_sha256=hashes[0], lattice_sha256=hashes[1], **result), indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
