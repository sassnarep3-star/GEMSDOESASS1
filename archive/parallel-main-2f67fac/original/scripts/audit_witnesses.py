#!/usr/bin/env python3
"""Re-read pinned GeoTIFF witnesses and independently audit duplicate claims.

This is a forensic audit, NOT the shared holdout evaluator, submission writer,
registry selector, or a geological experiment. It cannot authorize a submission.
"""
from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import tempfile
import zipfile

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

from fetch_witnesses import MANIFEST, ROOT, check_entry, sha256

SITE_IDS = tuple(f'GEMSDOE{i}' for i in (24, 25, 27, 28, 30, 31, 32, 33, 36))


def read_one(path: Path):
    with rasterio.open(path) as src:
        if src.count != 1:
            raise ValueError(f'{path.name} must have exactly one band')
        a = src.read(1)
        # The template's GDAL mask, not pixel value zero, defines its footprint.
        mask = src.read_masks(1) > 0
        grid = (src.crs, src.transform, src.shape)
        meta = {'dtype': src.dtypes[0], 'nodata': str(src.nodata),
                'crs': str(src.crs), 'shape': list(src.shape),
                'transform': list(src.transform)[:6]}
    return a, mask, grid, meta


def coverage(ref: np.ndarray, radius: float = 3) -> np.ndarray:
    """Euclidean <= radius in the aligned raster grid; an empty reference has no halo."""
    ref = np.asarray(ref, dtype=bool)
    if ref.ndim != 2 or not math.isfinite(radius) or radius < 0:
        raise ValueError('Expected a 2-D mask and a finite nonnegative radius')
    if not ref.any():
        return np.zeros_like(ref)
    return distance_transform_edt(~ref) <= radius


def overlap(candidate: np.ndarray, halo: np.ndarray) -> dict:
    candidate, halo = np.asarray(candidate, dtype=bool), np.asarray(halo, dtype=bool)
    if candidate.ndim != 2 or candidate.shape != halo.shape:
        raise ValueError('Dot and halo grids must align')
    count = int(candidate.sum())
    hits = int((candidate & halo).sum())
    return {'dots': count, 'hits': hits, 'fraction': hits / count if count else None,
            # Exact integer comparison avoids treating equality as a breach.
            'duplicate': bool(10 * hits > 7 * count) if count else None}


def binary_spearman(a: np.ndarray, b: np.ndarray, footprint: np.ndarray) -> float | None:
    """Exact Spearman with ties on binary footprint arrays (Pearson of the indicators)."""
    a, b, footprint = (np.asarray(v, dtype=bool) for v in (a, b, footprint))
    if a.ndim != 2 or a.shape != b.shape or a.shape != footprint.shape:
        raise ValueError('Binary masks and footprint must align')
    n = int(footprint.sum())
    x, y = int((a & footprint).sum()), int((b & footprint).sum())
    joint = int((a & b & footprint).sum())
    if not n or x in (0, n) or y in (0, n):
        return None  # Constant fields have undefined rank correlation, not a pass.
    numerator = n * joint - x * y
    return numerator / math.sqrt(float(x * (n - x) * y * (n - y)))


def placement_bound(footprint_pixels: int, covered_pixels: int, dots: int) -> dict:
    """Minimum possible directional overlap for K distinct in-footprint dots."""
    if any(isinstance(x, bool) or not isinstance(x, int) for x in (footprint_pixels, covered_pixels, dots)):
        raise ValueError('Counts must be integers')
    if not 0 < footprint_pixels or not 0 <= covered_pixels <= footprint_pixels:
        raise ValueError('Invalid footprint/coverage counts')
    if not 0 < dots <= footprint_pixels:
        raise ValueError('Dot count must be in 1..footprint_pixels')
    uncovered = footprint_pixels - covered_pixels
    minimum = max(0, dots - uncovered)
    first = (10 * uncovered) // 3 + 1
    return {'footprint_pixels': footprint_pixels, 'covered_pixels': covered_pixels,
            'uncovered_pixels': uncovered, 'candidate_distinct_dots': dots,
            'minimum_overlapping_dots': minimum, 'minimum_overlap_fraction': minimum / dots,
            'threshold': 0.70, 'guaranteed_duplicate': 10 * minimum > 7 * dots,
            'first_forced_dot_count': first if first <= footprint_pixels else None,
            'interpretation': 'A non-forced bound is UNKNOWN, never a uniqueness pass.'}


