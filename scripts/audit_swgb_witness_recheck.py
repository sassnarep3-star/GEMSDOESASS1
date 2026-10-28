#!/usr/bin/env python3
"""Recheck the historical SWGB TIFF against the frozen lattice witness.

Download the pinned witness from the GitHub contents API before invoking this
script. A single duplicate is sufficient to stop; this is not a full scan.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import rasterio
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vendor.gems57.uniqueness import dot_overlap

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / 'swgb/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif'
WITNESS_SHA = 'b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2'
CANDIDATE_SHA = 'f98c20df5bc67a482de6debd4abef9d3d104498bda0aacf464d693e271287729'
WITNESS_URL = 'https://github.com/buffedlizard55-lab/GEMSDOE24/blob/cf093c8c5e9fa77294ecf4c59b79cdade92cbc06/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(witness):
    if digest(witness) != WITNESS_SHA or digest(CANDIDATE) != CANDIDATE_SHA:
        raise ValueError('input hash mismatch')
    with rasterio.open(CANDIDATE) as c, rasterio.open(witness) as w:
        if c.count != 1 or w.count != 1 or (c.shape, c.crs, c.transform) != (w.shape, w.crs, w.transform):
            raise ValueError('witness and candidate grids do not match')
        x, y = c.read(1), w.read(1)
        if not np.isfinite(x).all() or not ((x >= 0) & (x <= 1)).all():
            raise ValueError('candidate contains nonfinite or out-of-range values')
        dots = int((x > 0).sum())
        if not dots:
            raise ValueError('candidate has no dots')
        overlap = dot_overlap(x, y, radius_px=3)
    return {'candidate_sha256': CANDIDATE_SHA, 'witness_sha256': WITNESS_SHA,
            'witness_url': WITNESS_URL, 'candidate_dots': dots,
            'directed_overlap_within_3px': overlap, 'duplicate': overlap > 0.70,
            'scope': 'One frozen registry witness; not a complete registry scan.',
            'surface_gate': 'not established by this audit',
            'format_check': 'candidate all-finite and in [0,1]; grid matches witness, not organizer-authenticated template',
            'verdict': 'negative' if overlap > 0.70 else 'incomplete',
            'approved_for_submission': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('witness', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.witness), indent=2))
