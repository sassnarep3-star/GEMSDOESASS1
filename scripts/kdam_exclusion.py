#!/usr/bin/env python3
"""Turn a novelty scan into the frozen exclusion mask used for the shipped emission.

Rule (declared before the constrained file was emitted, `knowledge/hypotheses_20261031.md`):
a dot of the shipped candidate may not lie within 4 px of any positive pixel of a registry raster
that the *unconstrained* candidate exceeded 70 % 3 px overlap with. 4 px, not 3 px, because the
protocol test uses "within 3 px" and a dot at exactly 3.0 px must not be a coin flip.

Synthetic calibration fixtures are never imported here: `novelty_scan.py` already excluded them.

Usage: python scripts/kdam_exclusion.py <novelty.json>
Writes: work/kdam/exclusion.npy and evidence/kdam/exclusion_mask.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.gems.grid import read_band  # noqa: E402

WORK = ROOT / "work/kdam"
EV = ROOT / "evidence/kdam"
INVENTORY = ROOT / "registry/focus_inventory_20261030.json"
RADIUS_PX = 4.0


def main() -> int:
    scan = json.loads(Path(sys.argv[1]).read_text())
    offenders = scan["duplicates"]
    if not offenders:
        mask = np.zeros((3730, 3292), bool)
        print("no offenders: empty exclusion mask")
    else:
        inv = {r["path"]: r["local"] for r in json.loads(INVENTORY.read_text())["rasters"]}
        union = np.zeros((3730, 3292), bool)
        for row in offenders:
            a = read_band(ROOT / inv[row["path"]])
            union |= np.nan_to_num(a, nan=0.0) > 0.0
            del a
        mask = ndimage.distance_transform_edt(~union) <= RADIUS_PX
    WORK.mkdir(parents=True, exist_ok=True)
    np.save(WORK / "exclusion.npy", mask)
    out = dict(source_scan=str(Path(sys.argv[1]).resolve().relative_to(ROOT)),
               rule=f"exclude <= {RADIUS_PX} px from the dots of every registry raster whose 3 px overlap "
                    f"with the unconstrained candidate exceeded {scan['thresholds']['overlap_limit']}",
               offenders=[dict(repo=r["repo"], path=r["path"], overlap3=r["overlap3"]) for r in offenders],
               masked_pixels=int(mask.sum()), footprint_cells=5167373,
               masked_fraction_of_footprint=float(mask.sum() / 5167373),
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    EV.mkdir(parents=True, exist_ok=True)
    (EV / "exclusion_mask.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: out[k] for k in ("offenders", "masked_pixels", "masked_fraction_of_footprint")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
