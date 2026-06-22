"""Forward (polar) and inverse (join) bearing–distance computations."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal


ComputationMode = Literal['forward', 'inverse']


@dataclass
class PointCoord:
    label: str
    easting: float
    northing: float


@dataclass
class BearingDistanceResult:
    mode: ComputationMode
    from_point: PointCoord
    to_point: PointCoord
    bearing_deg: float
    bearing_label: str
    distance: float
    latitude: float
    departure: float


def dms_to_decimal(degrees: int, minutes: int, seconds: float) -> float:
    sign = -1 if degrees < 0 else 1
    return sign * (abs(degrees) + minutes / 60.0 + seconds / 3600.0)


def format_bearing_dms(bearing_deg: float) -> str:
    bearing = bearing_deg % 360.0
    degrees = int(bearing)
    minutes_float = (bearing - degrees) * 60.0
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60.0
    return f'{degrees}°{minutes:02d}\'{seconds:05.2f}"'


def _components(bearing_deg: float, distance: float) -> tuple[float, float]:
    radians = math.radians(bearing_deg % 360.0)
    latitude = distance * math.cos(radians)
    departure = distance * math.sin(radians)
    return latitude, departure


def _bearing_distance(e1: float, n1: float, e2: float, n2: float) -> tuple[float, float, float, float]:
    departure = e2 - e1
    latitude = n2 - n1
    distance = math.hypot(departure, latitude)
    bearing = math.degrees(math.atan2(departure, latitude)) % 360.0
    return distance, bearing, latitude, departure


def forward_polar(
    from_label: str,
    from_e: float,
    from_n: float,
    to_label: str,
    bearing_deg: float,
    distance: float,
) -> BearingDistanceResult:
    if distance <= 0:
        raise ValueError('Distance must be greater than zero.')
    lat, dep = _components(bearing_deg, distance)
    to_e = from_e + dep
    to_n = from_n + lat
    return BearingDistanceResult(
        mode='forward',
        from_point=PointCoord(from_label, from_e, from_n),
        to_point=PointCoord(to_label, to_e, to_n),
        bearing_deg=bearing_deg % 360.0,
        bearing_label=format_bearing_dms(bearing_deg),
        distance=distance,
        latitude=lat,
        departure=dep,
    )


def inverse_join(
    from_label: str,
    from_e: float,
    from_n: float,
    to_label: str,
    to_e: float,
    to_n: float,
) -> BearingDistanceResult:
    distance, bearing, lat, dep = _bearing_distance(from_e, from_n, to_e, to_n)
    if distance <= 0:
        raise ValueError('The two points are coincident — distance is zero.')
    return BearingDistanceResult(
        mode='inverse',
        from_point=PointCoord(from_label, from_e, from_n),
        to_point=PointCoord(to_label, to_e, to_n),
        bearing_deg=bearing,
        bearing_label=format_bearing_dms(bearing),
        distance=distance,
        latitude=lat,
        departure=dep,
    )
