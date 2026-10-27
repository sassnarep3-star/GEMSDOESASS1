#!/usr/bin/env python3
"""Recheck exact pinned bytes, historical mask relationships, and the lattice bound."""
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
import scipy  # noqa: E402
from gems_audit.forensics import audit  # noqa: E402
from fetch_audit_inputs import destination, sha256_file  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, default=ROOT / ".cache" / "audit-inputs")
    ap.add_argument("--out", type=Path, default=ROOT / "evidence" / "focus_audit.json")
    ap.add_argument("--dots", type=int, default=37654, help="Budget for the literal lattice feasibility bound")
    args = ap.parse_args()
    man_path = ROOT / "registry" / "focus_sources.json"
    sources = json.loads(man_path.read_text())
    try:
        for entry in [*sources["sources"], *sources["auxiliary"]]:
            path = destination(entry, args.cache)
            if not path.is_file():
                raise FileNotFoundError(f"{path} absent; run scripts/fetch_audit_inputs.py first")
            actual = sha256_file(path)
            if actual != entry["sha256"]:
                raise ValueError(f"SHA-256 mismatch for {path.name}: {actual}")
        result = audit(args.cache, sources, args.dots)
        result["checked_utc"] = datetime.now(timezone.utc).isoformat()
        result["source_manifest_sha256"] = sha256_file(man_path)
        result["dependencies"] = {"numpy": np.__version__, "scipy": scipy.__version__, "rasterio": rasterio.__version__}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"out": str(args.out), "template": result["template"],
                          "lattice": result["lattice"], "family": result["family_forensics"],
                          "pairwise_checks": len(result["directional_pairwise_checks"])}, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"Audit blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
