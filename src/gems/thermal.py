"""Label-free geothermal-indicator features (H-TV family, session 2026-10-30).

Sources (all integrity-verified owner mirrors of free official data, see
registry/upstream_data_manifest.json and knowledge/hypotheses_20261030.md):
  * GDR 1391 "Well and Spring Temperature and Chemistry" (DOI 10.15121/1881483, CC BY 4.0)
  * GDR 1391 INGENIOUS 2 m temperature-probe regional survey (same DOI)
  * GDR 1391 "Paleo-Geothermal Features" (travertine/tufa/sinter deposits)
  * GDR 1391 Quaternary volcanic vents

LEAKAGE RULE: the wellspring CSV contains a `dist_known_fault_px` column that is derived from the
competition labels. It is NEVER read here (only the column names listed in _SPRING_COLS are
parsed). Every distance feature below is a distance to a geothermal ANCHOR, not to any fault.
"""
from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

import numpy as np
from scipy import ndimage

from .grid import ROOT, SHAPE, TRANSFORM

DATA_EXT = ROOT / 'data' / 'external'

_SPRING_COLS = ['thermalclass', 'row', 'col', 'temp_c',
                'geothermquartz_c', 'geothermchalc_c', 'geothermcat_c']


def _to_rowcol(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    inv = ~TRANSFORM
    col = inv.a * x + inv.b * y + inv.c
    row = inv.d * x + inv.e * y + inv.f
    return row, col


def _points_to_mask(rows: np.ndarray, cols: np.ndarray, shape=SHAPE) -> np.ndarray:
    m = np.zeros(shape, bool)
    r = np.rint(rows).astype(int)
    c = np.rint(cols).astype(int)
    ok = (r >= 0) & (r < shape[0]) & (c >= 0) & (c < shape[1])
    m[r[ok], c[ok]] = True
    return m


def load_anchor_points() -> dict:
    """Return dict of boolean masks + rasters. Pure label-free geothermal indicators."""
    H, W = SHAPE
    # ---- springs / wells ----
    sites: dict[tuple, dict] = {}
    with open(DATA_EXT / 'gdr_wellspring_in_footprint.csv') as fh:
        for r in csv.DictReader(fh):
            key = (r['name'], r['row'], r['col'])
            cls = (r['thermalclass'] or '').strip().lower()
            try:
                temp = float(r['temp_c']) if r['temp_c'] else np.nan
            except ValueError:
                temp = np.nan
            geo = []
            for k in ('geothermquartz_c', 'geothermchalc_c', 'geothermcat_c'):
                try:
                    geo.append(float(r[k]) if r[k] else np.nan)
                except ValueError:
                    geo.append(np.nan)
            s = sites.setdefault(key, dict(cls=set(), temp=[], geo=[], row=int(r['row']), col=int(r['col'])))
            s['cls'].add(cls)
            s['temp'].append(temp)
            s['geo'].extend(geo)
    rows_a, cols_a, rows_hot, cols_hot, rows_geo, cols_geo = [], [], [], [], [], []
    for s in sites.values():
        temp = np.nanmax(s['temp']) if s['temp'] else np.nan
        geo = np.nanmax(s['geo']) if s['geo'] else np.nan
        cls = s['cls']
        is_warmish = bool(cls & {'hot', 'warm'}) or (np.isfinite(temp) and temp >= 40.0)
        if is_warmish:
            rows_a.append(s['row']); cols_a.append(s['col'])
        is_hot = bool(cls & {'hot'}) or (np.isfinite(temp) and temp >= 60.0) or (np.isfinite(geo) and geo >= 150.0)
        if is_hot:
            rows_hot.append(s['row']); cols_hot.append(s['col'])
        if np.isfinite(geo) and geo >= 100.0:
            rows_geo.append(s['row']); cols_geo.append(s['col'])
    # ---- paleo deposits (NAD83 lon/lat -> EPSG:32611) ----
    from pyproj import Transformer
    tr = Transformer.from_crs('EPSG:4269', 'EPSG:32611', always_xy=True)
    z = zipfile.ZipFile(DATA_EXT / 'paleo_geothermal_regional.zip')
    paleo = list(csv.DictReader(io.StringIO(z.read('Paleo_geothermal_final.csv').decode('latin-1'))))
    pr, pc = [], []
    sinter_r, sinter_c = [], []
    for r in paleo:
        try:
            x, y = tr.transform(float(r['Long_deg_NAD83']), float(r['Lat_deg_NAD83']))
        except (TypeError, ValueError):
            continue
        rr, cc = _to_rowcol(np.array([x]), np.array([y]))
        if 0 <= rr[0] < H and 0 <= cc[0] < W:
            pr.append(rr[0]); pc.append(cc[0])
            if (r['Deposit_type'] or '').lower().startswith(('sinter', 'travertine', 'silica', 'alteration', 'sulfur', 'explosion')):
                sinter_r.append(rr[0]); sinter_c.append(cc[0])
    # ---- vents ----
    vr, vc = [], []
    with open(DATA_EXT / 'gdr_volcanic_vents_in_footprint.csv') as fh:
        for r in csv.DictReader(fh):
            vr.append(int(r['row'])); vc.append(int(r['col']))
    # ---- 2 m temperature probes (NAD83 UTM 11N -> EPSG:32611 via pyproj) ----
    zp = zipfile.ZipFile(DATA_EXT / '2m_temperature_probe_INGENIOUS_regional_data.zip')
    name = [n for n in zp.namelist() if n.endswith('.xlsx')][0]
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(zp.read(name)), read_only=True)
    ws = wb.active
    ex, ny, dab = [], [], []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[4] is None or row[5] is None:
            continue
        ex.append(float(row[4])); ny.append(float(row[5]))
        dab.append(float(row[9]) if row[9] is not None else 0.0)
    x2, y2 = tr.transform(np.array(ex), np.array(ny), errcheck=False)
    # probes are NAD83 zone-11 metres; pyproj EPSG:4269-based pipeline is for lon/lat, so map
    # UTM NAD83 (26911) explicitly:
    from pyproj import Transformer as T2
    tr2 = T2.from_crs('EPSG:26911', 'EPSG:32611', always_xy=True)
    x2, y2 = tr2.transform(np.array(ex), np.array(ny))
    prow, pcol = _to_rowcol(x2, y2)
    probe_z = np.zeros(SHAPE, np.float32)
    ok = (np.rint(prow).astype(int) >= 0) & (np.rint(prow).astype(int) < H) & \
         (np.rint(pcol).astype(int) >= 0) & (np.rint(pcol).astype(int) < W)
    dab_arr = np.clip(np.array(dab, np.float64), 0.0, None)
    np.add.at(probe_z, (np.rint(prow[ok]).astype(int), np.rint(pcol[ok]).astype(int)), dab_arr[ok])
    probe_z = ndimage.gaussian_filter(probe_z, 3.0).astype(np.float32)

    return dict(
        anchor=_points_to_mask(np.array(rows_a), np.array(cols_a)),
        hot=_points_to_mask(np.array(rows_hot), np.array(cols_hot)),
        geotherm=_points_to_mask(np.array(rows_geo), np.array(cols_geo)),
        paleo=_points_to_mask(np.array(pr), np.array(pc)),
        sinter=_points_to_mask(np.array(sinter_r), np.array(sinter_c)),
        vent=_points_to_mask(np.array(vr), np.array(vc)),
        probe_z=probe_z,
        n_sites=len(sites), n_anchor=len(rows_a), n_hot=len(rows_hot),
        n_geotherm=len(rows_geo), n_paleo=len(pr), n_vent=len(vr), n_probe=int(ok.sum()),
    )


