#!/usr/bin/env python3
"""Audit bytes, arrays, metadata and source-code mechanism of the nine reported bests.

Historical values are explicitly UNVERIFIED_REPORT, never ORGANIZER-CONFIRMED.
A different file hash is not enough: equality is checked on footprint predictions.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from novelty import canonical_hash

SPECS = [
    (24, 'gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif', .2477, 'Denser dotted H19-5 emission.'),
    (25, 'gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif', .2600, 'Sparser D2.8 dotted H19-5 emission.'),
    (27, 'gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif', .2449, 'Topographic gap-closure variant of D1.5.'),
    (28, 'gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif', .2710, 'Rung-3.0 re-spacing with catalogue-flank exclusion.'),
    (30, 'gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif', .2600, 'D2.8 reference repackaging; check normalized-array duplicates.'),
    (31, 'gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif', .2708, 'Catalogue-flank-pruned D2.8 reference.'),
    (32, 'gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif', .2778, 'Two-pixel known-catalogue-flank removal from the D2.8 R1 base.'),
    (33, 'GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif', .2632, 'Historical analog tip/stepover variant; method name is not independent scientific validation.'),
    (36, 'gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif', .2750, 'Historical Anderson-geothermal variant; filename is not proof of a trained PINN.'),
]


def main():
    inventory = json.loads((ROOT / 'registry/focus_inventory.json').read_text())
    sample = ROOT / 'data/official/sample_submission.tif'
    with rasterio.open(sample) as src:
        fp = np.isfinite(src.read(1))
        shape, crs, transform = src.shape, src.crs, src.transform
    with rasterio.open(ROOT / 'data/official/existing_faults.tif') as src:
        cat = src.read(1) == 1
    aliases = {}
    for r in inventory['rasters']:
        with rasterio.open(ROOT / r['local']) as src:
            if src.count != 1 or src.shape != shape or src.crs != crs or src.transform != transform:
                continue
            v = src.read(1)[fp]
            if not np.isfinite(v).all():
                continue
        aliases.setdefault(canonical_hash(v), []).append(dict(repo=r['repo'], ref=r['ref'], path=r['path'], sha256=r['sha256']))
    rows, masks = [], {}
    for n, name, reported, desc in SPECS:
        candidates = [r for r in inventory['rasters'] if r['repo'] == f'GEMSDOE{n}' and r['path'] == 'docs/downloads/' + name]
        if len(candidates) != 1:
            raise ValueError('missing/ambiguous historical artifact: ' + name)
        r = candidates[0]
        path = ROOT / r['local']
        if hashlib.sha256(path.read_bytes()).hexdigest() != r['sha256']:
            raise ValueError('cache hash drift')
        with rasterio.open(path) as src:
            a = src.read(1)
            checks = dict(single_band=src.count == 1, shape_match=src.shape == shape,
                crs_match=src.crs == crs, transform_match=src.transform == transform,
                no_nan_inside_footprint=bool(np.isfinite(a[fp]).all()),
                range_0_1_inside_footprint=bool(((a[fp] >= 0) & (a[fp] <= 1)).all()),
                all_finite_anywhere=bool(np.isfinite(a).all()))
            meta = dict(shape=list(src.shape), crs=str(src.crs), transform=list(src.transform)[:6],
                dtype=src.dtypes[0], bands=src.count, nan_outside_footprint=int(np.isnan(a[~fp]).sum()))
        digest = canonical_hash(a[fp])
        masks[n] = (a > 0) & fp
        rows.append(dict(site=f'GEMSDOE{n}', file=name, path=r['path'], ref=r['ref'], sha256=r['sha256'],
            evidence_class='UNVERIFIED_REPORT (excluded from validated score classes)', historical_report=reported,
            organizer_receipt=None, estimated_leaderboard_score=None,
            holdout_dti=None, method_summary=desc, method_summary_class='historical owner description, not validated causation',
            source_url=f"https://github.com/buffedlizard55-lab/GEMSDOE{n}/blob/{r['ref']}/{r['path']}",
            official_submission_url='https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/',
            canonical_footprint_sha256=digest, exact_prediction_aliases=aliases[digest],
            positive_pixels=int(masks[n].sum()), positive_on_known_catalogue=int((masks[n] & cat).sum()),
            local_format_checks=checks, metadata=meta, new_unique_submission=False,
            approved_for_submission=False, recommendation='Historical review only; do not resubmit as a new unique candidate.'))
    for row in rows:
        row['same_predictions_other_focus_sites'] = sorted(set(a['repo'] for a in row['exact_prediction_aliases'] if a['repo'] != row['site']))
    dcat = distance_transform_edt(~cat)
    expected = masks[31] & (dcat > 2)
    mechanism = dict(code_source='https://github.com/buffedlizard55-lab/GEMSDOE32/blob/1398109a23f04a2ace71c1bd2f527cfba87860b5/src/gems32/hypotheses33.py#L313-L331',
        exact_reproduction_from_site31_base=bool(np.array_equal(expected, masks[32])),
        base_dot_count=int(masks[31].sum()), output_dot_count=int(masks[32].sum()),
        removed_dot_count=int((masks[31] & ~masks[32]).sum()), added_dot_count=int((masks[32] & ~masks[31]).sum()),
        conclusion='Mask transformation verified from actual rasters. Score improvement causation remains unverified; known-fault proximity is not proof of false positives.')
    blocking_row = next(r for r in inventory['rasters'] if r['repo'] == 'GEMSDOE24' and r['path'] == 'inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif')
    with rasterio.open(ROOT / blocking_row['local']) as src:
        prior = (src.read(1) > 0) & fp
    distance = distance_transform_edt(~prior)
    obstruction = dict(registry_file=blocking_row, positive_support_pixels=int(prior.sum()),
        footprint_fraction_within_3px=float((distance[fp] <= 3).mean()),
        max_distance_in_footprint_px=float(distance[fp].max()),
        explanation='A regular 5px lattice can cover almost every possible candidate dot within 3px. Literal novelty gate can reject scientifically different surfaces; no exception was applied.')
    out = dict(generated_utc=datetime.now(timezone.utc).isoformat(),
        historical_score_warning='Values from the user prompt/owner ledgers, not organizer receipts. No leaderboard-score estimate is supported.',
        best_reported_site='GEMSDOE32', rows=rows, h33_mechanism_audit=mechanism, novelty_obstruction=obstruction)
    (ROOT / 'evidence/nine_site_audit.json').write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
    print(json.dumps(dict(h33_mechanism_audit=mechanism, novelty_obstruction={k:v for k,v in obstruction.items() if k!='registry_file'}), indent=2))


if __name__ == '__main__':
    main()
