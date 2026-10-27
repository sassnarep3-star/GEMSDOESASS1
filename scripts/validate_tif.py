#!/usr/bin/env python3
"""Check an existing saved TIFF against a template; never authorize a slot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems_audit.raster_contract import inspect_raster  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidate", type=Path)
    ap.add_argument("template", type=Path)
    ap.add_argument("--out", type=Path, help="Optional path for the independent technical receipt")
    args = ap.parse_args()
    try:
        result = inspect_raster(args.candidate, args.template)
    except Exception as exc:
        result = {"local_format_pass": False, "error": str(exc),
                  "organizer_acceptance_confirmed": False}
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    print(text, end="")
    return 0 if result["local_format_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
