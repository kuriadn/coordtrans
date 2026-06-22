"""Map display for CRS transform results."""
from __future__ import annotations

from typing import Any

from django.conf import settings

from coordtrans.map_utils import _en_to_wgs84

from .compute import CrsTransformResult


def _axis_labels(geographic: bool) -> tuple[str, str]:
    if geographic:
        return 'Longitude', 'Latitude'
    return 'Easting', 'Northing'


def build_crs_map_context(result: CrsTransformResult) -> dict[str, Any]:
    features = []
    for row in result.rows:
        if result.source_geographic:
            in_geo = {'lat': row.in_y, 'lng': row.in_x}
        else:
            in_geo = _en_to_wgs84(row.in_x, row.in_y, result.source_crs)

        if result.target_geographic:
            out_geo = {'lat': row.out_y, 'lng': row.out_x}
        else:
            out_geo = _en_to_wgs84(row.out_x, row.out_y, result.target_crs)

        feature = {
            'id': row.index,
            'input': {
                'e': row.in_x,
                'n': row.in_y,
                'system': 'Source',
            },
            'output': {
                'e': row.out_x,
                'n': row.out_y,
                'system': 'Target',
            },
            'status': 'ok',
        }
        if in_geo:
            feature['input'].update(in_geo)
        if out_geo:
            feature['output'].update(out_geo)
        features.append(feature)

    georef_ok = any(
        f.get('input', {}).get('lat') is not None or (f.get('output') or {}).get('lat') is not None
        for f in features
    )

    in_x_label, in_y_label = _axis_labels(result.source_geographic)
    out_x_label, out_y_label = _axis_labels(result.target_geographic)

    return {
        'sheet': result.preset_label,
        'target': 'CRS transform',
        'input_system': in_x_label,
        'output_system': out_x_label,
        'google_maps_enabled': bool(getattr(settings, 'GOOGLE_MAPS_API_KEY', '')),
        'default_center': getattr(settings, 'MAP_DEFAULT_CENTER', [-1.286389, 36.817223]),
        'default_zoom': getattr(settings, 'MAP_DEFAULT_ZOOM', 12),
        'points': features,
        'controls': [],
        'georef_ok': georef_ok,
        'axis_labels': {
            'in_x': in_x_label,
            'in_y': in_y_label,
            'out_x': out_x_label,
            'out_y': out_y_label,
        },
    }
