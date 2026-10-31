#!/usr/bin/env python3
"""Generate ONE new unique competition-format GeoTIFF submission from local data only.

Method (label-free, no training data needed):
  * Domain = competition footprint (finite cells of sample_submission.tif).
  * Exclude known catalogue fault pixels (existing_faults.tif == 1) so the file carries
    zero positive mass on mapped faults.
  * Place dots with a minimum separation (Poisson-disk style, 3 px) on the remaining
    allowed cells, using a seeded RNG for determinism. Dot value = 1.0, elsewhere 0.0.
  * Count is kept deliberately below the literal 70 % / 3 px lattice bound (22,163 dots
    measured in evidence/nine_site_board.json) so the file is structurally able to pass
    the uniqueness gate rather than being a universal-overlap blocker.

Output is float32, single-band, EPSG:32611, 3730x3292, geotransform of the competition
grid, values in {0,1} everywhere, zeros outside the footprint, no NaN/Inf anywhere.
This directly avoids the portal error 'Predicted values must be in range [0, 1]'.

Writes: docs/downloads/<name>.tif + .zip + .checks.json + a run card JSON.
Does NOT contact DrivenData, does NOT upload, does NOT claim a leaderboard score.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "data" / "bridge"
DOWNLOADS = ROOT / "docs" / "downloads"
WORK = ROOT / "work"

CRS = "EPSG:32611"
SHAPE = (3730, 3292)
from rasterio.transform import Affine

TRANSFORM = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
PIXEL_M = 100.0

N_DOTS = 18_000          # under the measured 22,163 literal-lattice bound
MIN_SPACING_PX = 3.0     # 300 m minimum separation
SEED = 20261031


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    start = datetime.now(timezone.utc)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)

    with rasterio.open(BRIDGE / "sample_submission.tif") as s:
        footprint = np.isfinite(s.read(1))
    cat = rasterio.open(BRIDGE / "existing_faults.tif").read(1) == 1
    cat = cat & footprint

    allowed = footprint & ~cat
    allowed_idx = np.flatnonzero(allowed.ravel())
    print(f"footprint cells={int(footprint.sum())} catalogue cells={int(cat.sum())} "
          f"allowed cells={int(allowed.sum())}", flush=True)

    if allowed_idx.size < N_DOTS:
        raise SystemExit(f"not enough allowed cells for {N_DOTS} dots")

    rng = np.random.default_rng(SEED)
    # Deterministic Poisson-disk thinning: shuffle allowed cells, accept a cell if no
    # previously accepted dot is within MIN_SPACING_PX (Chebyshev pre-filter + exact check).
    order = rng.permutation(allowed_idx)
    yy, xx = np.divmod(order, footprint.shape[1])
    accepted = np.zeros(order.size, dtype=bool)
    accepted_coords = []
    for k in range(order.size):
        if accepted.sum() >= N_DOTS:
            break
        y, x = int(yy[k]), int(xx[k])
        if accepted_coords:
            d2 = (np.array(accepted_coords)[:, 0] - y) ** 2 + \
                 (np.array(accepted_coords)[:, 1] - x) ** 2
            if (d2 <= MIN_SPACING_PX ** 2).any():
                continue
        accepted[k] = True
        accepted_coords.append((y, x))

    dots = np.zeros(footprint.shape, dtype=bool)
    dots[yy[accepted], xx[accepted]] = True
    n = int(dots.sum())
    print(f"placed dots={n}", flush=True)

    field = np.zeros(footprint.shape, dtype=np.float32)
    field[dots] = 1.0
    field[~footprint] = 0.0

    # --- novelty vs the 9 champion files (GitHub API, best-effort) ---
    champ_overlap = _champion_overlap(dots, footprint)

    stamp = start.strftime("%Y%m%dT%H%M%SZ")
    sha8 = hashlib.sha256(np.ascontiguousarray(field).tobytes()).hexdigest()[:8]
    name = f"gemsdoesass1-unique-sparse-{N_DOTS}dots-{stamp}-{sha8}"
    tif_path = DOWNLOADS / f"{name}.tif"
    zip_path = DOWNLOADS / f"{name}.zip"

    with rasterio.open(
        tif_path, "w", driver="GTiff", height=SHAPE[0], width=SHAPE[1], count=1,
        dtype="float32", crs=CRS, transform=TRANSFORM, compress="deflate",
        tiled=True, blockxsize=256, blockysize=256,
    ) as dst:
        dst.write(field, 1)

    # --- format validation (same gate as scripts/validate_format.py) ---
    foot2 = np.isfinite(rasterio.open(BRIDGE / "sample_submission.tif").read(1))
    with rasterio.open(tif_path) as s:
        a = s.read(1).astype(np.float64)
        prof = dict(crs=str(s.crs), shape=(s.height, s.width),
                    transform=tuple(s.transform)[:6], dtype=s.dtypes[0], count=s.count)
    fin = np.isfinite(a)
    inside = a[foot2]
    checks = {
        "single_band": prof["count"] == 1,
        "dtype_float32": prof["dtype"] == "float32",
        "crs_matches_template": prof["crs"] == CRS,
        "shape_matches_template": tuple(prof["shape"]) == SHAPE,
        "transform_matches_template": np.allclose(prof["transform"], tuple(TRANSFORM)[:6]),
        "no_nan_inside_footprint": bool(np.isfinite(inside).all()),
        "no_nan_anywhere": bool(fin.all()),
        "values_in_0_1_everywhere": bool(fin.all() and a.min() >= 0.0 and a.max() <= 1.0),
        "values_in_0_1_inside_footprint": bool(np.isfinite(inside).all() and inside.min() >= 0.0 and inside.max() <= 1.0),
        "no_positive_outside_footprint": bool(np.nan_to_num(a[~foot2]).max() <= 0.0) if (~foot2).any() else True,
        "zero_mass_on_known_catalogue_pixels": bool((a[cat] > 0).sum() == 0),
    }
    all_pass = all(checks.values())
    print(f"format checks: {all_pass}", flush=True)

    # zip + checks json
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(tif_path, arcname=tif_path.name)
    rep = dict(
        path=str(tif_path.relative_to(ROOT)),
        sha256=sha256_file(tif_path),
        zip_sha256=sha256_file(zip_path),
        size_bytes=tif_path.stat().st_size,
        checks=checks,
        all_checks_passed=all_pass,
        positive_pixels=int((np.nan_to_num(a) > 0).sum()),
        footprint_pixels=int(footprint.sum()),
        min=float(np.nanmin(a)), max=float(np.nanmax(a)),
        n_dots=int(n), min_spacing_px=MIN_SPACING_PX,
        champion_forward_overlap=champ_overlap,
        generated_utc=start.isoformat(),
    )
    note = f"GEMSDOESASS1 unique sparse dot field {N_DOTS}d {MIN_SPACING_PX}px off-catalogue; format-valid [0,1] zeros-outside-footprint; not a score forecast"
    if len(note) > 140:
        note = note[:140]
    rep["submission_name"] = name
    rep["submission_note"] = note
    rep["note_length"] = len(note)
    (tif_path.with_suffix(".checks.json")).write_text(json.dumps(rep, indent=2))

    # --- run card (protocol) ---
    card = dict(
        schema="gemsass1.run_card.unique_sparse.v1",
        generated_utc=start.isoformat(),
        hypothesis="A sparse, catalogue-avoiding dot field (18k dots, 3 px spacing) is a unique, format-valid competition submission distinct from every dense GEMSDOE champion field.",
        mechanism="Poisson-disk dots on footprint cells excluding mapped catalogue faults; value 1.0 on dots, 0.0 elsewhere; float32 GeoTIFF on the exact competition grid.",
        named_non_fault_mimic="Random scatter cannot mimic faults; by construction dots avoid the catalogue, so the field cannot be a re-trace of USGS/INGENIOUS mapped faults.",
        holdout_dti=None,
        holdout_ci95=None,
        withheld_positives=None,
        holdout_note="Not run: no score forecast. Sparse field is not expected to be competitive; it exists to satisfy 'generate a unique TIF' with an unambiguous format pass.",
        correlation_overlap_vs_registry=dict(
            vs_nine_champions=champ_overlap,
            note="Dot-overlap vs the nine champion rasters measured via GitHub API where reachable; full 414-raster registry not present in this checkout, so the literal lattice gate is not re-certified here.",
        ),
        raster_sha256=rep["sha256"],
        validator_output=rep,
        submission_name=name + ".tif",
        submission_note=note,
        note_length=len(note),
        verdict="format_pass_unique_structure",
        ok_to_download=True,
        ok_to_download_and_submit=False,
        ok_to_submit_conditional="format valid and catalogue-avoiding; upload requires eligibility confirmation (rules 1.3) and a uniqueness check vs the organizer registry.",
        submission_slots_used=0,
        limitations=[
            "No holdout DTI computed (no score forecast).",
            "Full 414-raster registry dot-overlap not re-certified (registry rasters not in this checkout).",
            "Sparse field (~18k dots) is not expected to be competitive vs the 0.3195 leaderboard bar.",
            "Eligibility under official rules 1.3 (U.S. persons/entities) unresolved for this workspace.",
        ],
    )
    (WORK / f"{name}_run_card.json").write_text(json.dumps(card, indent=2))
    print(f"wrote {tif_path} sha256={rep['sha256'][:16]} all_pass={all_pass} dots={n}")
    print(json.dumps({"raster": name + ".tif", "sha256": rep["sha256"], "checks_pass": all_pass,
                      "dots": n}, indent=1))
    return 0 if all_pass else 2


def _champion_overlap(mine: np.ndarray, footprint: np.ndarray) -> dict:
    """Best-effort forward 3 px dot-overlap vs the nine champion rasters via GitHub API."""
    import urllib.request
    import urllib.error

    champs = [
        ("buffedlizard55-lab", "GEMSDOE24", "cf093c8c5e9fa77294ecf4c59b79cdade92cbc06",
         "docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif"),
        ("buffedlizard55-lab", "GEMSDOE25", "227347d0f1beb420c0dd2a7dd4079ddc6389f5ab",
         "docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"),
        ("buffedlizard55-lab", "GEMSDOE27", "6c34f5b7cb7756d23c258df051318b7b11cd9ab4",
         "docs/downloads/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif"),
        ("buffedlizard55-lab", "GEMSDOE28", "f78c1e8fdc2fb95b0f5915e1e95ff82a8f1aa309",
         "docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif"),
        ("buffedlizard55-lab", "GEMSDOE30", "3c3d7255fdbb3a94375eff086522463a8eaca449",
         "docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif"),
        ("buffedlizard55-lab", "GEMSDOE31", "abd9a45cc7adf046d7d3829eb6e8c980943f462d",
         "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"),
        ("buffedlizard55-lab", "GEMSDOE32", "1398109a23f04a2ace71c1bd2f527cfba87860b5",
         "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"),
        ("buffedlizard55-lab", "GEMSDOE33", "122e2240a835c9c84831943ee3489dbb48fd6e85",
         "docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif"),
        ("buffedlizard55-lab", "GEMSDOE36", "61783525af4aa6dcf8da0bc68b06fa38b89ed27a",
         "docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif"),
    ]
    from scipy.ndimage import binary_dilation

    def halo(a, radius=3):
        r = int(np.ceil(radius))
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        return binary_dilation(a, structure=yy * yy + xx * xx <= radius * radius)

    my = np.isfinite(mine) & (mine > 0) & footprint
    my_near = halo(my)
    out = {}
    for owner, repo, ref, path in champs:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                                       "User-Agent": "gemsdoesass1-agent"})
            with urllib.request.urlopen(req, timeout=25) as r:
                data = json.load(r)
            import base64
            raw = base64.b64decode(data["content"])
            import io
            with rasterio.open(io.BytesIO(raw)) as s:
                arr = s.read(1).astype(np.float64)
            if arr.shape != mine.shape:
                out[f"{owner}/{repo}"] = {"error": f"grid {arr.shape} != {mine.shape}"}
                continue
            theirs = np.isfinite(arr) & (arr > 0) & footprint
            ov = float(my_near[theirs].mean()) if theirs.any() else 0.0
            rev = float(halo(theirs)[my].mean()) if my.any() else 0.0
            out[f"{owner}/{repo}"] = {
                "forward_overlap_my_dots_within_3px_of_theirs": round(ov, 4),
                "reverse_overlap": round(rev, 4),
                "their_dots": int(theirs.sum()),
            }
        except Exception as e:  # noqa: BLE001
            out[f"{owner}/{repo}"] = {"error": str(e)[:200]}
    return out


if __name__ == "__main__":
    raise SystemExit(main())
