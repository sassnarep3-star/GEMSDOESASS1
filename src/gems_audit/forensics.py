"""Reproducible historical-mask and literal-registry feasibility checks.

These are diagnostics, not a candidate generator or an organizer validator.
The nine historical TIFFs are an explicitly limited subset of the registry.
"""
from __future__ import annotations

from math import isfinite, sqrt
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation


def disk(radius: int) -> np.ndarray:
    if not isinstance(radius, int) or radius < 0:
        raise ValueError("radius must be a nonnegative integer")
    y, x = np.ogrid[-radius : radius + 1, -radius : radius + 1]
    return x * x + y * y <= radius * radius


def forced_overlap(total: int, covered: int, dots: int) -> dict[str, Any]:
    """Conservative 3-pixel overlap lower bound in a finite footprint.

    We use integer arithmetic for the user's *strictly greater than* 70% stop.
    A zero-dot candidate has no meaningful overlap and is deliberately invalid.
    """
    if any(isinstance(x, bool) or not isinstance(x, int) for x in (total, covered, dots)):
        raise ValueError("counts must be integers")
    if total <= 0 or not 0 <= covered <= total or not 1 <= dots <= total:
        raise ValueError("counts must describe a nonempty candidate in the footprint")
    uncovered = total - covered
    at_least = max(0, dots - uncovered)
    first_blocked = (10 * uncovered) // 3 + 1
    return {
        "footprint_pixels": total,
        "covered_pixels": covered,
        "uncovered_pixels": uncovered,
        "candidate_dots": dots,
        "minimum_overlapping_dots": at_least,
        "minimum_overlap_fraction": at_least / dots,
        "overlap_limit_fraction": 0.7,
        "proven_duplicate_stop": 10 * at_least > 7 * dots,
        "first_count_forced_above_limit": first_blocked if first_blocked <= total else None,
        "interpretation": "A proven stop is decisive for this reference. A no-proof result is not a uniqueness pass.",
    }


def binary_spearman(a: np.ndarray, b: np.ndarray, foot: np.ndarray) -> float | None:
    """Exact Spearman for two binary variables on the footprint; None if constant."""
    n = int(np.count_nonzero(foot))
    na = int(np.count_nonzero(a & foot))
    nb = int(np.count_nonzero(b & foot))
    if not n or na in (0, n) or nb in (0, n):
        return None
    both = int(np.count_nonzero(a & b & foot))
    return (n * both - na * nb) / sqrt(na * (n - na) * nb * (n - nb))


def duplicate_stop(overlap: float, rho: float | None) -> bool:
    """Strict literal thresholds; unmeasurable comparisons fail closed."""
    if not isfinite(overlap) or not 0 <= overlap <= 1 or rho is None or not isfinite(rho):
        return True
    return overlap > 0.7 or rho > 0.9


def matching_grid(a: rasterio.io.DatasetReader, b: rasterio.io.DatasetReader) -> bool:
    return (
        a.count == b.count == 1
        and a.height == b.height
        and a.width == b.width
        and a.crs == b.crs
        and a.transform == b.transform
    )


