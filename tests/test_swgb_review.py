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
import audit_swgb_lattice as audit


def write_tif(path, values, transform=None):
    with rasterio.open(path, 'w', driver='GTiff', height=values.shape[0], width=values.shape[1],
                       count=1, dtype='float32', crs='EPSG:32611',
                       transform=transform or from_origin(100, 200, 100, 100)) as ds:
        ds.write(values.astype('float32'), 1)


def test_directed_overlap_and_grid_checks(tmp_path, monkeypatch):
    candidate, lattice, template = [tmp_path / x for x in ('candidate.tif', 'lattice.tif', 'template.tif')]
    a = np.zeros((12, 12), dtype='float32'); a[3, 3] = 1; a[8, 8] = 1
    b = np.zeros_like(a); b[3, 4] = 1
    write_tif(candidate, a); write_tif(lattice, b); write_tif(template, np.zeros_like(a))
    for name, path in [('CANDIDATE_SHA', candidate), ('LATTICE_SHA', lattice), ('TEMPLATE_SHA', template)]:
        monkeypatch.setattr(audit, name, audit.digest(path))
    report = audit.audit(candidate, lattice, template)
    assert report['candidate_directed_overlap'] == .5
    assert report['duplicate'] is False
    assert report['approved_for_submission'] is False  # one witness never clears
    assert report['format_check']['ok']
    write_tif(lattice, b, transform=from_origin(101, 200, 100, 100))
    with pytest.raises(ValueError, match='Hash mismatch'):
        audit.audit(candidate, lattice, template)
    monkeypatch.setattr(audit, 'LATTICE_SHA', audit.digest(lattice))
    with pytest.raises(ValueError, match='Misaligned'):
        audit.audit(candidate, lattice, template)


def test_frozen_receipt_and_withdrawal():
    receipt = json.loads((ROOT / 'evidence/swgb_lattice_review.json').read_text())
    artifact = ROOT / 'swgb/downloads' / receipt['candidate']
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() == receipt['candidate_sha256']
    assert receipt['candidate_directed_overlap'] > receipt['threshold']
    assert receipt['duplicate'] and not receipt['approved_for_submission']
    assert receipt['format_check']['ok']
    for page in [ROOT / 'index.html', *(ROOT / 'swgb').glob('*.html')]:
        text = page.read_text().lower()
        assert 'do not submit' in text
        assert 'ok to download and submit' not in text
        assert '.tif"' not in text


def test_legacy_builder_is_blocked():
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/build_submission.py')],
                            capture_output=True, text=True, cwd=ROOT)
    assert result.returncode != 0
    assert 'BLOCKED: legacy SWGB builder' in result.stderr


@pytest.mark.parametrize('script,args', [('run_experiments.py', ['e1']), ('calibrate_holdout.py', [])])
def test_old_experiment_commands_cannot_overwrite_evidence(script, args):
    result = subprocess.run([sys.executable, str(ROOT / 'scripts' / script), *args],
                            capture_output=True, text=True, cwd=ROOT)
    assert result.returncode != 0
    assert 'BLOCKED:' in result.stderr
