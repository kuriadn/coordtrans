"""Map display for traverse results — geographic (UTM→WGS84) or local plan view."""
from __future__ import annotations

import json
from typing import Any

from django.conf import settings

from coordtrans.map_utils import _en_to_wgs84, _utm_epsg

from .compute import TraverseResult, format_bearing_dms


def _station_point(name: str, easting: float, northing: float, epsg) -> dict[str, Any]:
    geo = _en_to_wgs84(easting, northing, epsg)
    return {
        'name': name,
        'e': round(float(easting), 3),
        'n': round(float(northing), 3),
        'lat': geo['lat'] if geo else None,
        'lng': geo['lng'] if geo else None,
    }


def build_traverse_map_context(result: TraverseResult) -> dict[str, Any]:
    epsg = _utm_epsg()
    stations = [
        _station_point(st.name, st.easting, st.northing, epsg)
        for st in result.stations
    ]
    georef_ok = all(st.get('lat') is not None for st in stations)
    mode = 'geographic' if georef_ok else 'plan'

    station_by_name = {st['name']: st for st in stations}
    legs_out = []
    for leg in result.legs:
        from_pt = station_by_name.get(leg.from_station)
        to_pt = station_by_name.get(leg.to_station)
        if not from_pt or not to_pt:
            continue
        legs_out.append({
            'index': leg.index,
            'from_station': leg.from_station,
            'to_station': leg.to_station,
            'bearing_deg': round(leg.bearing_deg, 6),
            'bearing_label': format_bearing_dms(leg.bearing_deg),
            'distance': round(leg.distance, 3),
            'distance_label': f'{leg.distance:.2f} m',
            'from': from_pt,
            'to': to_pt,
        })

    return {
        'mode': mode,
        'traverse_type': result.traverse_type,
        'georef_ok': georef_ok,
        'google_maps_enabled': bool(getattr(settings, 'GOOGLE_MAPS_API_KEY', '')),
        'default_center': getattr(settings, 'MAP_DEFAULT_CENTER', [-1.286389, 36.817223]),
        'default_zoom': getattr(settings, 'MAP_DEFAULT_ZOOM', 12),
        'stations': stations,
        'legs': legs_out,
    }


def traverse_map_json(result: TraverseResult) -> str:
    return json.dumps(build_traverse_map_context(result))
