"""H-KDAM feature block: damage-zone radiometrics x potential-field contacts (label-free).

Hypothesis (pre-registered in knowledge/hypotheses_20261031.md before any run):
    Faults missing from the USGS/INGENIOUS catalogue map are best found where an *immobile-element
    normalised potassium depletion* (hydrothermal alteration of the damage zone) coincides with an
    independently derived *potential-field contact/lineament* (a magnetically defined basement
    structure). Neither instrument alone is enough: lidar scarps fade downslope, and raw aeromagnetic
    amplitude mostly tracks lithology/basement relief, so the corpus of previous lanes (which fed raw
    bands to a learner) can only re-find what the lidar scarp transform already sees.

Physics and the exact transforms
--------------------------------
All potential-field transforms below are the standard ones (Blakely 1995, *Potential Theory in
Gravity and Magnetic Applications*, CUP; Miller & Singh 1994, J. Appl. Geophys. 32:213-217, doi
10.1016/0926-9851(94)90022-1 for the tilt derivative; Wijns et al. 2005, Geophysics 70(4):39-43 for
the theta map; Roest et al. 1992, Geophysics 57(1):116-125 for the analytic signal):

  * horizontal gradient magnitude  HGM = hypot(dT/dx, dT/dy)
  * vertical derivative           dT/dz = |k| * FFT(T)          (Laplace, source-free half-space)
  * analytic signal amplitude      AS  = hypot(dT/dx, dT/dy, dT/dz)
  * tilt derivative                TDR = atan2(dT/dz, hypot(dT/dx, dT/dy))   zero at contacts
  * theta map                      cos(theta) = hypot(dT/dx,dT/dy) / AS      -> 1 at contacts
  * upward continuation to h       T_h = IFFT(exp(-|k| h) * FFT(T))

The input rasters here are the quantised (u8, rank-like) GeoDAWN products mirrored for this project,
so every derivative is a *rank-scale* surrogate, not a calibrated nT/m gradient. That is stated
wherever a number from these features is quoted; the model only needs monotone shape.

  * K-depletion halo: with Th effectively immobile and K mobile in hydrothermal systems, alteration
    shows up as a K/Th depression relative to the local background (IAEA-TECDOC-1363, 2003,
    "Guidelines for radioelement mapping using gamma ray spectrometry data"). Implemented as the
    band-pass  gauss(K/Th, sigma=3 px) - gauss(K/Th, sigma=12 px)  divided by the local mean, so the
    feature is a dimensionless relative depletion, not a raw count rate.

  * structure tensor / coherence (Bigun & Granlund 1987; Weickert 1997): per-scale coherence
    C = (l1 - l2)/(l1 + l2) in [0,1] and orientation theta. ``persist`` is min(C) over sigma=2,5,10 px
    (a lineament that survives three scales is a through-going structure, not a texture artifact);
    ``xcal`` is C_mag * C_lidar * cos^2(2 dtheta), which is only large where the magnetic and lidar
    structure tensors agree on orientation -- the two-instrument corroboration this lane adds.

Nodata handling: 0 is nodata in every mirrored u8 stack (see data/features/*.json). Missing cells are
filled by nearest valid neighbour *before* any derivative, so a nodata hole cannot manufacture an
edge. Filled cells are excluded from training/emission through ``valid``.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

PIXEL_M = 100.0


def fill_nearest(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Replace invalid cells by their nearest valid neighbour (indices from an EDT)."""
    if valid.all():
        return a.astype(np.float32, copy=False)
    if not valid.any():
        return np.zeros(a.shape, np.float32)
    _, (iy, ix) = ndimage.distance_transform_edt(~valid, return_indices=True)
    return a[iy, ix].astype(np.float32, copy=False)


