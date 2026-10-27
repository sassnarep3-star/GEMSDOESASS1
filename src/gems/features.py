"""Feature stack on the competition grid, built from the cached u8 products mirrored from GEMSDOE24.

Sources (all official, documented in the sidecar JSONs in data/features/):
  * GeoDAWN airborne magnetic + radiometric survey, USGS data release doi:10.5066/P93LGLVQ
    (K, Th, U, TC, Th/K, U/K, U/Th, TMI upward-continued 150 m)  -> geodawn_rad_u8, geodawn_extensions_u8
  * 1 m / 2 m lidar DEM derivatives aggregated to 100 m (scarp morphology)        -> lidar_scarp_features_u8
Quantisation: u8 with 0 = nodata (see sidecars). Values are rank-like; we work in float32.

Catalogue-derived context is NEVER computed here from the full catalogue; it comes from
`holdout.catalogue_features(visible)` so a fold only ever sees its visible faults.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from .grid import load_u8_stack

LIDAR_USE = ["ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max", "downface_max",
             "upface_max", "cross_max", "relief", "coh100", "strike"]


def _grad_mag(a: np.ndarray, sigma: float) -> np.ndarray:
    g = ndimage.gaussian_filter(a.astype(np.float32), sigma)
    return np.hypot(ndimage.sobel(g, axis=0), ndimage.sobel(g, axis=1)).astype(np.float32)


def build_static_features() -> tuple[dict, np.ndarray]:
    """Return ({name: HxW float32}, lidar_valid bool). Independent of the catalogue."""
    feats: dict[str, np.ndarray] = {}
    lid, lnames, _ = load_u8_stack("lidar_scarp_features")
    valid = lid[lnames.index("valid")] > 0
    for n in LIDAR_USE:
        feats[f"lidar_{n}"] = lid[lnames.index(n)].astype(np.float32)
    # strike channel is 0..254 -> 0..180 degrees; keep as doubled-angle components too
    strike_deg = (feats["lidar_strike"] - 1.0) / 254.0 * 180.0
    strike_rad = np.deg2rad(strike_deg)
    feats["lidar_strike_cos2"] = np.cos(2 * strike_rad).astype(np.float32)
    feats["lidar_strike_sin2"] = np.sin(2 * strike_rad).astype(np.float32)
    # scarp dipole: crest convexity and base concavity together (geometric mean), uphill-facing excess
    feats["lidar_dipole"] = np.sqrt(feats["lidar_lapneg_max"] * feats["lidar_lappos_max"]).astype(np.float32)
    feats["lidar_face_asym"] = (feats["lidar_downface_max"] - feats["lidar_upface_max"]).astype(np.float32)
    del lid
    rad, rnames, _ = load_u8_stack("geodawn_rad")
    for n in rnames:
        feats[f"rad_{n}"] = rad[rnames.index(n)].astype(np.float32)
    del rad
    ext, enames, _ = load_u8_stack("geodawn_extensions")
    for n in enames:
        feats[f"mag_{n}" if n.startswith("TMI") else f"rad_{n}"] = ext[enames.index(n)].astype(np.float32)
    del ext
    feats["mag_hgrad_s2"] = _grad_mag(feats["mag_TMI_up150"], 2.0)
    feats["mag_hgrad_s5"] = _grad_mag(feats["mag_TMI_up150"], 5.0)
    feats["rad_K_grad_s3"] = _grad_mag(feats["rad_K"], 3.0)
    feats["rad_ThK_grad_s3"] = _grad_mag(feats["rad_ThK"], 3.0)
    feats["lidar_ex_max_s3"] = ndimage.gaussian_filter(feats["lidar_ex_max"], 3.0).astype(np.float32)
    return feats, valid


def add_catalogue_context(feats: dict, catf: dict) -> dict:
    """Add visible-only catalogue context + strike agreement between lidar grain and nearest visible fault."""
    out = dict(feats)
    out["cat_logdist"] = np.log1p(catf["dist_vis"]).astype(np.float32)
    out["cat_logtip"] = np.log1p(catf["tip_vis"]).astype(np.float32)
    out["cat_dens"] = catf["dens_vis"]
    strike_deg = (feats["lidar_strike"] - 1.0) / 254.0 * 180.0
    d = np.deg2rad(strike_deg) - catf["strike_vis"]
    out["cat_strike_agree"] = np.cos(2 * d).astype(np.float32)   # +1 parallel, -1 perpendicular
    return out


def stack(feats: dict, mask: np.ndarray, names: list[str]) -> np.ndarray:
    return np.stack([feats[n][mask] for n in names], axis=1).astype(np.float32)
