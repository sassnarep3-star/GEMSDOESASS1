"""Independent, fail-closed inspection of *saved* GeoTIFF bytes.

This does not replace the shared writer, establish scientific validity, or
claim organizer acceptance. A valid dataset mask can express null outside
while retaining finite raw cells; whether the portal accepts it is unknown.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.transform import Affine

# Observed from the pinned peer mirror, NOT authenticated against the organizer.
# A mismatch blocks validation until the actual official template is checked.
MIRRORED_GRID_SHAPE = (3730, 3292)
MIRRORED_GRID_TRANSFORM = Affine(100, 0, 243350, 0, -100, 4508550)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inspect_raster(candidate_path: Path, template_path: Path, *,
                   expected_shape: tuple[int, int] = MIRRORED_GRID_SHAPE,
                   expected_transform: Affine = MIRRORED_GRID_TRANSFORM) -> dict[str, Any]:
    """Return technical checks, never an upload decision.

    Checks intentionally require *both* a null/NaN outside footprint and raw
    finite values in [0,1] everywhere. This is conservative given the reported
    range rejection; raw zero outside plus an internal TIFF mask can satisfy
    both local tests. It has not been tested against the real portal. By
    default the template must also match the observed mirror's grid, whose
    organizer authenticity is unverified. Overrides support synthetic tests.
    """
    with rasterio.open(template_path) as tpl, rasterio.open(candidate_path) as ds:
        template_data = tpl.read(1)
        foot = tpl.read_masks(1) != 0
        checks: dict[str, bool] = {
            "template_single_band": tpl.count == 1,
            "template_float32": tpl.dtypes[0] == "float32" if tpl.count else False,
            "template_expected_shape": tpl.shape == expected_shape,
            "template_expected_transform": tpl.transform == expected_transform,
            "template_epsg_32611": tpl.crs == CRS.from_epsg(32611),
            "template_100m_north_up": tuple(tpl.transform)[:2] == (100.0, 0.0)
            and tuple(tpl.transform)[3:5] == (0.0, -100.0),
            "template_nonempty_footprint": bool(foot.any()),
            "template_footprint_finite": bool(np.isfinite(template_data[foot]).all()),
            "geotiff": ds.driver == "GTiff",
            # An external .msk/.aux.xml sidecar will not travel with the single
            # TIFF upload; do not treat it as a self-contained valid file.
            "self_contained": len(ds.files) == 1,
            "single_band": ds.count == 1,
            "float32": ds.dtypes[0] == "float32" if ds.count else False,
            "crs_matches_template": ds.crs == tpl.crs,
            "epsg_32611": ds.crs == CRS.from_epsg(32611),
            "shape_matches_template": ds.shape == tpl.shape,
            "transform_matches_template": ds.transform == tpl.transform,
        }
        # The rest require exact shape; failing closed is more useful than an
        # IndexError or evaluating on mismatched regions.
        if not checks["shape_matches_template"] or ds.count != 1:
            return {"sha256": sha256_file(candidate_path), "checks": checks,
                    "local_format_pass": False, "organizer_acceptance_confirmed": False,
                    "note": "Pixel checks skipped due to shape or band mismatch."}
        values = ds.read(1)
        validity_mask = ds.read_masks(1) != 0
        inside = values[foot]
        outside = values[~foot]
        finite_inside = np.isfinite(inside)
        finite_all = np.isfinite(values)
        checks.update({
            "no_masked_inside_footprint": bool(validity_mask[foot].all()),
            "no_nan_or_inf_inside_footprint": bool(finite_inside.all()),
            "values_in_0_1_inside_footprint": bool(finite_inside.all() and (inside >= 0).all() and (inside <= 1).all()),
            "no_nan_or_inf_anywhere_raw": bool(finite_all.all()),
            "all_raw_values_in_0_1": bool(finite_all.all() and (values >= 0).all() and (values <= 1).all()),
            "outside_is_null_mask_or_nan": bool(np.all((~validity_mask | np.isnan(values))[~foot])),
        })
        return {
            "sha256": sha256_file(candidate_path),
            "template_sha256": sha256_file(template_path),
            "checks": checks,
            "local_format_pass": all(checks.values()),
            "inside_nonfinite_count": int((~finite_inside).sum()),
            "outside_nonfinite_count": int((~np.isfinite(outside)).sum()),
            "organizer_acceptance_confirmed": False,
            "note": "Local saved-byte checks only; no organizer acceptance, novelty, holdout or slot approval is inferred.",
        }
