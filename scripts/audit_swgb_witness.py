#!/usr/bin/env python3
"""Reproduce the SWGB duplicate witness; this cannot grant novelty clearance.

Retrieve the pinned Git blob with gh (see evidence/swgb-review.md) and pass its
path. The witness is enough to reject; it is not a complete registry scan.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import rasterio
from vendor.gems57.uniqueness import dot_overlap
from vendor.gems57.validate import sha256, validate

CANDIDATE = ROOT / 'swgb/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif'
TEMPLATE = ROOT / 'data/bridge/sample_submission.tif'
CATALOGUE = ROOT / 'data/bridge/existing_faults.tif'
PINS = {
    'candidate': 'f98c20df5bc67a482de6debd4abef9d3d104498bda0aacf464d693e271287729',
    'witness': 'b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2',
    'template': '2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc',
    'catalogue': '7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093',
}


def audit(witness):
    paths = {'candidate': CANDIDATE, 'witness': Path(witness), 'template': TEMPLATE, 'catalogue': CATALOGUE}
    for name, path in paths.items():
        if sha256(path) != PINS[name]:
            raise ValueError(f'{name} SHA256 does not match the frozen receipt')
    arrays = {}
    with rasterio.open(TEMPLATE) as reference:
        grid = (reference.count, reference.shape, reference.crs, reference.transform)
    for name, path in paths.items():
        with rasterio.open(path) as src:
            if (src.count, src.shape, src.crs, src.transform) != grid:
                raise ValueError(f'{name} grid or band count mismatch')
            arrays[name] = src.read(1)
    footprint = np.isfinite(arrays['template'])
    catalogue = arrays['catalogue'] == 1
    candidate = arrays['candidate']
    prior = arrays['witness']
    # Match the shared audit's footprint clipping and >0 support convention.
    overlap = dot_overlap(np.where(footprint, candidate, 0), np.where(footprint, prior, 0))
    receipt = validate(CANDIDATE, footprint=footprint, catalogue=catalogue)
    receipt['file'] = str(CANDIDATE.relative_to(ROOT))
    return {
        'scope': 'One pinned witness, not a complete registry scan; final dots only.',
        'witness_repo': 'buffedlizard55-lab/GEMSDOE24',
        'witness_ref': 'cf093c8c5e9fa77294ecf4c59b79cdade92cbc06',
        'witness_path': 'inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif',
        'witness_blob_sha1': '81c802618e6d46c6d62289d856ae74439439bbc6',
        'input_sha256': PINS,
        'shared_overlap_function': 'vendor.gems57.uniqueness.dot_overlap',
        'stage': 'final dots',
        'directed_overlap_within_3px': overlap,
        'overlap_limit': 0.70,
        'duplicate': bool(overlap > 0.70),
        'preplacement_surface_audit_broad_registry': 'not available; not cleared',
        'local_format_validation': receipt,
        'verdict': 'negative' if overlap > 0.70 else 'incomplete; not cleared',
        'approved_for_submission': False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('witness', type=Path)
    p.add_argument('--output', type=Path, help='write receipt JSON')
    args = p.parse_args()
    result = audit(args.witness)
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
