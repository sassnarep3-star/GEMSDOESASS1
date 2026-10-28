#!/usr/bin/env python3
"""Recheck an existing SWGB artifact against one frozen registry witness.

This is a post-hoc negative audit, not a new experiment or a complete registry scan.
Fetch the pinned lattice via gh (or pass --lattice); verify its SHA256 before use.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import rasterio
from vendor.gems57.gates import format_report
from vendor.gems57.uniqueness import dot_overlap

REF = 'cf093c8c5e9fa77294ecf4c59b79cdade92cbc06'
REMOTE = 'inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif'
LATTICE_SHA = 'b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2'
CANDIDATE = ROOT / 'swgb/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif'
CANDIDATE_SHA = 'f98c20df5bc67a482de6debd4abef9d3d104498bda0aacf464d693e271287729'
TEMPLATE_SHA = '2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(candidate, lattice, template):
    for path, sha in ((candidate, CANDIDATE_SHA), (lattice, LATTICE_SHA), (template, TEMPLATE_SHA)):
        if digest(path) != sha:
            raise ValueError(f'Hash mismatch: {path}')
    with rasterio.open(candidate) as c, rasterio.open(lattice) as p, rasterio.open(template) as t:
        if c.count != 1 or p.count != 1 or t.count != 1 or c.shape != p.shape or c.shape != t.shape or c.crs != p.crs or c.crs != t.crs or c.transform != p.transform or c.transform != t.transform:
            raise ValueError('Misaligned grids or band count')
        pred, prior, fp = c.read(1), p.read(1), np.isfinite(t.read(1))
    if not np.isfinite(prior[fp]).all():
        raise ValueError('Lattice has invalid values inside footprint')
    support = (pred > 0) & fp
    if not support.any():
        raise ValueError('Empty candidate')
    overlap = dot_overlap(np.where(fp, pred, 0), np.where(fp, prior, 0), radius_px=3)
    fmt = format_report(candidate, template, footprint=fp)
    return {
        'audit_type': 'POST-HOC REGISTRY-MEASUREMENT, not a new experiment; single witness only',
        'candidate': candidate.name, 'candidate_sha256': digest(candidate),
        'template_sha256': digest(template), 'template_provenance': 'owner mirror, not organizer authenticated',
        'prior_url': f'https://github.com/buffedlizard55-lab/GEMSDOE24/blob/{REF}/{REMOTE}',
        'prior_sha256': digest(lattice), 'candidate_positive_pixels': int(support.sum()),
        'radius_pixels': 3, 'candidate_directed_overlap': overlap,
        'threshold': 0.70, 'duplicate': overlap > 0.70,
        'surface_check': 'not reconstructed; no pre-placement clearance established',
        'registry_scope': 'one pinned lattice witness; not a complete scan or global uniqueness proof',
        'format_check': {k: fmt[k] for k in ('bands', 'dtype', 'crs', 'width', 'height', 'transform', 'nan_pixels', 'infinity_pixels', 'min', 'max', 'mass_outside_footprint', 'problems', 'ok', 'validation_class')},
        'approved_for_submission': False, 'verdict': 'negative',
        'note': 'Duplicate against registry lattice; do not submit.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lattice', type=Path, default=ROOT / '.cache/review/lattice.tif')
    parser.add_argument('--output', type=Path, help='Optional path for JSON; refuses overwrite')
    args = parser.parse_args()
    if not args.lattice.exists():
        args.lattice.parent.mkdir(parents=True, exist_ok=True)
        raw = subprocess.check_output(['gh', 'api', f'repos/buffedlizard55-lab/GEMSDOE24/contents/{REMOTE}?ref={REF}', '-H', 'Accept: application/vnd.github.raw'], timeout=90)
        if hashlib.sha256(raw).hexdigest() != LATTICE_SHA:
            raise ValueError('Downloaded lattice hash mismatch')
        args.lattice.write_bytes(raw)
    result = audit(CANDIDATE, args.lattice, ROOT / 'data/bridge/sample_submission.tif')
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if args.output:
        with args.output.open('x') as f:
            f.write(text)
    print(text, end='')


if __name__ == '__main__':
    main()
