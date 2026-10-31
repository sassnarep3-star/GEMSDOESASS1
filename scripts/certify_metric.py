#!/usr/bin/env python3
"""Certify the closed-form algebra of the local DTI evaluator before using it.

The evaluator is ``vendor/gems57/metric.py`` (hash-pinned, unmodified).  Nothing
in this project may be optimised against an instrument whose algebra has not
been reproduced from its own bytes, so this script re-derives the identities and
checks them numerically against ``dti_exact`` / ``dti_binary``:

  (I1)  D  = TP + a*FP + b*FN  with FN = K - TP  =>  D = a*(TP+FP) + b*K
        (only because a + b = 1; it is the single most important identity here
        because it makes the denominator a *linear* function of emitted mass)
  (I2)  dDTI/dTP  = (a*FP + b*K) / D^2        (recall lever)
        dDTI/dFP  = -a*TP / D^2               (precision lever)
        ratio |dDTI/dTP| / |dDTI/dFP| = (a*FP + b*K) / (a*TP)
  (I3)  One more emitted pixel is accepted iff  dT > a*DTI*(dT + dFP)
        where dT is marginal truth credit and dFP its marginal false-positive
        cost.  For DTI ~ 0.28 this is dT > 0.0593*dFP.
  (I4)  Oracle ceiling: predicting exactly the truth set gives DTI = 1.0
        (TP = K, FP = 0, FN = 0).
  (I5)  Straight-line model: dots of spacing s along a correctly identified
        fault give T = K*(1 - s/12), FP = 0 => DTI = (1-s/12)/(1-s/60).

Emitted evidence: evidence/metric_certification.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vendor.gems57.metric import (ALPHA, BETA, RADIUS_PX, dti_binary, dti_exact,  # noqa: E402
                                  dti_bruteforce, kernel)

rng = np.random.default_rng(20261031)


def line_truth(shape=(160, 160), rows=(40, 80, 120), cols=slice(10, 150)):
    t = np.zeros(shape, bool)
    for r in rows:
        t[r, cols] = True
    return t


def main() -> int:
    out = {"evidence_class": "METRIC-CERTIFICATION", "evaluator": "vendor/gems57/metric.py",
           "alpha": ALPHA, "beta": BETA, "radius_px": RADIUS_PX, "checks": []}

    def check(name, got, want, tol=1e-9, note=""):
        ok = bool(abs(got - want) <= tol * max(1.0, abs(want)))
        out["checks"].append(dict(name=name, got=float(got), want=float(want), tol=tol, ok=ok, note=note))
        print(f"[metric] {'OK ' if ok else 'FAIL'} {name}: got={got!r} want={want!r} {note}")
        return ok

    ok = True
    H, W = 160, 160
    truth = line_truth((H, W))

    # ---- (I4) oracle ceiling -------------------------------------------------
    r = dti_exact(truth.astype(np.float64), truth)
    ok &= check("I4 oracle DTI (P == T)", r["dti"], 1.0, 1e-12,
                f"TP={r['tp']:.1f} FP={r['fp']:.1f} FN={r['fn']:.1f} K={r['n_truth']}")

    # ---- (I1) denominator identity ------------------------------------------
    cases = []
    # a) random sparse dots
    p = np.zeros((H, W))
    idx = rng.choice(H * W, 400, replace=False)
    p.flat[idx] = 1.0
    cases.append(("random 400 dots", p))
    # b) dots on the truth line, spacing 3
    p2 = np.zeros((H, W))
    for r_ in (40, 80, 120):
        p2[r_, 10:150:3] = 1.0
    cases.append(("on-line dots s=3", p2))
    # c) a soft field
    from scipy import ndimage as ndi
    p3 = np.clip(ndi.gaussian_filter(truth.astype(float) * 0 + rng.random((H, W)) * 0.2, 2) * 3, 0, 1)
    cases.append(("soft random field", p3))
    # d) 5-px corridor
    p4 = np.zeros((H, W))
    for r_ in (40, 80, 120):
        p4[r_ - 2:r_ + 3, 10:150] = 1.0
    cases.append(("5 px corridor", p4))
    # e) points at 1 px off the line
    p5 = np.zeros((H, W))
    for r_ in (40, 80, 120):
        p5[r_ + 1, 10:150:2] = 1.0
    cases.append(("1 px off-line s=2", p5))

    for name, pred in cases:
        r = dti_exact(pred, truth)
        K = r["n_truth"]
        D_recomputed = ALPHA * (r["tp"] + r["fp"]) + BETA * K
        D_actual = r["tp"] + ALPHA * r["fp"] + BETA * r["fn"]
        ok &= check(f"I1 denominator [{name}]", D_recomputed, D_actual, 1e-9,
                    f"DTI={r['dti']:.4f} TP={r['tp']:.1f} FP={r['fp']:.1f} K={K} n_emit={r['n_emitted']}")
        # cross-check the fast path against the literal brute-force oracle
        rb = dti_bruteforce(pred, truth)
        ok &= check(f"I1b brute-force agreement [{name}]", r["dti"], rb["dti"], 1e-9)

    # ---- (I2) lever ratio ----------------------------------------------------
    r = dti_exact(p, truth)
    K = r["n_truth"]
    D = ALPHA * (r["tp"] + r["fp"]) + BETA * K
    d_dtp = (ALPHA * r["fp"] + BETA * K) / D ** 2
    d_dfp = -ALPHA * r["tp"] / D ** 2
    # numeric: raise TP by 1 (add an on-truth pixel with no FP) -- use a real edit
    yy, xx = np.nonzero(truth)
    p_add = p.copy()
    p_add[yy[0], xx[0]] = 1.0            # an on-truth pixel: adds TP, adds ~0 FP
    r2 = dti_exact(p_add, truth)
    ok &= check("I2a sign of recall lever", np.sign(r2["dti"] - r["dti"]), 1.0, 0.0,
                f"DTI {r['dti']:.4f} -> {r2['dti']:.4f}")
    p_add2 = p.copy()
    p_add2[5, 5] = 1.0                   # far from truth: pure FP
    r3 = dti_exact(p_add2, truth)
    ok &= check("I2b sign of precision lever", np.sign(r3["dti"] - r["dti"]), -1.0, 0.0,
                f"DTI {r['dti']:.4f} -> {r3['dti']:.4f}")
    out["lever_ratio_recall_over_precision"] = float(abs(d_dtp / d_dfp))
    print(f"[metric] lever ratio |dDTI/dTP| / |dDTI/dFP| = {abs(d_dtp / d_dfp):.1f} "
          f"(at TP={r['tp']:.0f} FP={r['fp']:.0f} K={K})")

    # ---- (I3) marginal acceptance bar ---------------------------------------
    # place one dot at each perpendicular offset from a long straight fault and
    # test the predicted bar dT > a*DTI*(dT+dFP) against the measured DTI change
    truth1 = np.zeros((H, W), bool)
    truth1[80, 10:150] = True
    base = np.zeros((H, W))
    base[80, 10:150:6] = 1.0             # sparse on-line dots spacing 6
    r0 = dti_exact(base, truth1)
    rows = []
    for off in range(0, 4):
        cand = base.copy()
        cand[80 + off, 20:120] = 1.0
        r1 = dti_exact(cand, truth1)
        improved = r1["dti"] > r0["dti"]
        bar = ALPHA * r0["dti"]
        # empirical dT and dFP per added pixel
        dT = (r1["tp"] - r0["tp"]) / 100.0
        dFP = (r1["fp"] - r0["fp"]) / 100.0
        predicted = dT > bar * (dT + dFP)
        rows.append(dict(offset_px=off, measured_dti=float(r1["dti"]), improved=bool(improved),
                         dT_per_px=float(dT), dFP_per_px=float(dFP),
                         bar_alpha_times_dti=float(bar), predicted_accept=bool(predicted),
                         agree=bool(improved) == bool(predicted)))
        ok &= bool(improved) == bool(predicted)
    out["marginal_rule"] = dict(base_dti=float(r0["dti"]), rows=rows)
    for row in rows:
        print(f"[metric] offset {row['offset_px']}px: dTI={row['measured_dti'] - r0['dti']:+.5f} "
              f"improved={row['improved']} predicted={row['predicted_accept']} "
              f"dT={row['dT_per_px']:.4f} dFP={row['dFP_per_px']:.4f} bar={row['bar_alpha_times_dti']:.4f}")

    # ---- (I5) straight-line spacing model -----------------------------------
    rows = []
    for s in (1, 1.5, 2, 2.8, 3, 4, 6):
        pred = np.zeros((H, W))
        step = max(1, int(round(s)))
        pred[80, 10:150:step] = 1.0
        rr = dti_exact(pred, truth1)
        model_T = (1 - s / 12.0)
        model_FP = 0.0
        model = model_T / (ALPHA * (model_T + model_FP) + BETA)
        rows.append(dict(spacing_px=s, measured_dti=float(rr["dti"]), model_dti=float(model),
                         coverage=float(rr["coverage"])))
        print(f"[metric] spacing {s:>4} px on a perfect line: measured DTI={rr['dti']:.4f} "
              f"model={model:.4f} coverage={rr['coverage']:.4f}")
    out["spacing_model"] = rows

    out["kernel_sum_over_line_profile"] = float(
        sum(kernel(np.hypot(0, d)) for d in range(-3, 4)))
    out["all_checks_passed"] = bool(ok)
    (ROOT / "evidence").mkdir(exist_ok=True)
    (ROOT / "evidence/metric_certification.json").write_text(
        json.dumps(out, indent=2, allow_nan=False) + "\n")
    print("[metric] " + ("ALL CHECKS PASSED" if ok else "CERTIFICATION FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