def inspect_raster(path: Path, grid, footprint: np.ndarray) -> tuple[dict, np.ndarray]:
    a, _, actual_grid, meta = read_one(path)
    if actual_grid != grid:
        raise ValueError(f'{path.name}: CRS, shape or transform differs from template')
    inside, outside = a[footprint], a[~footprint]
    finite_inside = np.isfinite(inside)
    within = finite_inside & (inside >= 0) & (inside <= 1)
    binary = bool(np.all((inside == 0) | (inside == 1)))
    mask = footprint & np.isfinite(a) & (a > 0)
    report = dict(meta, sha256=sha256(path), grid_matches_owner_mirror=True,
                  no_nan_or_inf_inside=bool(finite_inside.all()),
                  in_footprint_range_0_1=bool(within.all()),
                  full_array_finite=bool(np.isfinite(a).all()),
                  whole_array_range_0_1=bool(np.all(np.isfinite(a) & (a >= 0) & (a <= 1))),
                  outside_all_nan=bool(np.isnan(outside).all()),
                  outside_all_zero=bool(np.all(outside == 0)),
                  binary_inside=binary, positive_pixels=int(mask.sum()),
                  no_positive_outside=bool(not np.any(np.isfinite(outside) & (outside > 0))))
    if (meta['dtype'] != 'float32' or not report['no_nan_or_inf_inside']
            or not report['in_footprint_range_0_1'] or not binary
            or not report['no_positive_outside']):
        raise ValueError(f'{path.name}: forensic binary witness is malformed: {report}')
    return report, mask


def validate_registered_witness(registry: dict, lattice_hash: str, lattice_values: np.ndarray,
                                footprint: np.ndarray) -> tuple[dict, str]:
    """Bind the lattice bytes AND footprint contents to one pinned owner-registry entry."""
    entries = registry.get('entries')
    if not isinstance(entries, list) or registry.get('n_entries') != len(entries):
        raise ValueError('Malformed pinned registry snapshot')
    if lattice_values.ndim != 2 or lattice_values.shape != footprint.shape or not footprint.any():
        raise ValueError('Lattice and nonempty footprint must align')
    matching = [row for row in entries if row.get('id') == 'reg-052']
    if len(matching) != 1 or matching[0].get('file_sha256') != lattice_hash:
        raise ValueError('Registered lattice identity does not match the pinned witness')
    content_sha = hashlib.sha256(np.asarray(lattice_values[footprint], dtype='<f4').tobytes()).hexdigest()
    if content_sha != matching[0].get('footprint_sha256'):
        raise ValueError('Registered lattice footprint checksum mismatch')
    return matching[0], content_sha


def inspect_local_research_artifacts(manifest: dict, grid, footprint: np.ndarray) -> tuple[dict, np.ndarray]:
    """Re-read the parallel branch's tracked TIFFs/ZIP; never treat them as approved."""
    rows = manifest.get('local_research_artifacts', [])
    entries = {row['id']: row for row in rows}
    if len(entries) != len(rows) or set(entries) != {'parallel_zeros', 'parallel_nan', 'parallel_zip'}:
        raise ValueError('Local research-artifact inventory is incomplete or duplicated')
    paths = {}
    for name, row in entries.items():
        relative = Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError(f'Invalid local research-artifact path: {name}')
        full = (ROOT / relative).resolve()
        if not full.is_relative_to(ROOT.resolve()) or not full.is_file() or sha256(full) != row['sha256']:
            raise ValueError(f'Local research artifact missing or hash-mismatched: {name}')
        paths[name] = full
    zero_report, zero_mask = inspect_raster(paths['parallel_zeros'], grid, footprint)
    nan_report, nan_mask = inspect_raster(paths['parallel_nan'], grid, footprint)
    with zipfile.ZipFile(paths['parallel_zip']) as archive:
        members = archive.infolist()
        if (len(members) != 1 or members[0].filename != paths['parallel_zeros'].name
                or members[0].is_dir() or members[0].file_size != paths['parallel_zeros'].stat().st_size):
            raise ValueError('Parallel research ZIP must contain only the named zeros TIFF')
        digest = hashlib.sha256()
        with archive.open(members[0]) as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        if digest.hexdigest() != entries['parallel_zeros']['sha256']:
            raise ValueError('Parallel research ZIP member does not match the pinned zeros TIFF')
    report = {
        'provenance': 'Concurrent PR #3 research artifact; not generated by this audit.',
        'zeros_path': entries['parallel_zeros']['path'], 'zeros_tif': zero_report,
        'nan_path': entries['parallel_nan']['path'], 'nan_tif': nan_report,
        'zip_path': entries['parallel_zip']['path'], 'zip_sha256': entries['parallel_zip']['sha256'],
        'zip_member_matches_zeros': True,
        'twins_have_same_in_footprint_binary_mask': bool(np.array_equal(zero_mask, nan_mask)),
        'preplacement_surface': 'NOT AVAILABLE; no surface-rank test was possible.',
        'holdout': 'NOT INDEPENDENTLY REPLAYED; original shared evaluator and fitted model are absent.',
        'decision': 'DO NOT SUBMIT: final dots exceed the literal registered-lattice overlap stop.',
    }
    return report, zero_mask


