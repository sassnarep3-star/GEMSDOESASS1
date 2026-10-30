#!/usr/bin/env python3
"""Null-calibration of the parallel-run uniqueness gate (70% of dots within 3 px of a registry raster).

Question: does the 3 px overlap test discriminate at all, or is it saturated by ANY dense dot file?
Method: draw N uniform-random dots inside the footprint (no model, no catalogue information) and measure
their within-3px overlap with every registry raster and with the 13gems 5 px calibration lattice, using the
exact definition in vendor/gems57/uniqueness.py (3 px disc dilation of the other raster's dots).
Reads the byte-verified cache written by scripts/registry_snapshot.py (.cache/registry). Writes evidence/gate_null_audit.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.registry import REGISTRY_ENTRIES, OVERLAP_PX, DOT_OVERLAP_MAX  # noqa: E402

N_DOTS = 37_654
SEED = 0
CACHE = ROOT / ".cache" / "registry"
LATTICE = CACHE / "GEMSDOE24" / "inputs" / "calibration" / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"


def band(p):
    with rasterio.open(p) as s:
        return s.read(1)


def find(site, fn):
    hits = sorted((CACHE / site).rglob(fn))
    if len(hits) != 1:
        raise SystemExit(f"expected exactly one cached copy of {site}/{fn}, found {len(hits)}")
    return hits[0]


def within_r(dots, probe_mask, radius):
    """fraction of probe pixels (bool mask) within `radius` px of `dots` (disc, as in vendor/gems57/uniqueness.py)."""
    if radius == 0:
        near = dots
    else:
        r = int(np.ceil(radius))
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        near = ndimage.binary_dilation(dots, structure=yy * yy + xx * xx <= radius * radius)
    return float(near[probe_mask].mean()) if probe_mask.any() else 0.0


def within3(dots, probe_mask):
    return within_r(dots, probe_mask, OVERLAP_PX)


def main():
    tmpl = band(ROOT / "data/bridge/sample_submission.tif")
    foot = np.isfinite(tmpl)
    cat = band(ROOT / "data/bridge/existing_faults.tif") == 1
    fy, fx = np.nonzero(foot)
    rng = np.random.default_rng(SEED)
    pick = rng.choice(fy.size, size=N_DOTS, replace=False)
    probe = np.zeros(foot.shape, bool)
    probe[fy[pick], fx[pick]] = True

    lat = band(LATTICE)
    lat_dots = np.nan_to_num(lat, nan=0.0) > 0.5
    rows = []
    for site, fn, score in REGISTRY_ENTRIES:
        p = find(site, fn)
        dots = np.nan_to_num(band(p), nan=0.0) > 0.5
        rows.append(dict(site=site, file=fn, owner_reported_score=score, registry_dots=int(dots.sum()),
                         random_frac_within_3px=round(within3(dots, probe), 4)))
    rows.append(dict(site="calibration", file=LATTICE.name, owner_reported_score=None,
                     registry_dots=int(lat_dots.sum()), random_frac_within_3px=round(within3(lat_dots, probe), 4)))
    # Radius sensitivity: 3 px saturates; exact (0 px) and 1 px matching do not. Candidates = TIFFs already in repo.
    radius = {}
    for rr in (0, 1, 3):
        radius[rr] = {"random": round(within_r(lat_dots, probe, rr), 4)}
    candidates = {
        "swgb_44090_zeros": ROOT / "swgb/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif",
        "pbsc_37654_zeros": ROOT / "docs/downloads/gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif",
    }
    cand_rows = []
    for name, cp in candidates.items():
        cd = np.nan_to_num(band(cp), nan=0.0) > 0.5
        row = dict(candidate=cp.name, dots=int(cd.sum()), vs_lattice={})
        for rr in (0, 1, 3):
            row["vs_lattice"][f"{rr}px"] = round(within_r(lat_dots, cd, rr), 4)
        cand_rows.append(row)
    for rr in (0, 1, 3):
        radius[rr]["lattice_self_coverage"] = round(within_r(lat_dots, foot, rr), 4)
    worst = max(rows, key=lambda r: r["random_frac_within_3px"])
    out = dict(
        question="Does the 70%/3px dot-overlap gate discriminate, or is it saturated by any dense dot file?",
        method="N uniform-random footprint pixels (seed 0), no model, no catalogue information; overlap per vendor/gems57/uniqueness.py",
        n_random_dots=N_DOTS, footprint_pixels=int(foot.sum()), catalogue_pixels=int(cat.sum()),
        gate_threshold=DOT_OVERLAP_MAX, px=OVERLAP_PX,
        rows=rows,
        random_placement_exceeds_gate_against=[r["file"] for r in rows if r["random_frac_within_3px"] > DOT_OVERLAP_MAX],
        worst=dict(file=worst["file"], random_frac_within_3px=worst["random_frac_within_3px"]),
        radius_sensitivity=dict(note="fraction of probe pixels within r px of the 13gems lattice dots; 'random' = N uniform footprint pixels; 'lattice_self_coverage' = all footprint pixels", by_radius=radius),
        repo_candidates_vs_lattice=cand_rows,
        verdict=("GATE SATURATED: uniform-random dots already exceed the gate against the calibration lattice; "
                 "the gate cannot distinguish a copy from an original dense emission"
                 if worst["random_frac_within_3px"] > DOT_OVERLAP_MAX else "gate discriminates on this null"),
    )
    (ROOT / "evidence" / "gate_null_audit.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("random_placement_exceeds_gate_against", "worst", "verdict")}, indent=2))


if __name__ == "__main__":
    main()
