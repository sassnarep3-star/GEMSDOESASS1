"""The historical raster audit can use pinned lightweight inputs without full features."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_history import core_data_path


def test_core_audit_inputs_resolve_to_hash_verified_bridge_mirror():
    sample = core_data_path(ROOT, 'sample_submission')
    faults = core_data_path(ROOT, 'existing_faults')
    # Preferred official copy wins when present and hash-valid (after prepare_data.py); otherwise the bridge mirror.
    official = ROOT / 'data/official'
    if (official / 'sample_submission.tif').is_file():
        assert sample == official / 'sample_submission.tif'
    else:
        assert sample == ROOT / 'data/bridge/sample_submission.tif'
    if (official / 'existing_faults.tif').is_file():
        assert faults == official / 'existing_faults.tif'
    else:
        assert faults == ROOT / 'data/bridge/existing_faults.tif'
    assert sample.is_file() and faults.is_file()


def test_core_audit_inputs_fail_closed_on_corrupt_preferred_official_file(tmp_path):
    import shutil

    (tmp_path / 'registry').mkdir()
    (tmp_path / 'data/official').mkdir(parents=True)
    shutil.copy(ROOT / 'registry/upstream_data_manifest.json', tmp_path / 'registry/upstream_data_manifest.json')
    # The bad official file exists, while a correct bridge copy is available.
    (tmp_path / 'data/official/sample_submission.tif').write_bytes(b'not a raster')
    (tmp_path / 'data/bridge').mkdir()
    (tmp_path / 'data/bridge/sample_submission.tif').write_bytes(b'also invalid')
    with pytest.raises(ValueError, match='pinned owner-mirror receipt'):
        core_data_path(tmp_path, 'sample_submission')
