import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from bgac import emit
from novelty import audit, canonical_hash, centered_ranks, exact_spearman
from vendor.gems57 import metric, spatial
from vendor.gems57.evaluate_holdout import evaluate, pooled_summary
from vendor.gems57.submission_writer import write_submission
from vendor.gems57.grid import HEIGHT, WIDTH, TRANSFORM
from vendor.gems57.uniqueness import dot_overlap


def tif(path, a, *, crs='EPSG:32611', transform=None):
    with rasterio.open(path, 'w', driver='GTiff', height=a.shape[0], width=a.shape[1],
        count=1, dtype='float32', crs=crs, transform=transform or from_origin(100,100,1,1), compress='deflate') as ds:
        ds.write(a.astype(np.float32), 1)
    return path


@pytest.mark.parametrize('seed', range(8))
def test_exact_metric_matches_shared_bruteforce(seed):
    rng = np.random.default_rng(seed)
    p = rng.random((8, 9)) * (rng.random((8, 9)) > .8)
    truth = rng.random((8, 9)) > .8
    exact, brute = metric.dti_exact(p, truth), metric.dti_bruteforce(p, truth)
    for key in ('tp', 'fp', 'fn', 'dti'):
        assert exact[key] == pytest.approx(brute[key], abs=1e-10)


def test_mask_visible_pixel_exactly_and_pool_terms():
    shape = (12, 12)
    truth = np.zeros(shape, bool)
    truth[5, 5] = True
    visible = np.zeros(shape, bool)
    visible[5, 6] = True
    p = visible.astype(np.float32)
    fold = dict(region=np.ones(shape, bool), visible=visible, truth=truth)
    result, terms = evaluate(p, fold, np.ones(shape, bool), block_side=4)
    assert result['dti'] == 0
    assert result['n_emitted'] == 0
    np.testing.assert_allclose(terms.sum(0), [0, 0, 1, 1])
    p[5, 5] = 1
    result, terms = evaluate(p, fold, np.ones(shape, bool), block_side=4)
    assert result['dti'] == pytest.approx(1)
    assert result['fpw'] == 0
    assert result['tpw'] == 1


def test_physical_clusters_merge_cropped_coordinates():
    a = np.ones((5, 5), bool)
    t = np.zeros_like(a); t[2, 2] = True
    fold = dict(region=a, visible=~a, truth=t)
    result, terms = evaluate(t.astype(np.float32), fold, a, block_side=4, origin=(4,4), global_shape=(12,12))
    assert terms.shape == (9,4)
    assert terms[4,3] == 1
    assert terms[:,3].sum() == result['n_truth']


def test_whole_component_folds_hide_cross_quadrant_tails():
    cat = np.zeros((60, 60), bool)
    cat[10:50, 10] = True  # crosses quadrant boundary; no tail can remain visible
    cat[10:50, 48] = True
    eligible = np.ones_like(cat)
    for fold in spatial.folds(cat, eligible, buffer_px=3):
        if fold['truth'].any():
            assert not (fold['visible'] & fold['held_all']).any()
            held_ids = np.unique(fold['components'][fold['truth']])
            assert not np.isin(fold['components'][fold['visible']], held_ids).any()
            assert not (fold['train'] & fold['region']).any()
            assert fold['receipt']['nearest_training_to_region_px'] > 3


def test_pooled_not_mean_of_fold_ratios_and_same_truth_required():
    terms = np.array([[1,0,0,1],[0,20,9,9]], float)
    summary = pooled_summary({'BGAC-1':terms, 'control':terms}, candidate='BGAC-1', draws=100)
    assert summary['scores']['BGAC-1']['dti'] == pytest.approx(1/(1+4+7.2))
    assert summary['paired_differences']['control']['ci95'] == [0,0]
    bad = terms.copy(); bad[1,3] += 1
    with pytest.raises(ValueError, match='same integer truth'):
        pooled_summary({'BGAC-1':terms, 'control':bad}, candidate='BGAC-1', draws=100)


@pytest.mark.parametrize('binary', [False, True])
def test_exact_rank_formula_with_ties(binary):
    rng = np.random.default_rng(1)
    a = rng.integers(0,12,1000)
    b = rng.integers(0,2 if binary else 17,1000)
    ranks, norm = centered_ranks(a)
    assert exact_spearman(ranks,norm,b) == pytest.approx(spearmanr(a,b).statistic, abs=1e-12)


