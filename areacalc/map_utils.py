"""Map display for area / perimeter results."""
from __future__ import annotations

import json
from typing import Any

from django.conf import settings

from coordtrans.map_utils import _en_to_wgs84, _utm_epsg

from .compute import AreaResult, format_bearing_dms


def _point(label: str, easting: float, northing: float, epsg) -> dict[str, Any]:
    geo = _en_to_wgs84(easting, northing, epsg)
    return {
        'label': label,
        'e': round(float(easting), 3),
        'n': round(float(northing), 3),
        'lat': geo['lat'] if geo else None,
        'lng': geo['lng'] if geo else None,
    }


def build_area_map_context(result: AreaResult) -> dict[str, Any]:
    epsg = _utm_epsg()
    vertices = [
        _point(v.label, v.easting, v.northing, epsg)
        for v in result.vertices
    ]
    georef_ok = all(v.get('lat') is not None for v in vertices)
    mode = 'geographic' if georef_ok else 'plan'

    edges = []
    for edge in result.edges:
        edges.append({
            'index': edge.index,
            'from_label': edge.from_label,
            'to_label': edge.to_label,
            'distance': round(edge.distance, 3),
            'distance_label': f'{edge.distance:.2f} m',
            'bearing_label': format_bearing_dms(edge.bearing_deg),
            'from': _point(edge.from_label, edge.easting_from, edge.northing_from, epsg),
            'to': _point(edge.to_label, edge.easting_to, edge.northing_to, epsg),
        })

    return {
        'mode': mode,
        'closed': result.closed,
        'parcel_name': result.parcel_name,
        'georef_ok': georef_ok,
        'google_maps_enabled': bool(getattr(settings, 'GOOGLE_MAPS_API_KEY', '')),
        'default_center': getattr(settings, 'MAP_DEFAULT_CENTER', [-1.286389, 36.817223]),
        'default_zoom': getattr(settings, 'MAP_DEFAULT_ZOOM', 12),
        'vertices': vertices,
        'edges': edges,
        'area_sq_m': result.area_sq_m,
        'perimeter_m': result.perimeter_m,
    }


def area_map_json(result: AreaResult) -> str:
    return json.dumps(build_area_map_context(result))
