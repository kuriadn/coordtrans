"""Map display for bearing / distance results."""
from __future__ import annotations

import json
from typing import Any

from django.conf import settings

from coordtrans.map_utils import _en_to_wgs84, _utm_epsg

from .compute import BearingDistanceResult


def _point(label: str, easting: float, northing: float, epsg) -> dict[str, Any]:
    geo = _en_to_wgs84(easting, northing, epsg)
    return {
        'label': label,
        'e': round(float(easting), 3),
        'n': round(float(northing), 3),
        'lat': geo['lat'] if geo else None,
        'lng': geo['lng'] if geo else None,
    }


def build_geocalc_map_context(result: BearingDistanceResult) -> dict[str, Any]:
    epsg = _utm_epsg()
    from_pt = _point(
        result.from_point.label,
        result.from_point.easting,
        result.from_point.northing,
        epsg,
    )
    to_pt = _point(
        result.to_point.label,
        result.to_point.easting,
        result.to_point.northing,
        epsg,
    )
    georef_ok = from_pt.get('lat') is not None and to_pt.get('lat') is not None

    return {
        'mode': 'geographic' if georef_ok else 'plan',
        'georef_ok': georef_ok,
        'computation_mode': result.mode,
        'google_maps_enabled': bool(getattr(settings, 'GOOGLE_MAPS_API_KEY', '')),
        'default_center': getattr(settings, 'MAP_DEFAULT_CENTER', [-1.286389, 36.817223]),
        'default_zoom': getattr(settings, 'MAP_DEFAULT_ZOOM', 12),
        'from': from_pt,
        'to': to_pt,
        'edge': {
            'distance_label': f'{result.distance:.2f} m',
            'bearing_label': result.bearing_label,
            'from': from_pt,
            'to': to_pt,
        },
    }


def geocalc_map_json(result: BearingDistanceResult) -> str:
    return json.dumps(build_geocalc_map_context(result))