def test_constant_rank_is_undefined():
    a = np.ones(20)
    ranks, norm = centered_ranks(a)
    assert exact_spearman(ranks, norm, np.arange(20)) is None


def test_emitter_no_wrap_deterministic_spacing():
    surface = np.arange(400, dtype=np.float32).reshape(20,20)
    allowed = np.ones_like(surface, bool); allowed[:, 0] = False
    dots = emit(surface, allowed, 18)
    assert dots.sum() == 18
    assert not dots[:, 0].any()
    np.testing.assert_array_equal(dots, emit(surface, allowed, 18))
    points = np.argwhere(dots)
    distances = np.sqrt(((points[:,None,:] - points[None,:,:])**2).sum(2))
    np.fill_diagonal(distances, 100)
    assert distances.min() > 3


@pytest.mark.parametrize('stage',['surface','dots'])
def test_literal_overlap_applies_to_both_phases(tmp_path, stage):
    a = np.zeros((20, 20), np.float32); a[::5,::5] = 1
    prior = tif(tmp_path/'prior.tif', a)
    fp = np.ones_like(a, bool)
    candidate = np.linspace(.01,1,400,dtype=np.float32).reshape(a.shape)
    inventory = dict(complete_within_scope=True,failed=0,scope='test fixture',rasters=[dict(
        repo='test',ref='pinned',path='prior.tif',local=str(prior),sha256=hashlib.sha256(prior.read_bytes()).hexdigest())])
    report = audit(candidate, fp, inventory, tmp_path, prior, stage=stage)
    assert report['duplicate']
    assert not report['cleared']
    assert report['comparisons'][0]['directed_overlap_within_3px'] == pytest.approx(dot_overlap(candidate, a))


def test_incomplete_registry_cannot_clear(tmp_path):
    with pytest.raises(ValueError, match='incomplete registry'):
        audit(np.ones((3,3)),np.ones((3,3),bool),dict(complete_within_scope=False),tmp_path,tmp_path/'x',stage='surface')


def test_nonfinite_prior_not_silently_normalized(tmp_path):
    a = np.zeros((10, 10), np.float32); a[0,0] = np.nan
    path = tif(tmp_path/'bad.tif',a)
    inv = dict(complete_within_scope=True, failed=0,scope='test',rasters=[dict(repo='test',ref='pin',path='bad',local=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())])
    r = audit(np.ones_like(a),np.ones_like(a,bool),inv,tmp_path,path,stage='surface')
    assert not r['cleared'] and r['unassessable'] == 1


@pytest.mark.parametrize('bad', [np.nan, np.inf, -.01, 1.01, -9999])
def test_writer_rejects_invalid_before_creating_files(tmp_path,bad):
    p = np.zeros((3,3),np.float32); p[1,1] = bad
    with pytest.raises(ValueError, match='normalized, finite'):
        write_submission(tmp_path/'bad.tif',p,tmp_path/'missing.tif',np.ones_like(p,bool),name='bad',note='bad')
    assert list(tmp_path.iterdir()) == []


def test_writer_name_note_limits(tmp_path):
    p = np.zeros((3,3),np.float32)
    with pytest.raises(ValueError,match='note'):
        write_submission(tmp_path/'x.tif',p,tmp_path/'ref.tif',np.ones_like(p,bool),name='x',note='x'*141)
    with pytest.raises(ValueError,match='name'):
        write_submission(tmp_path/'x.tif',p,tmp_path/'ref.tif',np.ones_like(p,bool),name=' ',note='x')


def test_shared_writer_roundtrip_and_atomic_grid_failure(tmp_path):
    p = np.zeros((HEIGHT, WIDTH),np.float32); p[100,100] = 1
    fp = p > 0
    reference = tif(tmp_path/'ref.tif',np.zeros_like(p),transform=TRANSFORM)
    receipt = write_submission(tmp_path/'test.tif',p,reference,fp,name='test-only',note='Unit-test artifact; never a competition submission')
    assert receipt['validator']['all_checks_passed']
    assert not receipt['approved_for_weekly_slot']
    assert receipt['promoted'] is False
    with pytest.raises(FileExistsError):
        write_submission(tmp_path/'test.tif',p,reference,fp,name='test-only',note='test')
    wrong = tif(tmp_path/'wrong.tif',np.zeros_like(p),crs='EPSG:32610',transform=TRANSFORM)
    with pytest.raises(ValueError,match='template validator'):
        write_submission(tmp_path/'failed.tif',p,wrong,fp,name='failed',note='test')
    assert not list(tmp_path.glob('failed.*'))
    assert not list(tmp_path.glob('.*'))


