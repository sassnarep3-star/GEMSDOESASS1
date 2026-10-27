#!/usr/bin/env python3
"""Recheck selected peer candidates against the one decisive registered lattice.

A single duplicate is enough to stop under the literal protocol. This is not a
full-registry pass, pre-placement audit, new model experiment or submission.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy.ndimage import binary_dilation  # noqa: E402
from fetch_audit_inputs import destination, sha256_file  # noqa: E402
from gems_audit.forensics import disk, matching_grid  # noqa: E402
from gems_audit.raster_contract import inspect_raster  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, default=ROOT / ".cache" / "audit-inputs")
    ap.add_argument("--out", type=Path, default=ROOT / "evidence" / "claimed_candidates_audit.json")
    args = ap.parse_args()
    sources = json.loads((ROOT / "registry" / "focus_sources.json").read_text())
    claims = json.loads((ROOT / "registry" / "claimed_candidates.json").read_text())
    needed = [x for x in sources["auxiliary"] if x["id"] in {"sample_template_mirror", "registered_lattice"}]
    try:
        for entry in [*needed, *claims["entries"]]:
            path = destination(entry, args.cache)
            if not path.is_file() or sha256_file(path) != entry["sha256"]:
                raise ValueError(f"Missing or hash-mismatched input: {path}")
        template = args.cache / "sample_template_mirror.tif"
        lattice_path = args.cache / "registered_lattice.tif"
        rows = []
        with rasterio.open(template) as tpl, rasterio.open(lattice_path) as ref:
            if not matching_grid(tpl, ref):
                raise ValueError("Lattice grid differs from template")
            foot = tpl.read_masks(1) > 0
            if not foot.any() or not np.isfinite(tpl.read(1)[foot]).all():
                raise ValueError("Invalid template footprint")
            ref_values = ref.read(1)
            if not (ref.read_masks(1)[foot] > 0).all() or not np.isfinite(ref_values[foot]).all() or not np.all((ref_values[foot] == 0) | (ref_values[foot] == 1)):
                raise ValueError("Lattice contains invalid or masked footprint pixels")
            halo = binary_dilation((ref_values == 1) & foot, structure=disk(3))
            for entry in claims["entries"]:
                path = destination(entry, args.cache)
                with rasterio.open(path) as cand:
                    if not matching_grid(tpl, cand):
                        raise ValueError(f"{entry['id']}: grid differs from template")
                    a = cand.read(1)
                    if not (cand.read_masks(1)[foot] > 0).all() or not np.isfinite(a[foot]).all() or not np.all((a[foot] == 0) | (a[foot] == 1)):
                        raise ValueError(f"{entry['id']}: masked, invalid or non-binary footprint pixels")
                    dots = (a == 1) & foot
                n = int(dots.sum())
                if n == 0:
                    raise ValueError(f"{entry['id']}: no dots")
                overlap = int(np.count_nonzero(dots & halo))
                rows.append({
                    **entry,
                    "dots": n, "dots_within_3px_of_lattice": overlap,
                    "fraction_within_3px_of_lattice": overlap / n,
                    "literal_duplicate_stop": 10 * overlap > 7 * n,
                    "technical_audit": inspect_raster(path, template),
                    "surface_check": "not available; not re-evaluated",
                    "scope": "One known registry entry suffices for a stop; no full-registry pass is claimed.",
                })
        result = {
            "checked_utc": datetime.now(timezone.utc).isoformat(),
            "type": "independent saved-byte peer-candidate forensic recheck; no model experiment",
            "lattice_sha256": next(x["sha256"] for x in needed if x["id"] == "registered_lattice"),
            "template_sha256": next(x["sha256"] for x in needed if x["id"] == "sample_template_mirror"),
            "claims_manifest_sha256": sha256_file(ROOT / "registry" / "claimed_candidates.json"),
            "rows": rows,
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        for row in rows:
            print(f"{row['id']}: {row['dots_within_3px_of_lattice']}/{row['dots']} "
                  f"({row['fraction_within_3px_of_lattice']:.4%}); "
                  f"literal duplicate STOP={row['literal_duplicate_stop']}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Claim audit blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
