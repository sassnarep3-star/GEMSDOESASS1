#!/usr/bin/env python3
"""Score every registry raster on the hide-and-recover holdout and fit holdout -> live calibration.

CAVEAT (flagged irregularity IR-01): registry rasters were built by their authors with the *full*
catalogue visible, so their holdout scores can be optimistic relative to a lane that only sees the
visible faults. The calibration is therefore a rough instrument; every number from it is labelled
HOLDOUT-DTI / PROJECTION, never a score.
Output: evidence/holdout_calibration.json
"""
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gems.grid import load_footprint, load_catalogue, EVIDENCE
from gems.holdout import build_folds, score_pooled, EVALUATOR_VERSION
from gems.registry import load_registry

t0 = time.time()
foot, cat = load_footprint(), load_catalogue()
folds, n_seg = build_folds(cat, foot)
print(f"segments={n_seg} withheld test positives per fold={[f.n_test for f in folds]}")
reg = load_registry()
rows = []
for r in reg:
    s = score_pooled([r["dots"]] * len(folds), folds, n_boot=200)
    rows.append(dict(site=r["site"], file=r["file"], owner_reported_live=r["score"], dots=int(r["dots"].sum()),
                     holdout_dti=s["holdout_dti"], ci95=s["ci95"], tp=s["tp"], fp=s["fp"], fn=s["fn"]))
    print(f"{r['site']:10s} live={r['score']:.4f} holdout={s['holdout_dti']:.4f} [{s['ci95'][0]:.4f},{s['ci95'][1]:.4f}] dots={int(r['dots'].sum())} {r['file'][:50]}")
x = np.array([r["holdout_dti"] for r in rows]); y = np.array([r["owner_reported_live"] for r in rows])
A = np.vstack([x, np.ones_like(x)]).T
slope, icpt = np.linalg.lstsq(A, y, rcond=None)[0]
pred = slope * x + icpt
resid = y - pred
from scipy.stats import spearmanr, pearsonr
out = dict(evaluator=EVALUATOR_VERSION, n_segments=int(n_seg), n_withheld_positives=int(sum(f.n_test for f in folds)),
           per_fold_test_positives=[f.n_test for f in folds], rows=rows,
           calibration=dict(model="live ~ slope*holdout + intercept (OLS over registry rasters)", slope=float(slope),
                            intercept=float(icpt), spearman=float(spearmanr(x, y).correlation), pearson=float(pearsonr(x, y)[0]),
                            rmse=float(np.sqrt(np.mean(resid ** 2))), n=int(len(rows))),
           caveat="IR-01: registry rasters saw the full catalogue when built; holdout numbers for them may be optimistic.",
           elapsed_s=round(time.time() - t0, 1))
EVIDENCE.mkdir(exist_ok=True)
(EVIDENCE / "holdout_calibration.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out["calibration"], indent=1), f"elapsed {out['elapsed_s']}s")