def test_frozen_negative_artifact_contract():
    card = json.loads((ROOT/'evidence/run_card.json').read_text())
    assert card['verdict'] == 'negative' and card['approved_for_submission'] is False
    assert card['raster_sha256'] is None
    assert card['submission_slots_used'] == 0
    assert card['holdout_status'].startswith('EXPLORATORY')
    assert len(card['note']) <= 140
    # BGAC packaged nothing. H-PBSC (later session) may place a research TIF in
    # docs/downloads only if its own card says ok_to_submit is false.
    pbsc = json.loads((ROOT/'evidence/pbsc/run_card.json').read_text())
    tifs = list((ROOT/'docs/downloads').glob('*.tif'))
    zips = list((ROOT/'docs/downloads').glob('*.zip'))
    assert pbsc['ok_to_submit'] is False
    assert pbsc['verdict'] == 'negative'
    assert all(p.name == pbsc['submission_name'] for p in tifs)
    assert all(p.name.startswith(pbsc['submission_name'].replace('.tif', '')) for p in zips)


def test_empty_inventory_never_clears(tmp_path):
    reference = tif(tmp_path/'ref.tif',np.zeros((4,4),np.float32))
    r = audit(np.arange(16,dtype=np.float32).reshape(4,4)/15,np.ones((4,4),bool),
        dict(complete_within_scope=True,failed=0,scope='empty',rasters=[]),tmp_path,reference,stage='surface')
    assert not r['cleared'] and not r['comparisons_complete']


def test_constant_surface_never_clears(tmp_path):
    prior = np.zeros((10,10),np.float32); prior[0,0] = 1
    path = tif(tmp_path/'prior.tif',prior)
    inv = dict(complete_within_scope=True,failed=0,scope='test',rasters=[dict(repo='test',ref='pin',path='prior',local=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())])
    r = audit(np.zeros_like(prior),np.ones_like(prior,bool),inv,tmp_path,path,stage='surface')
    assert not r['cleared']


def test_build_gate_fail_closed_before_holdout():
    # Regression for the disclosed first-pass bug: incomplete is not permission.
    source = (ROOT/'scripts/evaluate_holdout.py').read_text()
    assert "if not surface_receipt['cleared']:" in source
    assert source.index("if not surface_receipt['cleared']:") < source.index('for fold in spatial.folds')


def test_writer_rejects_outside_footprint_and_known_fault_support(tmp_path):
    p = np.zeros((3,3),np.float32); p[1,1] = 1
    with pytest.raises(ValueError,match='outside the valid footprint'):
        write_submission(tmp_path/'out.tif',p,tmp_path/'missing.tif',np.zeros_like(p,bool),name='test',note='test')
    with pytest.raises(ValueError,match='mapped catalogue'):
        write_submission(tmp_path/'known.tif',p,tmp_path/'missing.tif',np.ones_like(p,bool),catalogue=p>0,name='test',note='test')
    assert not list(tmp_path.iterdir())


def test_concurrent_main_research_preserved_not_promoted():
    manifest = json.loads((ROOT/'archive/parallel-main-f620a70/manifest.json').read_text())
    assert len(manifest['files']) == 14
    for row in manifest['files']:
        p = ROOT / row['archived_path']
        assert p.stat().st_size == row['bytes']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256']
        if row['original_path'].endswith('.html'):
            assert p.suffix == '.txt'
    pbsc = json.loads((ROOT/'evidence/pbsc/run_card.json').read_text())
    assert pbsc['ok_to_submit'] is False
    tifs = list((ROOT/'docs/downloads').glob('*.tif'))
    assert all(p.name == pbsc['submission_name'] for p in tifs)


def test_second_parallel_audit_preserved_and_ledger_retained():
    manifest = json.loads((ROOT/'archive/parallel-main-2f67fac/manifest.json').read_text())
    assert len(manifest['files']) == 44
    for row in manifest['files']:
        assert hashlib.sha256((ROOT/row['archived_path']).read_bytes()).hexdigest() == row['sha256']
    assert (ROOT/'knowledge/user-provided-submission-ledger.md').is_file()
    assert 'testpaths = tests' in (ROOT/'pytest.ini').read_text()