def fft_vertical_and_horizontal(a: np.ndarray, spacing: float = PIXEL_M):
    """Return (dx, dy, dz) of a potential field by spectral differentiation (float32).

    dz = |k| * F is the vertical derivative implied by Laplace's equation in the source-free
    region above the sources; dx, dy use i*kx, i*ky. A Tukey taper removes the periodic-wrap
    artifact that would otherwise put a false contact on the grid border.
    """
    H, W = a.shape
    win = np.outer(np.hanning(H).astype(np.float32), np.hanning(W).astype(np.float32)) + 1e-6
    F = np.fft.rfft2(a * win)
    kx = 2.0 * np.pi * np.fft.fftfreq(H, d=spacing)
    ky = 2.0 * np.pi * np.fft.rfftfreq(W, d=spacing)
    kk = np.hypot(kx[:, None], ky[None, :])
    dx = np.fft.irfft2(1j * kx[:, None] * F, s=(H, W)).astype(np.float32)
    dy = np.fft.irfft2(1j * ky[None, :] * F, s=(H, W)).astype(np.float32)
    dz = np.fft.irfft2(kk * F, s=(H, W)).astype(np.float32)
    del F
    return dx, dy, dz


def fft_upward_continue(a: np.ndarray, height_m: float, spacing: float = PIXEL_M) -> np.ndarray:
    H, W = a.shape
    F = np.fft.rfft2(a)
    kx = 2.0 * np.pi * np.fft.fftfreq(H, d=spacing)
    ky = 2.0 * np.pi * np.fft.rfftfreq(W, d=spacing)
    kk = np.hypot(kx[:, None], ky[None, :])
    out = np.fft.irfft2(F * np.exp(-kk * height_m), s=(H, W)).astype(np.float32)
    del F
    return out


def _tensor(a: np.ndarray, sigma: float):
    """Structure tensor of a scalar field: coherence in [0,1] and orientation (mod pi)."""
    s = ndimage.gaussian_filter(a, sigma, mode="nearest").astype(np.float32)
    gy = ndimage.sobel(s, axis=0)
    gx = ndimage.sobel(s, axis=1)
    jxx = ndimage.gaussian_filter(gx * gx, sigma, mode="nearest")
    jyy = ndimage.gaussian_filter(gy * gy, sigma, mode="nearest")
    jxy = ndimage.gaussian_filter(gx * gy, sigma, mode="nearest")
    tr = jxx + jyy
    disc = np.sqrt(np.maximum((jxx - jyy) ** 2 + 4.0 * jxy * jxy, 0.0))
    l1 = 0.5 * (tr + disc)
    l2 = 0.5 * (tr - disc)
    coh = np.where(l1 > 1e-9, (l1 - l2) / np.maximum(l1, 1e-9), 0.0).astype(np.float32)
    theta = (0.5 * np.arctan2(2.0 * jxy, jxx - jyy)).astype(np.float32)
    return coh, theta