def build_thermal_features(anchors: dict, lidar_strike: np.ndarray) -> tuple[dict, dict]:
    """Return ({name: HxW float32}, meta). All features label-free."""
    feats = {}
    meta = {k: v for k, v in anchors.items() if isinstance(v, int)}
    # distance features (px)
    for key, out in (('anchor', 'th_anchor_logdist'), ('hot', 'th_hot_logdist'),
                     ('geotherm', 'th_geotherm_logdist'), ('paleo', 'th_paleo_logdist'),
                     ('sinter', 'th_sinter_logdist'), ('vent', 'th_vent_logdist')):
        dist, idx = ndimage.distance_transform_edt(~anchors[key], return_indices=True)
        feats[out] = np.log1p(dist).astype(np.float32)
        if key == 'anchor':
            nearest_r, nearest_c = idx
    # cluster density of anchors (1.5 km Gaussian window)
    mass = (anchors['anchor'].astype(np.float32) + 0.5 * anchors['hot'].astype(np.float32)
            + 0.5 * anchors['paleo'].astype(np.float32))
    feats['th_anchor_dens'] = ndimage.gaussian_filter(mass, 15.0).astype(np.float32)
    # shallow heat-flow anomaly raster
    feats['th_probe_z'] = anchors['probe_z']
    # along-strike alignment with the nearest anchor (cos2, +1 parallel), gated 2-30 px
    H, W = SHAPE
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bearing = np.arctan2(nearest_r.astype(np.float32) - yy, nearest_c.astype(np.float32) - xx)
    strike_deg = (lidar_strike - 1.0) / 254.0 * 180.0
    d = np.deg2rad(strike_deg) - bearing
    cos2 = np.cos(2 * d).astype(np.float32)
    dist_anchor = np.expm1(feats['th_anchor_logdist'])
    gate = ((dist_anchor >= 2.0) & (dist_anchor <= 30.0)).astype(np.float32)
    feats['th_align_cos2'] = np.where(gate > 0, np.maximum(cos2, 0.0), 0.0).astype(np.float32)
    return feats, meta
