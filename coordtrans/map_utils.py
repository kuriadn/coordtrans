"""Map display helpers — reproject survey coordinates to WGS84 for Leaflet."""

from __future__ import annotations

import json
from typing import Any

from django.conf import settings

try:
    import pyproj
except ImportError:  # pragma: no cover
    pyproj = None


def _transformer(epsg: int | str):
    if pyproj is None:
        return None
    try:
        source = pyproj.CRS.from_user_input(epsg)
        target = pyproj.CRS.from_epsg(4326)
        return pyproj.Transformer.from_crs(source, target, always_xy=True)
    except Exception:
        return None


def _en_to_wgs84(easting, northing, epsg: int | str):
    transformer = _transformer(epsg)
    if transformer is None:
        return None
    try:
        lng, lat = transformer.transform(float(easting), float(northing))
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return None
        return {'lat': round(lat, 8), 'lng': round(lng, 8)}
    except Exception:
        return None


def _cassini_epsg():
    proj4 = getattr(settings, 'MAP_CASSINI_PROJ4', '')
    if proj4:
        return proj4
    epsg = getattr(settings, 'MAP_CASSINI_EPSG', None)
    if epsg:
        return epsg
    return 32637


def _utm_epsg():
    return getattr(settings, 'MAP_UTM_EPSG', 32637)


def _crs_for_system(system_label: str):
    """Return pyproj input for Cassini or UTM easting/northing."""
    if system_label in ('Cassini', 'cass'):
        return _cassini_epsg()
    return _utm_epsg()


def _sheet_control_points(sheet_no: str):
    from coordtrans.models import SheetReference

    points = []
    try:
        sheet = SheetReference.objects.select_related(
            'pt1', 'pt2', 'pt3', 'pt4',
        ).get(shtno=sheet_no)
    except SheetReference.DoesNotExist:
        return points

    for idx, pt in enumerate((sheet.pt1, sheet.pt2, sheet.pt3, sheet.pt4), start=1):
        for label, e, n, system in (
            ('cass', pt.cass_x, pt.cass_y, 'Cassini'),
            ('utm', pt.utm_x, pt.utm_y, 'U.T.M'),
        ):
            geo = _en_to_wgs84(e, n, _crs_for_system(system))
            if geo:
                points.append({
                    'id': f'CP{idx}-{label}',
                    'label': f'Control {pt.pid} ({label.upper()})',
                    'e': float(e),
                    'n': float(n),
                    'lat': geo['lat'],
                    'lng': geo['lng'],
                    'kind': 'control',
                })
    return points


def build_map_context(retval) -> dict[str, Any] | None:
    """
    Build JSON-serialisable map payload from convertData() output.

    retval[0] = [sheet, target_label, in_count, valid_count]
    retval[1] = list of [input_pt, output_pt|error_message]
    """
    if not retval or len(retval) < 2:
        return None

    meta = retval[0]
    rows = retval[1]
    if not isinstance(rows, list):
        return None
    if not rows or not isinstance(rows[0], list):
        return None

    sheet_no = meta[0]
    target_label = meta[1]
    input_system = 'U.T.M' if target_label == 'Cassini' else 'Cassini'
    output_system = target_label

    input_epsg = _crs_for_system(input_system)
    output_epsg = _crs_for_system(output_system)

    features = []
    for index, row in enumerate(rows, start=1):
        if len(row) < 2:
            continue
        inp, out = row[0], row[1]
        feature = {
            'id': index,
            'input': {
                'e': float(inp[0]),
                'n': float(inp[1]),
                'system': input_system,
            },
            'output': None,
            'status': 'skipped',
        }
        in_geo = _en_to_wgs84(inp[0], inp[1], input_epsg)
        if in_geo:
            feature['input'].update(in_geo)

        if out != 'Point outside sheet - Not transformed':
            out_geo = _en_to_wgs84(out[0], out[1], output_epsg)
            feature['output'] = {
                'e': float(out[0]),
                'n': float(out[1]),
                'system': output_system,
            }
            feature['status'] = 'ok'
            if out_geo:
                feature['output'].update(out_geo)
        features.append(feature)

    georef_ok = any(
        f.get('input', {}).get('lat') is not None
        or (f.get('output') or {}).get('lat') is not None
        for f in features
    )

    return {
        'sheet': sheet_no,
        'target': target_label,
        'input_system': input_system,
        'output_system': output_system,
        'google_maps_enabled': bool(getattr(settings, 'GOOGLE_MAPS_API_KEY', '')),
        'default_center': getattr(settings, 'MAP_DEFAULT_CENTER', [-1.286389, 36.817223]),
        'default_zoom': getattr(settings, 'MAP_DEFAULT_ZOOM', 12),
        'points': features,
        'controls': _sheet_control_points(sheet_no),
        'georef_ok': georef_ok,
    }


def map_context_json(retval) -> str:
    data = build_map_context(retval)
    return json.dumps(data or {})
