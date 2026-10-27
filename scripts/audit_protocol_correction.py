#!/usr/bin/env python3
"""Second-pass audit only: recompute frozen surface support, not dots or experiments.

Preserves the first-pass card and declares its holdout exploratory. The runner is
fixed to apply both literal tests before placement and to stop on incomplete scans.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
import numpy as np
import rasterio
from bgac import build
from novelty import audit


def main():
    original_path = ROOT / 'evidence/first_pass_run_card.json'
    if original_path.exists():
        raise SystemExit('Correction already frozen; verify it, do not overwrite.')
    card_path = ROOT / 'evidence/run_card.json'
    original_text = card_path.read_text()
    card = json.loads(original_text)
    with rasterio.open(ROOT / 'data/official/sample_submission.tif') as src:
        footprint = np.isfinite(src.read(1))
    features, _ = build(ROOT, footprint)
    inventory = json.loads((ROOT / 'registry/focus_inventory.json').read_text())
    receipt = audit(features['BGAC-1'], footprint, inventory, ROOT,
                    ROOT / 'data/official/sample_submission.tif', stage='surface')
    if receipt['candidate_values_sha256'] != card['canonical_surface_sha256']:
        raise AssertionError('Corrective audit must use the identical frozen surface')
    if not receipt['duplicate']:
        raise AssertionError('Expected literal pre-placement overlap blocker was not reproduced')
    (ROOT / 'evidence/corrected_surface_novelty.json').write_text(json.dumps(receipt, indent=2, allow_nan=False) + '\n')
    original_path.write_text(original_text)
    card.update(protocol_correction='Pass 2 found that first-pass surface audit tested rank only and continued despite an unassessable prior. Both are now fixed; holdout retained only as exploratory negative evidence, NOT protocol-qualified promotion evidence.',
        holdout_status='EXPLORATORY HOLDOUT-DTI; protocol execution disqualified before placement',
        stop_reason='Corrected literal surface overlap exceeds 70%; stop before placement. No additional dot placement or experiment during correction.',
        first_pass_record='first_pass_run_card.json', surface_audit='corrected_surface_novelty.json',
        validator_output=dict(file_status='NOT WRITTEN: duplicate gate',
            in_memory_surface_all_finite=bool(np.isfinite(features['BGAC-1']).all()),
            in_memory_surface_range_0_1=bool(((features['BGAC-1'] >= 0) & (features['BGAC-1'] <= 1)).all()),
            reference_grid_only=dict(shape=[3730, 3292], crs='EPSG:32611', transform=[100,0,243350,0,-100,4508550]),
            on_disk_submission_validation=None),
        planned_submission_name='gems-sass1-bgac1-20261027-d510a8033961',
        verdict='negative', approved_for_submission=False)
    card['correlation_overlap_vs_registry']['surface_overlap'] = receipt['max_directed_overlap_within_3px']
    card['correlation_overlap_vs_registry']['surface_corrected_scan_max_spearman'] = receipt['max_spearman']
    card['correlation_overlap_vs_registry']['scope_note'] = 'First-pass full rank scan retained; corrected surface and dot overlap scans stop at first violation, not full-registry maxima.'
    card_path.write_text(json.dumps(card, indent=2, allow_nan=False) + '\n')
    print('Frozen surface identical. Pre-placement literal duplicate reproduced; first-pass protocol error disclosed.')


if __name__ == '__main__':
    main()
