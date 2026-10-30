#!/usr/bin/env python3
"""Re-run the literal novelty audit against an ADDITIVE refreshed registry snapshot.

Why: the frozen registry (registry/focus_inventory.json, snapshot 2026-10-27) is pinned and
must not be edited. Since then the nine focus repos have advanced; scripts/registry_refresh.py
--out writes a new manifest (registry/focus_inventory_<date>.json) without touching the frozen one.
This script audits existing candidate rasters (negative artifacts, kept for audit only) against
that refreshed manifest using the shared, unmodified novelty.audit (vendor-backed dot overlap,
exact Spearman, literal 0.90 / 70% / 3 px rules, no saturated-prior exemption).

Positive control: one registry raster is audited against the registry that contains it. It must
be flagged duplicate; otherwise the detector is not trusted and the script fails.

Writes evidence/registry_refresh_<tag>.json. Nothing is uploaded or promoted.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.novelty import audit, centered_ranks, exact_spearman  # noqa: E402
from vendor.gems57.uniqueness import dot_overlap  # noqa: E402

CANDIDATES = {
    'H-PBSC research TIF (negative, holdout-lost)': 'docs/downloads/gemsass1-pbsc-playa-37654dots-20261028T225532Z-87cfb194-zeros.tif',
    'SWGB research TIF (withdrawn, 99.87% lattice overlap)': 'swgb/downloads/gemsass1-swgb-hrv2-44090dots-20261027T122104Z-f9b3f764-zeros.tif',
}


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def summarize(receipt, new_blob_shas):
    rows = receipt['comparisons']
    new_rows = [r for r in rows if r.get('sha256') in new_blob_shas and 'directed_overlap_within_3px' in r]
    best_new = max(new_rows, key=lambda r: r['directed_overlap_within_3px'], default=None)
    top = sorted((r for r in rows if 'directed_overlap_within_3px' in r),
                 key=lambda r: -r['directed_overlap_within_3px'])[:5]
    return dict(
        duplicate=receipt['duplicate'], cleared=receipt['cleared'],
        comparisons_complete=receipt['comparisons_complete'],
        registry_size=receipt['registry_size'], processed=receipt['processed'],
        unassessable=receipt['unassessable'], unique_value_arrays=receipt['unique_value_arrays'],
        max_spearman=receipt['max_spearman'],
        max_directed_overlap_within_3px=receipt['max_directed_overlap_within_3px'],
        new_since_frozen_compared=len(new_rows),
        max_overlap_vs_new_since_frozen=(best_new or {}).get('directed_overlap_within_3px'),
        max_overlap_vs_new_since_frozen_source=(
            {k: best_new[k] for k in ('repo', 'path', 'sha256')} if best_new else None),
        top5_by_overlap=[{k: r.get(k) for k in ('repo', 'path', 'spearman', 'directed_overlap_within_3px', 'duplicate')} for r in top],
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--refreshed', default='registry/focus_inventory_20261030_api.json')
    ap.add_argument('--frozen', default='registry/focus_inventory.json')
    ap.add_argument('--tag', default='20261030')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    refreshed = json.loads((ROOT / args.refreshed).read_text())
    frozen = json.loads((ROOT / args.frozen).read_text())
    if not refreshed.get('complete_within_scope') or refreshed.get('failed'):
        raise SystemExit('refreshed registry incomplete; refusing to audit')
    frozen_shas = {r['sha256'] for r in frozen['rasters']}
    new_blob_shas = {r['sha256'] for r in refreshed['rasters']} - frozen_shas
    frozen_repo_blobs = {(r['repo'], r['blob_sha1']) for r in frozen['rasters']}
    # Two counts, both reported: per-repo blob identities (what the GitHub trees show) and distinct
    # file contents (byte-identical files in two repos count once).
    new_repo_blobs = {(r['repo'], r['blob_sha1']) for r in refreshed['rasters']} - frozen_repo_blobs

    sample = ROOT / 'data/bridge/sample_submission.tif'
    with rasterio.open(sample) as src:
        footprint = np.isfinite(src.read(1))
    root = ROOT

    results = {}
    for label, rel in CANDIDATES.items():
        path = ROOT / rel
        with rasterio.open(path) as src:
            pred = src.read(1).astype(np.float32)
            nan_in_fp = int(np.isnan(pred[footprint]).sum())
            dots = int(((pred > 0) & footprint).sum())
        if nan_in_fp:
            raise SystemExit(f'{rel}: NaN inside footprint; not auditable')
        receipt = audit(pred, footprint, refreshed, root, sample, stage='dots', stop_on_duplicate=False)
        entry = summarize(receipt, new_blob_shas)
        entry.update(path=rel, sha256=sha256_file(path), dots_in_footprint=dots,
                     values_in_0_1=bool(((pred >= 0) & (pred <= 1)).all()))
        results[label] = entry
        print(label, 'duplicate=', entry['duplicate'], 'cleared=', entry['cleared'],
              'max_overlap=', entry['max_directed_overlap_within_3px'], flush=True)

    # Positive control: first refreshed registry raster that is a real prediction (in-footprint dots).
    control_row = None
    for item in refreshed['rasters']:
        with rasterio.open(ROOT / item['local']) as src:
            if src.count == 1 and src.shape == footprint.shape:
                arr = src.read(1)
                # audit() requires a finite candidate everywhere, so the control must be finite across the whole grid.
                if np.isfinite(arr).all() and ((arr > 0) & footprint).sum() > 1000:
                    control_row = (item, arr.astype(np.float32))
                    break
    if control_row is None:
        raise SystemExit('no control raster found')
    item, arr = control_row
    # (a) direct self-match: a raster must match itself. Without this, an audit-level hit could be
    # an earlier, different registry row and would not prove the detector sees a true self-match.
    masked = np.where(footprint, arr, 0)
    self_overlap = dot_overlap(masked, masked)
    ranks, norm = centered_ranks(arr[footprint])
    self_rho = exact_spearman(ranks, norm, arr[footprint])
    if self_overlap is None or self_overlap < 0.999 or self_rho is None or self_rho < 0.999:
        raise SystemExit(f'positive control failed self-match: overlap={self_overlap} rho={self_rho}')
    # (b) audit-level detection on the same registry, reporting which row triggered it.
    control_receipt = audit(arr, footprint, refreshed, root, sample, stage='dots', stop_on_duplicate=True)
    if not control_receipt['duplicate']:
        raise SystemExit('positive control failed: audit did not flag a registry raster against the registry')
    first_hit = next(r for r in control_receipt['comparisons'] if r.get('duplicate'))
    control = dict(
        path=f"{item['repo']}/{item['path']}",
        self_match_directed_overlap_within_3px=float(self_overlap),
        self_match_spearman=float(self_rho),
        audit_duplicate_detected=True,
        first_audit_hit=dict(repo=first_hit['repo'], path=first_hit['path'],
                             is_control_itself=first_hit['sha256'] == item['sha256']),
    )
    print('positive control self-match overlap', self_overlap, 'rho', self_rho,
          'first audit hit', control['first_audit_hit'], flush=True)

    out = dict(
        schema='registry-refresh-audit-v1',
        tag=args.tag,
        purpose='Additive re-check of existing negative candidates against refreshed registry; no promotion, no upload, no slot.',
        frozen_manifest=dict(path=args.frozen, sha256=sha256_file(ROOT / args.frozen),
                             snapshot_utc=frozen['snapshot_utc'], rasters=len(frozen['rasters']),
                             refs=frozen['refs']),
        refreshed_manifest=dict(path=args.refreshed, sha256=sha256_file(ROOT / args.refreshed),
                                snapshot_utc=refreshed['snapshot_utc'], rasters=len(refreshed['rasters']),
                                failed=refreshed['failed'], refs=refreshed['refs']),
        new_registry_repo_blobs_since_frozen=len(new_repo_blobs),
        new_registry_distinct_contents_since_frozen=len(new_blob_shas),
        footprint=dict(source='data/bridge/sample_submission.tif', cells=int(footprint.sum()),
                       rule='np.isfinite(sample)'),
        thresholds=dict(rank_corr_max=0.90, dot_overlap_max=0.70, overlap_px=3, dot_rule='prediction > 0 within footprint'),
        positive_control=control,
        candidates=results,
        verdict='no candidate cleared' if all(not v['cleared'] for v in results.values()) else 'see per-candidate cleared flags',
    )
    out_path = ROOT / (args.out or f'evidence/registry_refresh_{args.tag}.json')
    if out_path.exists():
        raise SystemExit(f'refusing to overwrite {out_path.relative_to(ROOT)}')
    out_path.write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
    print('wrote', out_path.relative_to(ROOT))


if __name__ == '__main__':
    main()
