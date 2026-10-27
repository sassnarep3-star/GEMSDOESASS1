"""Competition grid constants and raster IO.

Grid verified from `data/bridge/sample_submission.tif` (sha256 2176d08e…) which mirrors the
organizer template: EPSG:32611, 3730 rows x 3292 cols, 100 m pixels,
transform (100, 0, 243350, 0, -100, 4508550). Footprint = finite pixels of the template
(5,167,373 px); everything else is NaN in the template.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
BRIDGE = DATA / "bridge"
FEATURES = DATA / "features"
REGISTRY = DATA / "registry"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"
WORK = ROOT / "work"

CRS = "EPSG:32611"
SHAPE = (3730, 3292)
TRANSFORM = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
PIXEL_M = 100.0


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_band(p: Path, band: int = 1) -> np.ndarray:
    with rasterio.open(p) as s:
        return s.read(band)


def read_profile(p: Path) -> dict:
    with rasterio.open(p) as s:
        return dict(crs=str(s.crs), shape=(s.height, s.width), transform=tuple(s.transform)[:6],
                    dtype=s.dtypes[0], nodata=s.nodata, count=s.count)


def load_footprint() -> np.ndarray:
    return np.isfinite(read_band(BRIDGE / "sample_submission.tif"))


def load_catalogue() -> np.ndarray:
    """Known USGS/INGENIOUS fault pixels (existing_faults.tif, int8: 1 fault, 0 none, -1 nodata)."""
    return read_band(BRIDGE / "existing_faults.tif") == 1


def load_u8_stack(name: str):
    """Return (array[bands,H,W] uint8, channel names, sidecar json). 0 == nodata in all stacks."""
    p = FEATURES / f"{name}_u8.tif"
    meta = json.loads((FEATURES / f"{name}.json").read_text())
    with rasterio.open(p) as s:
        arr = s.read()
    names = meta.get("channels") or meta.get("bands")
    return arr, list(names), meta


def binary_dots(p: Path) -> np.ndarray:
    a = read_band(p)
    return np.nan_to_num(a, nan=0.0) > 0.5