def _rank01(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Map a feature to [0,1] by percentile ranks over valid cells (scale-free, outlier-robust)."""
    v = a[valid]
    if v.size == 0:
        return np.zeros(a.shape, np.float32)
    lo, hi = np.percentile(v, [0.5, 99.5])
    out = np.clip((a - lo) / max(hi - lo, 1e-9), 0.0, 1.0)
    return out.astype(np.float32)


def build_kdam_features() -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Return ({name: float32 HxW}, valid). Every feature is label-free (catalogue never read)."""
    from .grid import load_u8_stack

    lid, lnames, _ = load_u8_stack("lidar_scarp_features")
    lid_valid = lid[lnames.index("valid")] > 0
    rad, rnames, _ = load_u8_stack("geodawn_rad")
    ext, enames, _ = load_u8_stack("geodawn_extensions")

    def ch(stack, names, n):
        return stack[names.index(n)].astype(np.float32)

    feats: dict[str, np.ndarray] = {}
    # ---- lidar scarp morphology (existing, kept as the topographic control) -----------
    for n in ("ex_max", "step_max", "lapneg_max", "relief", "coh100"):
        feats[f"lidar_{n}"] = np.where(lid_valid, ch(lid, lnames, n), 0.0).astype(np.float32)
    strike_deg = (ch(lid, lnames, "strike") - 1.0) / 254.0 * 180.0
    strike = np.deg2rad(strike_deg)
    feats["lidar_strike_cos2"] = (np.cos(2 * strike) * lid_valid).astype(np.float32)
    feats["lidar_strike_sin2"] = (np.sin(2 * strike) * lid_valid).astype(np.float32)
    lidar_relief_filled = fill_nearest(feats["lidar_relief"], lid_valid)
    del lid

    # ---- radiometrics: immobile-element normalised potassium --------------------------
    K = fill_nearest(ch(rad, rnames, "K"), ch(rad, rnames, "K") > 0)
    Th = fill_nearest(ch(rad, rnames, "Th"), ch(rad, rnames, "Th") > 0)
    rad_valid = (ch(rad, rnames, "K") > 0) & (ch(rad, rnames, "Th") > 0)
    thk = fill_nearest(ch(ext, enames, "ThK"), ch(ext, enames, "ThK") > 0)  # u8 K/Th
    feats["rad_K"] = np.where(rad_valid, K, 0.0).astype(np.float32)
    feats["rad_Th"] = np.where(rad_valid, Th, 0.0).astype(np.float32)
    feats["rad_ThK"] = np.where(rad_valid, thk, 0.0).astype(np.float32)
    del K, Th

    # K-depletion halo: band-pass of K/Th, normalised by the local mean (dimensionless)
    small = ndimage.gaussian_filter(thk, 3.0, mode="nearest")
    large = ndimage.gaussian_filter(thk, 12.0, mode="nearest")
    halo = (small - large) / np.maximum(large, 1e-3)
    feats["kdep_halo"] = np.where(rad_valid, halo, 0.0).astype(np.float32)
    feats["kdep_deplete"] = np.where(rad_valid, np.maximum(-halo, 0.0), 0.0).astype(np.float32)
    del small, large, halo, thk

    # ---- magnetics: contacts, lineaments, cross-instrument agreement -------------------
    tmi_raw = ch(ext, enames, "TMI_up150")
    mag_valid = tmi_raw > 0
    tmi = fill_nearest(tmi_raw, mag_valid)
    feats["mag_TMI"] = np.where(mag_valid, tmi, 0.0).astype(np.float32)
    dx, dy, dz = fft_vertical_and_horizontal(tmi)
    thdr = np.hypot(dx, dy)
    as_amp = np.hypot(thdr, dz)
    feats["mag_tdr"] = np.arctan2(dz, np.maximum(thdr, 1e-6)).astype(np.float32)
    feats["mag_theta"] = (thdr / np.maximum(as_amp, 1e-6)).astype(np.float32)
    up500 = fft_upward_continue(tmi, 500.0)
    g500 = ndimage.gaussian_filter(up500, 2.0, mode="nearest")
    feats["mag_hgm500"] = np.hypot(ndimage.sobel(g500, 0), ndimage.sobel(g500, 1)).astype(np.float32)
    del g500, up500, as_amp
    # coherence persistence across scales (a through-going lineament survives all three)
    c2, t2 = _tensor(tmi, 2.0)
    c5, t5 = _tensor(tmi, 5.0)
    c10, t10 = _tensor(tmi, 10.0)
    feats["lineament_persist"] = np.minimum(np.minimum(c2, c5), c10).astype(np.float32)
    # distance to the nearest magnetic *contact*: |TDR| small AND horizontal gradient strong
    hgm0 = np.hypot(dx, dy)
    hi = hgm0 > np.percentile(hgm0[mag_valid], 80.0) if mag_valid.any() else hgm0 > 0
    contact = (np.abs(feats["mag_tdr"]) < 0.20) & hi
    feats["mcontact_dist"] = ndimage.distance_transform_edt(~contact).astype(np.float32) if contact.any() else np.full(tmi.shape, 100.0, np.float32)
    del dx, dy, dz, hgm0, contact, hi
    # cross-instrument orientation agreement (magnetic vs lidar structure tensor)
    coh_l, theta_l = _tensor(lidar_relief_filled, 5.0)
    coh_m, theta_m = _tensor(tmi, 5.0)
    dtheta = theta_m - theta_l
    feats["xcal_agree"] = (coh_l * coh_m * np.cos(2.0 * dtheta) ** 2).astype(np.float32)
    del coh_l, coh_m, theta_l, theta_m, dtheta, tmi, c2, c5, c10, t2, t5, t10
    del rad, ext, lidar_relief_filled, tmi_raw
    valid = lid_valid | mag_valid | rad_valid
    return feats, valid


def rank_features(feats: dict[str, np.ndarray], valid: np.ndarray, names: list[str]) -> np.ndarray:
    """Stack the selected features, each mapped to [0,1] by rank, as one float16 array."""
    out = np.empty((len(names),) + valid.shape, np.float16)
    for i, n in enumerate(names):
        out[i] = _rank01(feats[n], valid).astype(np.float16)
    return out
