"""Literal protocol checks, exact over all footprint pixels. No saturated-prior exemption."""
import hashlib
from pathlib import Path
import numpy as np
import rasterio
from scipy.stats import rankdata
from vendor.gems57.uniqueness import dot_overlap


def canonical_hash(a):
    return hashlib.sha256(np.asarray(a, dtype='<f4').tobytes()).hexdigest()


def centered_ranks(a):
    r = rankdata(a).astype(np.float64)
    r -= r.mean()
    return r, float(np.linalg.norm(r))


def exact_spearman(centered, norm, b):
    if norm == 0 or np.ptp(b) == 0:
        return None
    lo, hi = float(b.min()), float(b.max())
    high = b == hi
    if np.all(high | (b == lo)):
        n1, n = int(high.sum()), b.size
        return float(centered[high].sum() / (norm * np.sqrt(n1 * (n - n1) / n)))
    r, n = centered_ranks(b)
    return float(np.dot(centered, r) / (norm * n)) if n else None


def audit(prediction, footprint, inventory, root, reference, *, stage, stop_on_duplicate=True):
    if stage not in ('surface', 'dots'):
        raise ValueError('unknown novelty stage')
    if not inventory.get('complete_within_scope') or inventory.get('failed'):
        raise ValueError('incomplete registry; cannot grant novelty clearance')
    p = np.asarray(prediction)
    if p.shape != footprint.shape or not np.isfinite(p).all():
        raise ValueError('nonfinite or misaligned candidate')
    v = p[footprint]
    ranks, norm = centered_ranks(v)
    digest = canonical_hash(v)
    dots = (p > 0) & footprint
    count = int(dots.sum())
    if stage == 'dots' and not count:
        raise ValueError('empty dots cannot be cleared')
    rows, seen = [], {}
    duplicate = False
    unassessable = 0
    with rasterio.open(reference) as ref:
        shape, crs, transform = ref.shape, ref.crs, ref.transform
    for index, item in enumerate(inventory['rasters']):
        path = Path(root) / item['local']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('registry cache changed: ' + str(path))
        row = {k: item[k] for k in ('repo', 'ref', 'path', 'sha256')}
        with rasterio.open(path) as src:
            if src.count != 1 or src.shape != shape or src.crs != crs or src.transform != transform:
                row.update(status='incompatible-grid-or-bands', shape=list(src.shape), bands=src.count)
                rows.append(row)
                continue
            old = src.read(1)
        values = old[footprint]
        if not np.isfinite(values).all():
            row.update(status='unassessable-nonfinite-inside-footprint')
            unassessable += 1
            rows.append(row)
            continue
        prior_hash = canonical_hash(values)
        if prior_hash in seen:
            measured = dict(seen[prior_hash])
        else:
            rho = exact_spearman(ranks, norm, values)
            # The inherited literal support rule applies in BOTH phases. A
            # continuous surface's positive pixels are not exempt from overlap.
            # Delegate geometry to the unmodified shared template implementation.
            overlap = dot_overlap(np.where(footprint, p, 0), np.where(footprint, old, 0))
            measured = dict(spearman=rho, directed_overlap_within_3px=overlap,
                            canonical_values_sha256=prior_hash,
                            exact_values_equal=prior_hash == digest,
                            duplicate=(rho is not None and rho > .90) or (overlap is not None and overlap > .70))
            seen[prior_hash] = measured
        row.update(measured, status='compared')
        rows.append(row)
        if measured['duplicate']:
            duplicate = True
            if stop_on_duplicate:
                break
        if (index + 1) % 50 == 0:
            print(f'novelty {stage}: {index + 1}/{len(inventory["rasters"])}', flush=True)
    correlations = [r['spearman'] for r in rows if r.get('spearman') is not None]
    overlaps = [r['directed_overlap_within_3px'] for r in rows if r.get('directed_overlap_within_3px') is not None]
    compared = sum(r['status'] == 'compared' for r in rows)
    complete = len(rows) == len(inventory['rasters']) and not unassessable and compared > 0
    return dict(stage=stage, duplicate=duplicate,
                cleared=complete and not duplicate and norm > 0 and count > 0,
                comparisons_complete=complete, registry_scope=inventory['scope'],
                registry_size=len(inventory['rasters']), processed=len(rows), unique_value_arrays=len(seen),
                unassessable=unassessable, max_spearman=max(correlations, default=None),
                max_directed_overlap_within_3px=max(overlaps, default=None),
                candidate_values_sha256=digest, comparison_method='exact all-footprint ranks; positive support >0, no density exemptions',
                comparisons=rows)
