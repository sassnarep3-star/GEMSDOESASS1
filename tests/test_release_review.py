"""Regression tests for the revoked SWGB release and literal overlap audit."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_swgb_lattice import compare


def write_tif(path, values, transform=None):
    with rasterio.open(path, 'w', driver='GTiff', height=values.shape[0], width=values.shape[1],
                       count=1, dtype='float32', crs='EPSG:32611',
                       transform=transform or from_origin(100, 100, 1, 1)) as out:
        out.write(values.astype('float32'), 1)


def test_overlap_includes_exactly_three_pixels_and_rejects_above_threshold(tmp_path):
    a = np.zeros((12, 12)); b = np.zeros_like(a)
    a[3, 6] = 1; a[10, 10] = 1; b[3, 3] = 1
    candidate, prior = tmp_path / 'a.tif', tmp_path / 'b.tif'
    write_tif(candidate, a); write_tif(prior, b)
    result = compare(candidate, prior)
    assert result['within_3_pixels'] == 1 and result['directed_overlap'] == 0.5
    assert not result['duplicate']
    a[10, 10] = 0; write_tif(candidate, a)
    assert compare(candidate, prior)['duplicate']


def test_invalid_grid_and_values_fail_closed(tmp_path):
    a = np.zeros((5, 5)); a[1, 1] = 1
    candidate, prior = tmp_path / 'a.tif', tmp_path / 'b.tif'
    write_tif(candidate, a); write_tif(prior, a, from_origin(0, 0, 1, 1))
    with pytest.raises(ValueError, match='grid mismatch'):
        compare(candidate, prior)
    write_tif(prior, a); a[0, 0] = np.nan; write_tif(candidate, a)
    with pytest.raises(ValueError, match='invalid values'):
        compare(candidate, prior)


@pytest.mark.parametrize('script', ['build_submission.py'])
def test_legacy_release_tools_stop_before_side_effects(script):
    card = ROOT / 'evidence/run_card.json'
    old = card.read_bytes()
    result = subprocess.run([sys.executable, str(ROOT / 'scripts' / script)], capture_output=True, text=True)
    assert result.returncode != 0 and 'BLOCKED' in result.stderr
    assert card.read_bytes() == old


def test_current_pages_revoke_promotion():
    assert 'DO NOT SUBMIT' in (ROOT / 'index.html').read_text()
    for page in (ROOT / 'swgb').glob('*.html'):
        assert 'Do not submit' in page.read_text()
        assert 'downloads/' not in page.read_text()
    result = json.loads((ROOT / 'evidence/swgb_lattice_audit.json').read_text())
    assert result['duplicate'] and result['within_3_pixels'] / result['candidate_dots'] > .70


def test_generated_pages_and_download_index_do_not_revive_swgb_approval():
    """A revoked candidate must never be called a selector-cleared submission."""
    pages = [ROOT / 'docs/index.html', ROOT / 'docs/executive-summary.html', ROOT / 'docs/how-to-submit.html']
    pages += sorted((ROOT / 'docs/sites').glob('GEMSDOE*.html'))
    for page in pages:
        text = page.read_text()
        assert 'No SWGB, H-PBSC or BGAC-1 file is approved for submission.' in text
        assert 'selector-cleared file' not in text
        assert 'red / green banners' not in text
    download_index = (ROOT / 'docs/downloads/README.md').read_text()
    assert 'OK TO SUBMIT' not in download_index
    # SWGB/PBSC must stay revoked in the download index.
    assert 'withdrawn' in download_index and 'ok_to_submit = false' in download_index
    # Any approval in the download index must match the thermal run card exactly.
    card = json.loads((ROOT / 'evidence/thermal/run_card.json').read_text())
    if card['ok_to_download_and_submit']:
        assert 'OK TO DOWNLOAD AND SUBMIT' in download_index
        assert card['raster_name'] in download_index
    else:
        assert 'OK TO DOWNLOAD AND SUBMIT' not in download_index


def test_generated_verdict_matches_run_card_gates():
    """The verdict and the linked file on every generated page must equal the current release card.

    The pages are generated from the release named by `evidence/current_release.json` when that
    pointer exists (2026-10-31 H-BSTEP), else from `evidence/kdam/release.json` when present
    (2026-10-31 H-KDAM), otherwise from the 2026-10-30 thermal card. Every card in evidence/ must
    satisfy the same format/validator invariants regardless of which one the site promotes.
    """
    pointer = ROOT / 'evidence' / 'current_release.json'
    kdam = ROOT / 'evidence' / 'kdam' / 'release.json'
    if pointer.exists():
        ptr = json.loads(pointer.read_text())
        rel = json.loads((ROOT / ptr['release']).read_text())
        card = rel['card']
        gates = rel['gates']
        validator = rel.get('validator') or json.loads(
            (ROOT / 'evidence/kdam' / f"final_{card['submission_name']}.json").read_text())['validator']
    elif kdam.exists():
        card = json.loads(kdam.read_text())['card']
        gates = json.loads(kdam.read_text())['gates']
        validator = json.loads((ROOT / 'evidence/kdam' /
                                f"final_{card['submission_name']}.json").read_text())['validator']
    else:
        card = json.loads((ROOT / 'evidence/thermal/run_card.json').read_text())
        gates = json.loads((ROOT / 'evidence/thermal/release.json').read_text())['gates']
        validator = json.loads((ROOT / 'evidence/thermal/release.json').read_text())['validator']
    assert card['ok_to_download_and_submit'] == all(passed for _, passed in gates)
    verdict_word = 'OK TO DOWNLOAD AND SUBMIT' if card['ok_to_download_and_submit'] else 'NOT OK TO SUBMIT'
    assert card['submission_slots_used'] == 0
    assert len(card['note']) <= 140 and len(card['submission_name']) <= 140
    v = validator
    assert v['all_checks_passed']
    assert v['checks']['values_in_0_1_everywhere'] and v['checks']['no_nan_anywhere']
    assert v['checks']['crs_matches_template'] and v['checks']['shape_matches_template']
    assert v['checks']['transform_matches_template']
    for page in (ROOT / 'docs/index.html', ROOT / 'docs/executive-summary.html', ROOT / 'docs/how-to-submit.html'):
        text = page.read_text()
        assert verdict_word in text
        assert card['submission_name'].replace('.tif', '') in text
        assert card['raster_sha256'][:16] in text
    # score pages must label every number
    for page in (ROOT / 'docs/index.html', ROOT / 'docs/executive-summary.html'):
        text = page.read_text()
        assert 'HOLDOUT-DTI' in text
        assert 'OWNER-REPORT' in text


def test_regavoid_negative_release_is_disclosed_and_locked():
    """2026-10-31 H-REGAVOID: the negative release must stay disclosed, byte-locked and
    never rendered as an active download (AMEND-2 shipped-bytes gate)."""
    release = json.loads((ROOT / 'evidence/regavoid/release.json').read_text())
    card = release['card']
    assert card['ok_to_download_and_submit'] is False
    assert card['ok_to_download_and_submit'] == all(passed for _, passed in release['gates'])
    failed = [label for label, passed in release['gates'] if not passed]
    assert failed, 'a negative release must name its failing gates'
    run = json.loads((ROOT / 'evidence/regavoid/run_card.json').read_text())
    assert run['ok_to_submit'] is False and run['verdict'] == 'negative'
    assert run['slot']['used'] == 0
    assert run['budget']['experiments_run'] <= 3
    assert run['budget']['cumulative_seconds'] <= run['budget']['seconds_budget']
    canary = json.loads((ROOT / 'evidence/regavoid/leakage_canary.json').read_text())
    assert not canary['flagged_over_0p90']
    tif = ROOT / 'docs/downloads' / run['submission_name']
    assert tif.is_file()
    assert hashlib.sha256(tif.read_bytes()).hexdigest() == run['raster_sha256']
    # AMEND-2 structural record: TVGB shipped bytes measure 0.0000 while its release claimed 0.1287
    diag = json.loads((ROOT / 'evidence/regavoid/tvgb_shipped_diagnostic.json').read_text())
    assert diag['holdout_dti'] == 0.0 and diag['release_claimed_value'] > 0.1
    # rendered site: the panel discloses the negative verdict, the file is never an active link
    index = (ROOT / 'docs/index.html').read_text()
    assert 'NOT OK TO SUBMIT' in index
    assert 'H-REGAVOID' in index
    assert f'downloads/{run["submission_name"]}' not in index
    assert f'downloads/{run["submission_name"]}' not in (ROOT / 'docs/how-to-submit.html').read_text()


def test_parallel_sparse_card_is_self_consistent_and_not_submit_cleared():
    """The parallel lane's sparse placeholder must keep its own (negative) verdict."""
    card = json.loads((ROOT / 'evidence' /
                       'gemsdoesass1-unique-sparse-18000dots-20261031T050135Z-8b99942e-zeros_run_card.json').read_text())
    assert card['ok_to_download_and_submit'] is False
    assert card['ok_to_download'] is True
    v = card['validator_output']
    assert v['all_checks_passed']
    assert v['checks']['values_in_0_1_everywhere'] and v['checks']['no_nan_anywhere']
    assert v['checks']['crs_matches_template'] and v['checks']['shape_matches_template']
    assert v['checks']['transform_matches_template']
    assert v['checks']['zero_mass_on_known_catalogue_pixels']
    assert card['submission_slots_used'] == 0
    assert len(card['note']) <= 140 and len(card['submission_name']) <= 140
