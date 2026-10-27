#!/usr/bin/env python3
"""Check two already-tracked parallel-run TIFF variants; never authorize upload."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from gems_audit.forensics import matching_grid  # noqa: E402
from gems_audit.raster_contract import inspect_raster, sha256_file  # noqa: E402

STEM = "gemsdoesass1-hybrid-blindpiedmont-dispersed-37654-20261027T113459Z-cbceb1d0"
PINS = {
    "zero": "50b1350dd92cde3af8bd85f13f39f7feb8c82416f095df281cd8c5291dbb1274",
    "nan": "ddd12d0d3e3f94dee8b85a5df3c6bb6509e6a3d7c6ea83e78e8afa293ead1189",
    "template": "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc",
}


def main() -> int:
    paths = {
        "zero": ROOT / "docs" / "downloads" / f"{STEM}-zeros.tif",
        "nan": ROOT / "docs" / "downloads" / f"{STEM}-nan.tif",
        "template": ROOT / ".cache" / "audit-inputs" / "sample_template_mirror.tif",
    }
    try:
        for label, path in paths.items():
            if sha256_file(path) != PINS[label]:
                raise ValueError(f"{label} hash differs from the recorded bytes")
        with rasterio.open(paths["template"]) as template, rasterio.open(paths["zero"]) as zero, rasterio.open(paths["nan"]) as nan:
            if not matching_grid(template, zero) or not matching_grid(template, nan):
                raise ValueError("Variant grids differ from the reference")
            foot = template.read_masks(1) > 0
            a, b = zero.read(1), nan.read(1)
            if not foot.any() or not np.isfinite(a[foot]).all() or not np.isfinite(b[foot]).all():
                raise ValueError("Invalid inside-footprint values")
            equal = bool(np.array_equal(a[foot], b[foot]))
            result = {
                "checked_utc": datetime.now(timezone.utc).isoformat(),
                "scope": "Previously merged synthetic research raster, not generated in this run; no organizer acceptance or score inferred.",
                "source_pr": "https://github.com/sassnarep3-star/GEMSDOESASS1/pull/3",
                "same_inside_footprint_values": equal,
                "inside_footprint_positive_pixels": int(np.count_nonzero(a[foot] > 0)),
                "zero": inspect_raster(paths["zero"], paths["template"]),
                "nan": inspect_raster(paths["nan"], paths["template"]),
                "literal_lattice_check": "See claimed_candidates_audit.json for the zero variant; equal inside values imply the same dots for the NaN variant if same_inside_footprint_values is true.",
                "ok_to_submit": False,
            }
        out = ROOT / "evidence" / "parallel_variant_audit.json"
        out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(f"Same inside-footprint values: {equal}; both variants remain research-only.")
        return 0 if equal else 1
    except (OSError, ValueError) as exc:
        print(f"Variant check blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
