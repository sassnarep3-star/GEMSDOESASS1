#!/usr/bin/env python3
"""Run the ONE preregistered BGAC-1 experiment through the shared evaluator.

No score projections, no slot selector, no upload. Failures produce a negative card.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
import numpy as np
import rasterio
from sklearn.metrics import roc_auc_score
from vendor.gems57 import spatial
from vendor.gems57.evaluate_holdout import evaluate, pooled_summary, VERSION
from vendor.gems57.submission_writer import write_submission
from bgac import build, emit
from novelty import audit, canonical_hash


def save(path, obj):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def crop_for(region, pad=3):
    y, x = np.nonzero(region)
    h, w = region.shape
    return (slice(max(0, y.min()-pad), min(h, y.max()+pad+1)),
            slice(max(0, x.min()-pad), min(w, x.max()+pad+1)))


def main():
    start = time.monotonic()
    # Rerunning a registered experiment accidentally is prohibited.
    card_path = ROOT / 'evidence/run_card.json'
    if card_path.exists():
        raise SystemExit('Frozen run card already exists. Verify it; do not overwrite or optimize against this holdout.')
    sample = ROOT / 'data/official/sample_submission.tif'
    with rasterio.open(sample) as src:
        footprint = np.isfinite(src.read(1))
    with rasterio.open(ROOT / 'data/official/existing_faults.tif') as src:
        catalogue = (src.read(1) == 1) & footprint
    inventory = json.loads((ROOT / 'registry/focus_inventory.json').read_text())
    features, eligible = build(ROOT, footprint)
    surface = features['BGAC-1']
    print('surface built; eligible', int(eligible.sum()), flush=True)
    surface_receipt = audit(surface, footprint, inventory, ROOT, sample, stage='surface')
    save('evidence/surface_novelty.json', surface_receipt)
    base_card = dict(schema_version=1, generated_utc=datetime.now(timezone.utc).isoformat(),
        hypothesis='BGAC-1: buried basin-edge anti-gradient consistency',
        mechanism='Signed gravity/basement gradient opposition at 2 and 5 px scales with weak surface-expression weighting.',
        non_fault_mimic='A smooth depositional basin margin with low-density fill; gravity-derived basement inversion coupling.',
        experiments_run=1, experiment_budget=3, max_runtime_seconds=7200,
        evaluator_version=VERSION, holdout_dti=None, ci95=None, withheld_positive_pixels=None,
        correlation_overlap_vs_registry=dict(surface=surface_receipt['max_spearman'],
            surface_overlap=surface_receipt['max_directed_overlap_within_3px'], dots=None, overlap=None),
        raster_sha256=None, canonical_surface_sha256=surface_receipt['candidate_values_sha256'],
        validator_output={'status':'not written'}, submission_name=None, note='BGAC-1 signed basin-edge test; no leaderboard score or weekly-slot approval.',
        verdict='negative', approved_for_submission=False, submission_slots_used=0,
        data_provenance='SHA-verified public owner mirror; not organizer authenticated.',
        limitations=['No organizer submission-page receipt or weekly-cap verification.',
                     'Global novelty outside the nine focus repositories is unverified.',
                     'No compatible prior local holdout best existed in this empty repository.'])
    if not surface_receipt['cleared']:
        base_card['stop_reason'] = ('surface duplicate: protocol requires immediate stop before placement'
            if surface_receipt['duplicate'] else 'surface audit incomplete/unassessable: stop before placement')
        base_card['elapsed_seconds'] = time.monotonic()-start
        save('evidence/run_card.json', base_card)
        print(base_card['stop_reason'])
        return
    if time.monotonic()-start > 7200:
        raise TimeoutError('two-hour budget exhausted')
    # Pixel-exact whole-component hide/recover folds from the shared template.
    terms = {key: None for key in features}
    fold_reports, canaries = [], []
    rng = np.random.default_rng(20261027)
    for fold in spatial.folds(catalogue, eligible, buffer_px=80):
        sl = crop_for(fold['region'])
        region = fold['region'][sl]
        visible = fold['visible'][sl]
        truth = fold['truth'][sl]
        active = eligible[sl] & region & ~visible
        positives = np.flatnonzero(truth & active)
        negatives = np.flatnonzero(active & ~truth)
        pos = rng.choice(positives, size=min(15000, len(positives)), replace=False)
        neg = rng.choice(negatives, size=min(15000, len(negatives)), replace=False)
        ids = np.r_[pos, neg]
        target = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
        budget = round(.0073 * int(active.sum()))
        fold_report = dict(fold['receipt'], budget_dots=budget, arms={})
        fail_canary = False
        for key, field in features.items():
            values = field[sl].ravel()[ids]
            auc = float(roc_auc_score(target, values))
            leak = auc > .90 or auc < .10
            canaries.append(dict(feature=key, fold=fold['fold'], auc=auc, positives=len(pos),
                background=len(neg), fails=leak, background_is_unlabeled=True))
            fail_canary |= leak
        save('evidence/canaries.json', dict(evidence_class='LEAKAGE-CANARY, NOT A DTI SCORE', tests=canaries))
        if fail_canary:
            base_card.update(stop_reason='AUC canary veto; investigate leakage before trusting results', canary_pass=False)
            save('evidence/run_card.json', base_card)
            print(base_card['stop_reason'])
            return
        local_fold = {k: fold[k][sl] for k in ('region', 'visible', 'truth')}
        for key, field in features.items():
            dots = emit(field[sl], active, budget)
            result, block_terms = evaluate(dots.astype(np.float32), local_fold, eligible[sl],
                origin=(sl[0].start, sl[1].start), global_shape=footprint.shape)
            fold_report['arms'][key] = result
            terms[key] = block_terms if terms[key] is None else terms[key] + block_terms
        fold_reports.append(fold_report)
        print('fold', fold['fold'], 'completed', fold_report['arms']['BGAC-1']['dti'], flush=True)
        if time.monotonic()-start > 7200:
            raise TimeoutError('two-hour budget exhausted')
    summary = pooled_summary(terms, draws=1999, seed=20261027, candidate='BGAC-1')
    summary.update(folds=fold_reports, split='shared spatial.folds label-blind-quadrants-v2; whole components, 80px buffer',
                   eligible_pixels=int(eligible.sum()), unique_hidden_positives=int((catalogue & eligible).sum()),
                   interpretation='Catalogue hide/recover proxy only; no leaderboard score estimate or vent validation.')
    save('evidence/holdout.json', summary)
    score = summary['scores']['BGAC-1']
    base_card.update(holdout_dti=score['dti'], ci95=score['ci95'],
        withheld_positive_pixels=score['withheld_positive_pixels'], canary_pass=True,
        holdout_evidence_class='HOLDOUT-DTI', best_comparable_control=summary['best_comparable_control'])
    allowed = eligible & ~catalogue
    final = emit(surface, allowed, round(.0073 * int(allowed.sum())))
    # Dots are checked before invoking the shared fail-closed writer.
    final_receipt = audit(final.astype(np.float32), footprint, inventory, ROOT, sample, stage='dots')
    save('evidence/dot_novelty.json', final_receipt)
    base_card['correlation_overlap_vs_registry'].update(dots=final_receipt['max_spearman'], overlap=final_receipt['max_directed_overlap_within_3px'])
    base_card['canonical_dots_sha256'] = canonical_hash(final[footprint])
    base_card['final_dot_count'] = int(final.sum())
    if final_receipt['duplicate']:
        base_card['stop_reason'] = 'duplicate final dots: literal protocol stop; no TIFF packaged'
    elif not surface_receipt['cleared'] or not final_receipt['cleared']:
        base_card['stop_reason'] = 'registry comparisons incomplete or unassessable; no uniqueness clearance'
    else:
        name = 'gems-sass1-bgac1-20261027-' + base_card['canonical_dots_sha256'][:12]
        note = 'BGAC-1 signed gravity-basement anti-gradient, 2/5px; weak surface relief; holdout proxy only; no slot approval.'
        path = ROOT / 'docs/downloads' / (name + '.tif')
        receipt = write_submission(path, final.astype(np.float32), sample, footprint,
            catalogue=catalogue, name=name, note=note,
            metadata=dict(evidence='../../evidence/run_card.json', approved_for_submission=False))
        base_card.update(submission_name=name, note=note, raster_sha256=receipt['sha256'],
                         validator_output=receipt['validator'], artifact=str(path.relative_to(ROOT)))
        base_card['stop_reason'] = 'research artifact only: official data/rules, full registry and compatible incumbent gate remain unverified'
    base_card['paired_comparison'] = summary['paired_differences'][summary['best_comparable_control']]
    base_card['elapsed_seconds'] = time.monotonic()-start
    save('evidence/run_card.json', base_card)
    print(json.dumps(base_card, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
