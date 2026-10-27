"""BGAC-1 label-free signed gravity/depth opposition. See frozen hypothesis card."""
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from scipy.stats import rankdata


def percentile_ranks(a, valid):
    out = np.zeros(a.shape, np.float32)
    n = int(valid.sum())
    if not n:
        raise ValueError('no supported feature pixels')
    out[valid] = rankdata(a[valid]).astype(np.float32) / n
    return out


def build(root, footprint):
    cache = Path(root) / '.cache/features'
    raw = {k: np.load(cache / f'band-{i:02d}.npy', mmap_mode='r')
           for k, i in [('gravity', 13), ('basement', 15), ('topography', 12)]}
    valid = footprint.copy()
    for a in raw.values():
        valid &= np.isfinite(a)
    eligible = valid & (ndi.distance_transform_edt(valid) > 20)
    # Fixed physical support restriction: 4 sigma of the largest smoothing scale.
    filled = {k: np.where(valid, a, np.median(a[valid])).astype(np.float32) for k, a in raw.items()}
    features = {}
    oppositions = []
    for scale in (2, 5):
        grads = {}
        for key in ('gravity', 'basement'):
            a = filled[key]
            gy = ndi.gaussian_filter(a, scale, order=(1, 0), mode='nearest')
            gx = ndi.gaussian_filter(a, scale, order=(0, 1), mode='nearest')
            mag = np.hypot(gx, gy)
            features[f'{key}_gradient_s{scale}'] = percentile_ranks(mag, eligible)
            grads[key] = (gy, gx, mag)
        ay, ax, am = grads['gravity']
        by, bx, bm = grads['basement']
        den = am * bm
        opposition = np.divide(-(ay * by + ax * bx), den, out=np.zeros_like(den), where=den > 1e-12)
        opposition = np.clip(opposition, 0, 1)
        opposition[~eligible] = 0
        features[f'signed_opposition_s{scale}'] = opposition
        oppositions.append(opposition)
    a = filled['topography']
    relief = np.hypot(ndi.gaussian_filter(a, 2, order=(1, 0), mode='nearest'),
                      ndi.gaussian_filter(a, 2, order=(0, 1), mode='nearest'))
    features['low_surface_expression'] = 1 - percentile_ranks(relief, eligible)
    features['low_surface_expression'][~eligible] = 0
    magnitude = np.ones(footprint.shape, np.float32)
    for key in ('gravity_gradient_s2', 'basement_gradient_s2', 'gravity_gradient_s5', 'basement_gradient_s5'):
        magnitude *= features[key]
    # Geometric mean of four magnitude ranks, times two-scale sign consistency.
    surface = np.power(magnitude, .25) * np.sqrt(oppositions[0] * oppositions[1])
    surface *= .5 + .5 * features['low_surface_expression']
    surface[~eligible] = 0
    features['BGAC-1'] = surface.astype(np.float32)
    return features, eligible


def emit(surface, allowed, budget, radius=3):
    """Stable priority hard-core dots; no random jitter or catalogue-derived scoring."""
    if surface.shape != allowed.shape or budget < 0 or not np.isfinite(surface).all():
        raise ValueError('invalid emitter inputs')
    ids = np.flatnonzero(allowed & (surface > 0))
    order = np.argsort(-surface.ravel()[ids], kind='stable')
    ids = ids[order]
    h, w = surface.shape
    blocked = np.zeros(surface.shape, bool)
    dots = np.zeros(surface.shape, bool)
    yy, xx = np.mgrid[-radius:radius+1, -radius:radius+1]
    disk = yy**2 + xx**2 <= radius**2
    n = 0
    for i in ids:
        if n >= budget:
            break
        y, x = divmod(int(i), w)
        if blocked[y, x]:
            continue
        dots[y, x] = True
        n += 1
        y0, y1 = max(0, y-radius), min(h, y+radius+1)
        x0, x1 = max(0, x-radius), min(w, x+radius+1)
        blocked[y0:y1, x0:x1] |= disk[y0-y+radius:y1-y+radius, x0-x+radius:x1-x+radius]
    return dots
