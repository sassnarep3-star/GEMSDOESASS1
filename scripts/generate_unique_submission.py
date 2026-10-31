#!/usr/bin/env python3
"""Generate a unique, format-valid GeoTIFF submission using a novel geological hypothesis.

Hypothesis (H-STEP-OVER): uncatalogued geothermal faults concentrate in the step-over/splay
annulus 300-900 m from mapped catalogue faults -- close enough to share the geothermal system,
far enough to not be re-detections of already-mapped scarps. This zone is distinct from:

  * H19-5 family dots (>2 px from catalogue, ML-driven field; overlaps catalogue flank)
  * SWGB dots (>600 m / 6 px from catalogue, HGB-driven; deep far-field)
  * Champion 0.2778 (= dots >2 px from catalogue)

Method:
  1. Load competition grid from sample_submission.tif (CRS, shape, transform, footprint).
  2. Load catalogue from existing_faults.tif (known fault pixels to exclude).
  3. Compute Euclidean distance transform from catalogue pixels.
  4. Select the step-over annulus: 3-9 px (300-900 m) from catalogue faults.
  5. Poisson-disk sample at 3.0 px spacing within the annulus, ~40 000 dots.
  6. Write binary float32 TIF (0/1), zeros outside footprint, no NaN, exact grid match.
  7. Validate with the shared fail-closed writer.
  8. Audit novelty vs available registry rasters (lane-drift gate: rho<=0.90, overlap<=70%).

All numbers are HOLDOUT-DTI proxy measurements or local format checks; no organizer score
is claimed. The output is a research artifact pending a separate selector decision.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems.grid import CRS, SHAPE, TRANSFORM, sha256_file  # noqa: E402
from gems.submission import write_submission  # noqa: E402
from gems.emission import poisson_disk_dots  # noqa: E402

N_DOTS = 40_000
MIN_DIST_PX = 3.0
ANNULUS_INNER_PX = 3.0   # 300 m
ANNULUS_OUTER_PX = 9.0   # 900 m


def load_grid_and_catalogue():
    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as s:
        footprint = np.isfinite(s.read(1))
        profile = dict(crs=str(s.crs), shape=(s.height, s.width),
                       transform=tuple(s.transform)[:6], dtype=s.dtypes[0])
    with rasterio.open(ROOT / "data/bridge/existing_faults.tif") as s:
        catalogue = (s.read(1) == 1) & footprint
    return footprint, catalogue, profile


def build_step_over_field(footprint, catalogue):
    """Binary field: 1 inside the step-over annulus, 0 elsewhere."""
    # Distance from nearest catalogue fault pixel
    dist = ndimage.distance_transform_edt(~catalogue)
    annulus = (dist >= ANNULUS_INNER_PX) & (dist <= ANNULUS_OUTER_PX) & footprint
    return annulus.astype(np.float32)


def main():
    start = time.monotonic()
    footprint, catalogue, profile = load_grid_and_catalogue()
    print(f"grid: {SHAPE} {CRS} footprint={int(footprint.sum())} catalogue={int(catalogue.sum())}",
          flush=True)

    field = build_step_over_field(footprint, catalogue)
    annulus_cells = int((field > 0).sum())
    print(f"step-over annulus cells: {annulus_cells}", flush=True)

    allowed = field > 0
    dots = poisson_disk_dots(field, allowed, N_DOTS, MIN_DIST_PX)
    n_dots = int(dots.sum())
    print(f"emitted dots: {n_dots}", flush=True)

    # Build submission: dots as binary field (1.0 at dot locations, 0 elsewhere)
    submission = np.where(dots, 1.0, 0.0).astype(np.float32)
    submission = np.where(footprint, submission, 0.0)

    # Validation via shared fail-closed writer
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sha8 = hashlib.sha256(submission[footprint].tobytes()).hexdigest()[:8]
    name = f"gemsass1-stepover-{N_DOTS}dots-{stamp}-{sha8}"
    note = (f"GEMSASS1 H-STEP-OVER catalogue-stepover-annulus 300-900m "
            f"{N_DOTS}d 3.0px off-cat; HOLDOUT proxy; see run card")
    assert len(note) <= 140, f"note too long: {len(note)}"

    out_tif = ROOT / "docs/downloads" / f"{name}.tif"
    receipt = write_submission(submission, footprint, out_tif, catalogue=catalogue,
                               note=note,
                               meta=dict(hypothesis="H-STEP-OVER",
                                         annulus_inner_px=ANNULUS_INNER_PX,
                                         annulus_outer_px=ANNULUS_OUTER_PX,
                                         n_dots=n_dots,
                                         min_dist_px=MIN_DIST_PX,
                                         annulus_cells=annulus_cells))
    print(f"wrote {out_tif} sha256={receipt['sha256']} all_checks={receipt['all_checks_passed']}",
          flush=True)

    # Novelty / lane-drift audit vs available registry rasters
    from gems.registry import lane_audit, load_registry
    registry = load_registry()
    print(f"registry rasters loaded: {len(registry)}", flush=True)
    audit = lane_audit(submission, dots, footprint, registry=registry)
    print(f"lane audit: max_spearman={audit['max_spearman']:.4f} "
          f"max_overlap={audit['max_frac_dots_within_3px']:.4f} "
          f"is_duplicate={audit['is_duplicate']}", flush=True)

    card = dict(
        schema_version=1,
        generated_utc=datetime.now(timezone.utc).isoformat(),
        hypothesis="H-STEP-OVER: uncatalogued geothermal faults concentrate in the step-over/splay "
                   "annulus 300-900 m from mapped catalogue faults",
        mechanism="Euclidean distance annulus (3-9 px / 300-900 m) from known catalogue faults; "
                  "Poisson-disk dots at 3.0 px spacing within the annulus; zeros outside footprint.",
        named_non_fault_mimic="Pluvial shoreline benches, fluvial terrace risers, road/canal "
                              "embankments, basaltic vent rims -- linear features that parallel "
                              "mapped faults without being faults.",
        holdout_dti=None,  # Not evaluated: no holdout run for this lane; negative proxy only
        ci95=None,
        withheld_positive_pixels=None,
        evaluator_version="GEMSASS1-HR-v2-segment",
        correlation_overlap_vs_registry=dict(
            max_spearman=audit["max_spearman"],
            max_frac_dots_within_3px=audit["max_frac_dots_within_3px"],
            is_duplicate=audit["is_duplicate"],
            thresholds=dict(spearman=0.90, overlap=0.70, px=3),
            rows=audit["rows"],
        ),
        raster_sha256=receipt["sha256"],
        raster_name=f"{name}.tif",
        validator_output=receipt,
        submission_name=f"{name}.tif",
        note=note,
        note_length=len(note),
        n_dots=n_dots,
        annulus_cells=annulus_cells,
        verdict="promote" if (receipt["all_checks_passed"] and not audit["is_duplicate"]) else "negative",
        approved_for_submission=False,
        submission_slots_used=0,
        data_provenance="Local competition grid (sample_submission.tif) + catalogue "
                        "(existing_faults.tif); not organizer authenticated.",
        limitations=[
            "No organizer submission-page receipt; all historical scores are OWNER-REPORT.",
            "HOLDOUT-DTI not evaluated for this lane; no leaderboard score forecast is made.",
            "Registry coverage partial (300/414 rasters restored; GitHub rate-limited).",
            "Eligibility: official rules limit competitors to US citizens/permanent residents "
            "or US-incorporated entities; confirm with administrator before upload.",
        ],
        experiments_run=1,
        experiment_budget=3,
        max_runtime_seconds=7200,
        elapsed_seconds=time.monotonic() - start,
    )
    out_path = ROOT / "evidence" / f"stepover_run_card_{stamp}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(card, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: card[k] for k in ("verdict", "raster_name", "raster_sha256",
                                           "submission_name", "note_length", "n_dots")},
                     indent=2))
    print(f"run card: {out_path}")


if __name__ == "__main__":
    main()