def run(input_dir: Path) -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if manifest['schema'] != 'gems-audit-inputs-v1':
        raise ValueError('Unexpected input manifest schema')
    entries = {row['id']: row for row in manifest['inputs']}
    if len(entries) != len(manifest['inputs']) or set(entries) != {*SITE_IDS, 'sample', 'labels', 'lattice', 'KPL36', 'registry_snapshot'}:
        raise ValueError('Witness inventory is incomplete or has duplicate identifiers')
    for row in entries.values():
        check_entry(row)
        path = input_dir / row['local_name']
        if not path.is_file() or sha256(path) != row['sha256']:
            raise ValueError(f"Missing or hash-mismatched input: {row['id']}")
    def path(item):
        return input_dir / entries[item]['local_name']
    sample, sample_mask, grid, sample_meta = read_one(path('sample'))
    footprint = sample_mask & np.isfinite(sample)
    if (sample_meta['dtype'] != 'float32' or str(grid[0]) != 'EPSG:32611'
            or grid[2] != (3730, 3292) or list(grid[1])[:6] != [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0]
            or not footprint.any()):
        raise ValueError('The pinned owner sample does not match the expected audit grid')
    labels, _, labels_grid, labels_meta = read_one(path('labels'))
    if labels_grid != grid:
        raise ValueError('Label mirror grid does not match sample')
    labelled = labels == 1
    sample_ones_equal_labels = bool(np.array_equal(sample == 1, labelled))

    lattice_report, lattice = inspect_raster(path('lattice'), grid, footprint)
    # Bind the mathematical witness to the literal, pinned registry entry, not
    # merely to a similar-looking lattice file.  This snapshot is not complete
    # evidence of the current parallel registry.
    registry = json.loads(path('registry_snapshot').read_text(encoding='utf-8'))
    with rasterio.open(path('lattice')) as src:
        lattice_values = src.read(1)
    registered, lattice_content_sha = validate_registered_witness(
        registry, entries['lattice']['sha256'], lattice_values, footprint)
    del lattice_values
    lattice_halo = coverage(lattice)
    covered_count = int((lattice_halo & footprint).sum())
    bound = placement_bound(int(footprint.sum()), covered_count, 37654)
    kpl_report, kpl = inspect_raster(path('KPL36'), grid, footprint)
    kpl_overlap = overlap(kpl, lattice_halo)

    reports, dots = {}, {}
    for site in SITE_IDS:
        reports[site], dots[site] = inspect_raster(path(site), grid, footprint)
    parallel_report, parallel_dots = inspect_local_research_artifacts(manifest, grid, footprint)
    parallel_report['overlap_with_lattice'] = overlap(parallel_dots, lattice_halo)
    parallel_report['binary_spearman_with_lattice'] = binary_spearman(parallel_dots, lattice, footprint)
    parallel_comparisons = []
    comparisons = []
    for ref in SITE_IDS:
        halo = coverage(dots[ref])
        parallel_comparisons.append({'reference': ref, **overlap(parallel_dots, halo),
                                     'spearman_binary': binary_spearman(parallel_dots, dots[ref], footprint)})
        for site in SITE_IDS:
            if site == ref:
                continue
            result = overlap(dots[site], halo)
            rho = binary_spearman(dots[site], dots[ref], footprint)
            comparisons.append({'candidate': site, 'reference': ref,
                                **result, 'spearman_binary': rho})
    if any(row['fraction'] is None for row in comparisons + parallel_comparisons):
        raise ValueError('Empty witness masks cannot demonstrate uniqueness')
    parallel_report['versus_nine_historical_witnesses'] = parallel_comparisons
    parallel_report['max_historical_overlap_fraction'] = max(row['fraction'] for row in parallel_comparisons)
    parallel_report['historical_overlap_scope'] = 'Only nine witnesses, not the complete registry; passing these does not override the lattice failure.'
    per_site = {}
    for site in SITE_IDS:
        pairs = [r for r in comparisons if r['candidate'] == site]
        closest = max(pairs, key=lambda r: r['fraction'])
        per_site[site] = {'max_overlap_fraction': closest['fraction'],
                          'closest_reference': closest['reference'],
                          'fails_against_at_least_one': any(r['duplicate'] for r in pairs)}
    # Byte-forensic identities only. These do not prove what was uploaded or why it scored as claimed.
    b2_from_25 = dots['GEMSDOE25'] & (distance_transform_edt(~labelled) > 2)
    findings = {
        '25_and_30_identical_in_footprint': bool(np.array_equal(dots['GEMSDOE25'], dots['GEMSDOE30'])),
        '32_minus_31_pixels': int((dots['GEMSDOE32'] & ~dots['GEMSDOE31']).sum()),
        '31_minus_32_pixels': int((dots['GEMSDOE31'] & ~dots['GEMSDOE32']).sum()),
        '32_minus_36_pixels': int((dots['GEMSDOE32'] & ~dots['GEMSDOE36']).sum()),
        '36_minus_32_pixels': int((dots['GEMSDOE36'] & ~dots['GEMSDOE32']).sum()),
        '32_vs_25_minus_visible_catalogue_2px_xor_pixels': int(np.logical_xor(b2_from_25, dots['GEMSDOE32']).sum()),
    }
    return {
        'schema': 'gems-owner-witness-audit-v1',
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Read-only hash-pinned owner mirrors and a concurrent local research artifact; neither organizer receipts nor the complete current registry.',
        'experiment_count': 0,
        'sample': dict(sample_meta, sha256=entries['sample']['sha256'],
                       footprint_pixels=int(footprint.sum()), ones=int((sample == 1).sum()),
                       ones_equal_label_mirror=sample_ones_equal_labels,
                       caveat='Use for grid/footprint only: its ones match known labels, not the advertised absence prediction.'),
        'labels': dict(labels_meta, sha256=entries['labels']['sha256'], ones=int(labelled.sum())),
        'registry_snapshot': {'sha256': entries['registry_snapshot']['sha256'],
                              'entry_count': len(registry['entries']),
                              'scope': 'Pinned GEMSDOE36 owner snapshot; not the complete current registry.'},
        'lattice': dict(lattice_report, within_3px_footprint_pixels=covered_count,
                        registered_id=registered['id'],
                        footprint_sha256=lattice_content_sha,
                        origin='13GEMSDOE calibration raster, pinned as reg-052 in the owner snapshot'),
        'literal_budget_bound': bound,
        'kpl36': dict(kpl_report, overlap_with_lattice=kpl_overlap,
                      surface_check='NOT RUN: the pre-placement surface is unavailable',
                      decision='DO NOT SUBMIT: literal final-dot gate fails; no holdout independently replayed'),
        'parallel_research_artifact': parallel_report,
        'historical_witnesses': reports,
        'historical_nine_pairwise': {'comparisons': comparisons, 'by_site': per_site,
            'minimum_directional_fraction': min(r['fraction'] for r in comparisons),
            'all_72_fail_overlap': all(r['duplicate'] for r in comparisons)},
        'forensics': findings,
        'submission_ready': False,
        'no_public_score_estimate': True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=ROOT / '.local-data' / 'audit')
    parser.add_argument('--output', type=Path, help='Write an atomic JSON report; otherwise print to stdout')
    args = parser.parse_args()
    result = run(args.input_dir)
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        fd, tmpname = tempfile.mkstemp(prefix='.audit-', dir=args.output.parent, text=True)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                stream.write(text)
            os.replace(tmpname, args.output)
        finally:
            Path(tmpname).unlink(missing_ok=True)
        print(f'Wrote {args.output}. This forensic audit does not authorize submissions.')
    else:
        print(text, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
