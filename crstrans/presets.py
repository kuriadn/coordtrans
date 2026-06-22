"""CRS preset definitions — defaults from project settings."""
from __future__ import annotations

from django.conf import settings


def _cassini_proj4() -> str:
    return getattr(
        settings,
        'MAP_CASSINI_PROJ4',
        '+proj=cass +lat_0=0 +lon_0=37.0 +k=0.99975 +x_0=500000 +y_0=0 '
        '+ellps=clrk80 +towgs84=-205,-48,153,0,0,0,0 +units=m +no_defs',
    )


def _utm_epsg() -> int:
    return int(getattr(settings, 'MAP_UTM_EPSG', 32637))


PRESET_CHOICES = (
    ('cassini-utm', 'Cassini-Soldner → UTM 37N (default)'),
    ('utm-cassini', 'UTM 37N → Cassini-Soldner'),
    ('utm-wgs84', 'UTM 37N → WGS84 (lat/lon)'),
    ('cassini-wgs84', 'Cassini-Soldner → WGS84 (lat/lon)'),
    ('wgs84-utm', 'WGS84 (lat/lon) → UTM 37N'),
    ('custom', 'Custom PROJ4 / EPSG'),
)


def resolve_preset(preset_key: str) -> tuple[str, str | int]:
    cass = _cassini_proj4()
    utm = _utm_epsg()
    mapping = {
        'cassini-utm': (cass, utm),
        'utm-cassini': (utm, cass),
        'utm-wgs84': (utm, 4326),
        'cassini-wgs84': (cass, 4326),
        'wgs84-utm': (4326, utm),
    }
    if preset_key not in mapping:
        raise ValueError(f'Unknown preset: {preset_key}')
    return mapping[preset_key]


def preset_label(preset_key: str) -> str:
    for key, label in PRESET_CHOICES:
        if key == preset_key:
            return label
    return preset_key
