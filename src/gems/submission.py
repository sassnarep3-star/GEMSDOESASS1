"""Submission writer + validator.

Submission format (official, https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
"Submission format"): a single-band GeoTIFF matching the template's CRS, shape and geotransform
with predicted values in [0, 1]. The organizer's upload form rejects files whose values are
outside [0, 1] ("Predicted values must be in range [0, 1]") — a NaN written outside the footprint
has been accepted historically by sibling sites ("-nan" files), but the safest file is the
"-zeros" variant: zeros everywhere outside the footprint, never a NaN, never an Inf, float32.

`validate()` is the automatic gate; `write_submission()` refuses to write a failing raster.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio

from .grid import CRS, SHAPE, TRANSFORM, read_band, sha256_file, BRIDGE


def validate(path: Path, footprint: np.ndarray, catalogue: np.ndarray | None = None) -> dict:
    with rasterio.open(path) as s:
        a = s.read(1)
        prof = dict(crs=str(s.crs), shape=(s.height, s.width), transform=tuple(s.transform)[:6],
                    dtype=s.dtypes[0], count=s.count, nodata=s.nodata)
    tmpl = BRIDGE / "sample_submission.tif"
    with rasterio.open(tmpl) as t:
        tprof = dict(crs=str(t.crs), shape=(t.height, t.width), transform=tuple(t.transform)[:6])
    fin = np.isfinite(a)
    inside = a[footprint]
    checks = {
        "single_band": prof["count"] == 1,
        "dtype_float32": prof["dtype"] == "float32",
        "crs_matches_template": prof["crs"] == tprof["crs"] == CRS,
        "shape_matches_template": tuple(prof["shape"]) == tuple(tprof["shape"]) == SHAPE,
        "transform_matches_template": np.allclose(prof["transform"], tprof["transform"]) and np.allclose(prof["transform"], tuple(TRANSFORM)[:6]),
        "no_nan_inside_footprint": bool(np.isfinite(inside).all()),
        "no_nan_anywhere": bool(fin.all()),
        "values_in_0_1_everywhere": bool(fin.all() and a.min() >= 0.0 and a.max() <= 1.0),
        "values_in_0_1_inside_footprint": bool(np.isfinite(inside).all() and inside.min() >= 0.0 and inside.max() <= 1.0),
        "no_positive_outside_footprint": bool(np.nan_to_num(a[~footprint]).max() <= 0.0) if (~footprint).any() else True,
    }
    if catalogue is not None:
        checks["zero_mass_on_known_catalogue_pixels"] = bool((a[catalogue] > 0).sum() == 0)
    stats = dict(positive_pixels=int((np.nan_to_num(a) > 0).sum()), footprint_pixels=int(footprint.sum()),
                 min=float(np.nanmin(a)), max=float(np.nanmax(a)), sha256=sha256_file(path),
                 size_bytes=path.stat().st_size, profile=prof)
    return dict(path=str(path), checks=checks, all_checks_passed=all(checks.values()), **stats)


def write_submission(mask_or_field: np.ndarray, footprint: np.ndarray, out_tif: Path,
                     catalogue: np.ndarray | None = None, note: str = "", meta: dict | None = None) -> dict:
    a = np.asarray(mask_or_field, dtype=np.float32)
    a = np.where(footprint, np.clip(a, 0.0, 1.0), 0.0).astype(np.float32)   # zeros outside; never NaN
    out_tif.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_tif, "w", driver="GTiff", height=SHAPE[0], width=SHAPE[1], count=1,
                       dtype="float32", crs=CRS, transform=TRANSFORM, compress="deflate",
                       tiled=True, blockxsize=256, blockysize=256) as dst:
        dst.write(a, 1)
    rep = validate(out_tif, footprint, catalogue)
    if not rep["all_checks_passed"]:
        out_tif.unlink(missing_ok=True)
        raise RuntimeError(f"validator failed: {rep['checks']}")
    zip_path = out_tif.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(out_tif, arcname=out_tif.name)
    rep["zip"] = dict(path=str(zip_path), sha256=sha256_file(zip_path), size_bytes=zip_path.stat().st_size)
    if len(note) > 140:
        raise ValueError("submission note must be <= 140 characters")
    rep["submission_note"] = note
    rep["meta"] = meta or {}
    out_tif.with_suffix(".checks.json").write_text(json.dumps(rep, indent=2))
    return rep
