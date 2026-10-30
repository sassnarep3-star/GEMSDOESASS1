"""Guards the 2026-10-30 gate audit: its evidence must stay consistent with the bytes it cites."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gate_audit_records_saturation_and_candidate_hashes():
    g = json.loads((ROOT / "evidence/gate_null_audit.json").read_text())
    assert g["gate_threshold"] == 0.70 and g["px"] == 3
    assert g["radius_sensitivity"]["by_radius"]["3"]["random"] > 0.70  # saturation is the finding
    assert "GATE SATURATED" in g["verdict"]
    # the 17 non-lattice registry rasters must still discriminate (random placement well below 70%)
    others = [r for r in g["rows"] if r["site"] != "calibration"]
    assert others and max(r["random_frac_within_3px"] for r in others) < 0.70


def test_candidate_validator_hashes_match_disk():
    v = json.loads((ROOT / "evidence/candidate_validator_20261030.json").read_text())
    for name, rec in v.items():
        matches = list(ROOT.rglob(name))
        matches = [m for m in matches if ".git" not in m.parts and ".venv" not in m.parts]
        assert len(matches) == 1, name
        assert hashlib.sha256(matches[0].read_bytes()).hexdigest() == rec["sha256"]
        assert rec["sha_match"] is True and rec["all_checks_passed"] is True