def _positive_binary(ds: rasterio.io.DatasetReader, foot: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    data = ds.read(1)
    valid = np.isfinite(data) & (ds.read_masks(1) > 0)
    inside = data[foot]
    if not np.all(valid[foot]):
        raise ValueError(f"{ds.name}: invalid, masked or non-finite pixel inside footprint")
    if not np.all((inside == 0) | (inside == 1)):
        raise ValueError(f"{ds.name}: historical reference is not binary inside footprint")
    # np.nan outside the footprint is allowed for historical comparison, not
    # silently considered part of the footprint or part of the candidate.
    support = (data == 1) & foot
    info = {
        "dots": int(support.sum()),
        "dtype": ds.dtypes[0],
        "nodata": "NaN" if ds.nodata is not None and np.isnan(ds.nodata) else ds.nodata,
        "finite_inside": int(np.isfinite(inside).sum()),
        "whole_array_finite": bool(np.isfinite(data).all()),
        "whole_array_in_0_1": bool(np.isfinite(data).all() and (data >= 0).all() and (data <= 1).all()),
        "outside_masked_or_nan": bool(np.all(((ds.read_masks(1) == 0) | np.isnan(data))[~foot])),
    }
    return support, info


def audit(cache: Path, sources: dict, dots: int = 37654) -> dict[str, Any]:
    """Audit pinned local bytes after the caller verifies their SHA-256 hashes."""
    template_path = cache / "sample_template_mirror.tif"
    with rasterio.open(template_path) as template:
        sample = template.read(1)
        foot = template.read_masks(1) > 0
        if template.count != 1 or template.dtypes[0] != "float32" or template.crs is None:
            raise ValueError("Template is not a single-band georeferenced float32 raster")
        if not foot.any() or not np.isfinite(sample[foot]).all():
            raise ValueError("Invalid template footprint")
        template_info = {
            "shape_rows_cols": [template.height, template.width],
            "crs": str(template.crs),
            "transform": list(template.transform)[:6],
            "nodata": "NaN" if template.nodata is not None and np.isnan(template.nodata) else template.nodata,
            "footprint_pixels": int(foot.sum()),
            "positive_pixels": int(np.count_nonzero(sample[foot] > 0)),
        }
        with rasterio.open(cache / "labels_mirror.tif") as labels:
            if not matching_grid(template, labels):
                raise ValueError("Labels and template grids differ")
            lab_data = labels.read(1)
            label_valid = labels.read_masks(1) > 0
            if not np.array_equal(label_valid, foot):
                raise ValueError("Label and sample footprints differ")
            if not np.all((lab_data[foot] == 0) | (lab_data[foot] == 1)):
                raise ValueError("Labels are not binary inside footprint")
            label_mask = (lab_data == 1) & foot
            template_info["label_positive_pixels"] = int(label_mask.sum())
            template_info["sample_positive_mask_equals_labels"] = bool(np.array_equal((sample == 1) & foot, label_mask))
        with rasterio.open(cache / "registered_lattice.tif") as lattice_ds:
            if not matching_grid(template, lattice_ds):
                raise ValueError("Registered lattice and template grids differ")
            lattice, lattice_info = _positive_binary(lattice_ds, foot)
        halo = binary_dilation(lattice, structure=disk(3))
        covered = int(np.count_nonzero(halo & foot))
        bound = forced_overlap(int(foot.sum()), covered, dots)

        masks: dict[str, np.ndarray] = {}
        site_info: dict[str, dict] = {}
        for row in sources["sources"]:
            site = row["site"]
            with rasterio.open(cache / f"{site}.tif") as ds:
                if not matching_grid(template, ds):
                    raise ValueError(f"{site}: grid does not match template")
                mask, info = _positive_binary(ds, foot)
            if not mask.any():
                raise ValueError(f"{site}: constant or empty support")
            masks[site] = mask
            site_info[site] = {**info, "sha256": row["sha256"], "source": row["source"],
                               "user_reported_value": row["reported_value"],
                               "evidence_class": row["report_class"]}

    comparisons = []
    for reference, ref_mask in masks.items():
        near_ref = binary_dilation(ref_mask, structure=disk(3))
        for candidate, candidate_mask in masks.items():
            if candidate == reference:
                continue
            cand_count = site_info[candidate]["dots"]
            overlap = int(np.count_nonzero(candidate_mask & near_ref)) / cand_count
            rho = binary_spearman(candidate_mask, ref_mask, foot)
            comparisons.append({
                "candidate": candidate, "reference": reference,
                "candidate_fraction_within_3px": overlap,
                "binary_spearman": rho,
                "exact_same_mask": bool(np.array_equal(candidate_mask, ref_mask)),
                "duplicate_stop": duplicate_stop(overlap, rho),
            })
    for site in site_info:
        related = [r for r in comparisons if r["candidate"] == site]
        worst = max(related, key=lambda r: r["candidate_fraction_within_3px"])
        site_info[site]["worst_fraction_within_3px"] = worst["candidate_fraction_within_3px"]
        site_info[site]["worst_reference"] = worst["reference"]
        site_info[site]["duplicate_vs_any_other_of_nine"] = any(r["duplicate_stop"] for r in related)
        site_info[site]["same_mask_sites"] = [r["reference"] for r in related if r["exact_same_mask"]]

    champ = masks["GEMSDOE32"]
    parent = masks["GEMSDOE25"]
    solo = masks["GEMSDOE31"]
    anderson = masks["GEMSDOE36"]
    label_near_2px = binary_dilation(label_mask, structure=disk(2))
    family = {
        "d28_25_and_30_symmetric_difference": int(np.count_nonzero(parent ^ masks["GEMSDOE30"])),
        "b2_vs_parent_excluding_label_radius_2_symmetric_difference": int(np.count_nonzero(champ ^ (parent & ~label_near_2px))),
        "b2_extra_vs_solo": int(np.count_nonzero(champ & ~solo)),
        "solo_extra_vs_b2": int(np.count_nonzero(solo & ~champ)),
        "b2_missing_from_anderson": int(np.count_nonzero(champ & ~anderson)),
        "anderson_extra_vs_b2": int(np.count_nonzero(anderson & ~champ)),
    }
    return {
        "schema_version": 1,
        "audit_type": "forensics only; no geological experiment, candidate raster, holdout or submission",
        "input_provenance": "SHA-256 pinned owner mirrors, not organizer-authenticated. Hashes prove byte consistency only.",
        "limitations": [
            "Nine historical TIFFs only, not all current or unpublished registry rasters.",
            "These are final binary masks, not their pre-placement surfaces.",
            "User-reported leaderboard values are not bound to submitted bytes by organizer receipts.",
            "Sample mirror contradicts organizer page's description of a zero-prediction sample.",
            "Whole-array range compliance does not establish portal acceptance or official outside-footprint compliance.",
        ],
        "template": template_info,
        "lattice": {"sha256": sources["auxiliary"][2]["sha256"], "dots": lattice_info["dots"], **bound},
        "site_summary": site_info,
        "directional_pairwise_checks": comparisons,
        "family_forensics": family,
    }
