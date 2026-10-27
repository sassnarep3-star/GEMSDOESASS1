import numpy as np, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gems.metric import dti_exact, dti_binary, dti_bruteforce

def test_fast_matches_bruteforce():
    rng = np.random.default_rng(1)
    for t in range(5):
        truth = rng.random((24, 24)) < 0.04
        pred = (rng.random((24, 24)) < 0.06).astype(float) * rng.random((24, 24))
        a, b = dti_exact(pred, truth), dti_bruteforce(pred, truth)
        assert abs(a["dti"] - b["dti"]) < 1e-9 and abs(a["tp"] - b["tp"]) < 1e-9 and abs(a["fp"] - b["fp"]) < 1e-9
        pb = pred > 0.5
        c, d = dti_binary(pb, truth), dti_bruteforce(pb.astype(float), truth)
        assert abs(c["dti"] - d["dti"]) < 1e-9

def test_identities():
    rng = np.random.default_rng(2)
    truth = rng.random((30, 30)) < 0.05
    r = dti_binary(truth, truth)
    assert abs(r["dti"] - 1.0) < 1e-9 and r["fp"] == 0.0
    r0 = dti_binary(np.zeros_like(truth), truth)
    assert r0["dti"] == 0.0 and r0["fn"] == truth.sum()
