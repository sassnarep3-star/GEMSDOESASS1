#!/usr/bin/env python3
"""Nine-site best-submission board + literal uniqueness audit (measured, not projected).

Reads only local bytes:
  * registry/focus_inventory.json       -- pinned, Git-blob-verified rasters (scripts/registry_snapshot.py)
  * data/bridge/sample_submission.tif   -- competition grid and scored footprint (finite cells)
  * data/bridge/existing_faults.tif     -- catalogue (value 1 inside the footprint = mapped fault pixel)
  * .cache/registry/GEMSDOE24/inputs/calibration/13gems_*.tif -- the 5-px lattice (a submitted file)

Owner-reported scores are copied from the user's ledger and labelled OWNER-REPORT.
Nothing here is a leaderboard estimate.  Output: evidence/nine_site_board.json.
Shared definitions (3 px dot halo, 70 % limit, saturation certificate) come from vendor/gems57.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vendor.gems57.metric import RADIUS_PX  # noqa: E402
from vendor.gems57.uniqueness import (OVERLAP_LIMIT, RHO_LIMIT, _near,  # noqa: E402
                                      dot_overlap, representation_class,
                                      saturation_certificate, surface_rho)

# Best owner-reported file per focus site, from the user ledger (OWNER-REPORT, not organizer-confirmed).
# Stems are matched exactly once against registry paths; the GEMSDOE30 entry is the plain file (no "-nanoutside").
BEST = {
    'GEMSDOE24': ('h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif', 0.2477),
    'GEMSDOE25': ('dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif', 0.2600),
    'GEMSDOE27': ('topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif', 0.2449),
    'GEMSDOE28': ('h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif', 0.2710),
    'GEMSDOE30': ('d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif', 0.2600),
    'GEMSDOE31': ('h27-4-solo-d28-20261004-8acb75e1-nan.tif', 0.2708),
    'GEMSDOE32': ('h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif', 0.2778),
    'GEMSDOE33': ('h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif', 0.2632),
    'GEMSDOE36': ('anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif', 0.2750),
}
LATTICE_REL = 'inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif'
SEEDS = (1, 2, 3, 4, 5)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dots_of(arr: np.ndarray) -> np.ndarray:
    return np.isfinite(arr) & (arr > 0)


def forward_overlap(cand_coords: np.ndarray, reg_tree: cKDTree, radius: float = RADIUS_PX) -> float:
    """Fraction of candidate dots within `radius` px of a registry dot (same rule as vendor dot_overlap)."""
    if not len(cand_coords):
        return 0.0
    d, _ = reg_tree.query(cand_coords, k=1)
    return float(np.mean(d <= radius + 1e-9))


def max_dots_satisfying_rule(uncovered_cells: int, overlap_limit: float = OVERLAP_LIMIT) -> int:
    """Largest N such that the literal rule (<= limit of dots within the halo) can still pass.

    Only dots on cells with no lattice dot within 3 px can be outside the halo. A pass needs
    outside/N >= 1 - limit, and outside <= uncovered, hence N <= uncovered / (1 - limit).
    """
    return int(np.floor(uncovered_cells / (1.0 - overlap_limit)))


def load_grid():
    with rasterio.open(ROOT / 'data/bridge/sample_submission.tif') as s:
        sub = s.read(1)
        grid = (s.shape, s.crs, s.transform)
    with rasterio.open(ROOT / 'data/bridge/existing_faults.tif') as f:
        cat_raw = f.read(1)
    footprint = np.isfinite(sub)
    catalogue = (cat_raw == 1) & footprint
    return footprint, catalogue, grid


def main():
    footprint, catalogue, grid = load_grid()
    allowed = footprint & ~catalogue
    fp_cells = int(footprint.sum())
    inv = json.loads((ROOT / 'registry/focus_inventory.json').read_text())
    rows = inv['rasters']
    sites = list(BEST)

    # ---- nine best files: integrity, grid, validator fields ----
    best = {}
    for site, (name, owner_score) in BEST.items():
        hits = [r for r in rows if r['repo'] == site and r['path'].endswith(name)]
        if len(hits) != 1:
            raise SystemExit(f'expected exactly one registry file for {site} {name}, found {len(hits)}')
        r = hits[0]
        path = ROOT / r['local']
        if not path.is_file():
            raise SystemExit(f'missing local registry file (run scripts/registry_snapshot.py): {path}')
        if sha256(path) != r['sha256']:
            raise SystemExit(f'sha256 mismatch for {path}')
        with rasterio.open(path) as src:
            if (src.shape, src.crs, src.transform) != grid:
                raise SystemExit(f'grid mismatch for {path}')
            arr = src.read(1).astype(np.float64)
        d = dots_of(arr)
        vals = arr[np.isfinite(arr)]
        best[site] = dict(
            registry_path=f"{r['repo']}/{r['path']}", sha256=r['sha256'], bytes=r['bytes'],
            owner_reported_score=owner_score,
            score_label='OWNER-REPORT (user ledger; no organizer receipt)',
            dots=int(d.sum()), dots_outside_footprint=int((d & ~footprint).sum()),
            dots_on_catalogue=int((d & catalogue).sum()),
            nan_inside_footprint=int(np.isnan(arr[footprint]).sum()),
            nan_outside_footprint=int(np.isnan(arr[~footprint]).sum()),
            values_min=float(vals.min()), values_max=float(vals.max()),
            values_in_01=bool(vals.min() >= 0 and vals.max() <= 1),
            representation=representation_class(int(d.sum()), fp_cells),
            _dots=d, _coords=np.argwhere(d), _arr=arr,
        )

    # ---- pairwise forward overlap among the nine (literal 3 px rule) ----
    pair = {}
    for a in sites:
        for b in sites:
            if a != b:
                pair[f'{a}->{b}'] = round(dot_overlap(best[a]['_dots'], best[b]['_dots']), 4)
    max_pair = max(pair.items(), key=lambda kv: kv[1])
    pairs_over = sorted(k for k, v in pair.items() if v > OVERLAP_LIMIT)

    # ---- lattice: GEMSDOE24 calibration raster; GEMSDOE13 submitted it (0.0904 owner-reported) ----
    lattice_path = ROOT / '.cache/registry/GEMSDOE24' / LATTICE_REL
    if not lattice_path.is_file():
        raise SystemExit('lattice missing: run scripts/registry_snapshot.py')
    cert = saturation_certificate(lattice_path, footprint, catalogue, expected_grid=grid)
    cert['witness_file'] = f'.cache/registry/GEMSDOE24/{LATTICE_REL}'  # repo-relative, portable evidence
    with rasterio.open(lattice_path) as src:
        lat = src.read(1)
    lat_dots = dots_of(lat)
    lat_tree = cKDTree(np.argwhere(lat_dots))

    # Null: uniformly random dots, same count as the 0.2778 file, placed only on allowed cells.
    k_null = best['GEMSDOE32']['dots']
    allowed_idx = np.flatnonzero(allowed.ravel())
    null_fracs = []
    for seed in SEEDS:
        pick = np.random.default_rng(seed).choice(allowed_idx, size=k_null, replace=False)
        coords = np.argwhere(np.isin(np.arange(footprint.size), pick).reshape(footprint.shape))
        null_fracs.append(forward_overlap(coords, lat_tree))
    lattice_vs = {s: round(forward_overlap(best[s]['_coords'], lat_tree), 4) for s in sites}

    lat_halo = _near(lat_dots)
    uncovered_fp = int((footprint & ~lat_halo).sum())
    uncovered_allowed = int((allowed & ~lat_halo).sum())
    n_max = max_dots_satisfying_rule(uncovered_fp)
    feasibility = {s: dict(dots=best[s]['dots'],
                           min_dots_outside_halo_needed=int(np.ceil((1 - OVERLAP_LIMIT) * best[s]['dots'])),
                           feasible_under_literal_rule=bool(best[s]['dots'] <= n_max)) for s in sites}

    # ---- one pass over the whole registry: every raster vs all nine best files ----
    scan = {s: dict(max=0.0, nearest=None, exact=[]) for s in sites}
    registry_dot_groups = {}
    for r in rows:
        p = ROOT / r['local']
        if not p.is_file():
            raise SystemExit(f'registry file not restored: {p}')
        with rasterio.open(p) as src:
            a = src.read(1)
        if a.shape != footprint.shape:
            continue
        rd = dots_of(a)
        tag = f"{r['repo']}/{r['path']}"
        registry_dot_groups.setdefault(hashlib.sha256(np.packbits(rd).tobytes()).hexdigest(), []).append(tag)
        if not rd.any():
            continue
        tree = cKDTree(np.argwhere(rd))
        for s in sites:
            if tag == best[s]['registry_path']:
                continue
            ov = forward_overlap(best[s]['_coords'], tree)
            if ov > scan[s]['max']:
                scan[s]['max'], scan[s]['nearest'] = ov, tag
            if np.array_equal(rd, best[s]['_dots']):
                scan[s]['exact'].append(tag)
    # Cross-check: the KD-tree rule must equal the shared dot_overlap on each site's nearest raster.
    crosscheck = {}
    for s in sites:
        if scan[s]['nearest'] is None:
            continue
        repo, path = scan[s]['nearest'].split('/', 1)
        r = next(x for x in rows if x['repo'] == repo and x['path'] == path)
        with rasterio.open(ROOT / r['local']) as src:
            rd = dots_of(src.read(1))
        shared = dot_overlap(best[s]['_dots'], rd)
        kd = forward_overlap(best[s]['_coords'], cKDTree(np.argwhere(rd)))
        crosscheck[s] = dict(shared_dot_overlap=round(shared, 6), kdtree=round(kd, 6),
                             agree=bool(abs(shared - kd) < 1e-6))
    if not all(v['agree'] for v in crosscheck.values()):
        raise SystemExit(f'KD-tree rule disagrees with shared implementation: {crosscheck}')

    # ---- surface Spearman among the nine (0.90 gate, dot-union) ----
    rho_pairs = {}
    for i, a in enumerate(sites):
        for b in sites[i + 1:]:
            rho = surface_rho(best[a]['_arr'], best[b]['_arr'], footprint)
            v = rho['spearman_on_dot_union']
            rho_pairs[f'{a}|{b}'] = dict(spearman_dot_union=None if v != v else round(v, 4),
                                         jaccard_dot_sets=round(rho['jaccard_dot_sets'], 4))

    # ---- exact duplicates across the registry (identical positive-pixel sets) ----
    dot_groups = [v for v in registry_dot_groups.values() if len(v) > 1]
    cross_site = [v for v in dot_groups if len({x.split('/')[0] for x in v}) > 1]

    out = dict(
        evidence_class='REGISTRY-MEASUREMENT + OWNER-REPORT (scores are not organizer receipts)',
        generated_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),
        grid=dict(shape=list(grid[0]), crs=grid[1].to_string(), transform=list(grid[2])[:6]),
        footprint_cells=fp_cells, catalogue_cells=int(catalogue.sum()), allowed_cells=int(allowed.sum()),
        thresholds=dict(overlap_limit=OVERLAP_LIMIT, rho_limit=RHO_LIMIT, radius_px=RADIUS_PX),
        registry_scope=inv['scope'], registry_rasters_scanned=len(rows), registry_failed=inv.get('failed'),
        nine_site_best={s: {k: v for k, v in best[s].items() if not k.startswith('_')} for s in sites},
        nine_site_pairwise_forward_overlap=pair,
        nine_site_pairs_over_limit=len(pairs_over), nine_site_pairs_total=len(pair),
        nine_site_max_pair=dict(pair=max_pair[0], overlap=max_pair[1]),
        nine_site_surface_pairs=rho_pairs,
        per_best_registry_scan={s: dict(max_forward_overlap_any_other_registry_raster=round(scan[s]['max'], 4),
                                        nearest_registry_raster=scan[s]['nearest'],
                                        exact_dot_set_matches=scan[s]['exact']) for s in sites},
        per_best_crosscheck=crosscheck,
        lattice=dict(file=f'.cache/registry/GEMSDOE24/{LATTICE_REL}', sha256=sha256(lattice_path),
                     dots=int(lat_dots.sum()), saturation_certificate=cert,
                     null_random_same_count_overlap=dict(k=k_null, seeds=list(SEEDS),
                                                          per_seed=[round(x, 4) for x in null_fracs],
                                                          mean=round(float(np.mean(null_fracs)), 4)),
                     nine_site_best_vs_lattice=lattice_vs),
        lattice_gate_bound=dict(uncovered_footprint_cells=uncovered_fp,
                                uncovered_allowed_cells=uncovered_allowed,
                                max_dots_satisfying_literal_70pct_rule=n_max,
                                per_site_feasibility=feasibility,
                                reasoning=('Dots outside the 3 px halo of the lattice can only sit on uncovered '
                                           'cells. At least 30% of a candidate\'s dots must be outside the halo, so '
                                           'N <= uncovered / 0.30.')),
        exact_duplicates=dict(dot_set_groups=len(dot_groups), dot_set_groups_detail=dot_groups,
                              cross_site_dot_set_groups=len(cross_site), cross_site_detail=cross_site),
    )
    (ROOT / 'evidence').mkdir(exist_ok=True)
    (ROOT / 'evidence/nine_site_board.json').write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
    print(json.dumps(dict(
        max_pair=out['nine_site_max_pair'], pairs_over_limit=f"{len(pairs_over)}/{len(pair)}",
        lattice_null_mean=out['lattice']['null_random_same_count_overlap']['mean'],
        lattice_universal_blocker=cert['universal_overlap_blocker'],
        uncovered_footprint=uncovered_fp, max_dots_literal_rule=n_max,
        exact_dot_groups=len(dot_groups), cross_site_dot_groups=len(cross_site),
        per_best_max_overlap={s: scan[s]['max'] for s in sites}), indent=2))


if __name__ == '__main__':
    main()
