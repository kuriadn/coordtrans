"""Shared angle and DMS helpers for survey calculator apps."""
from __future__ import annotations

import math


def dms_to_decimal(degrees: int, minutes: int, seconds: float) -> float:
    sign = -1 if degrees < 0 else 1
    return sign * (abs(degrees) + minutes / 60.0 + seconds / 3600.0)


def dec_deg(degrees: float, minutes: int = 0, seconds: float = 0) -> float:
    sign = 1 if degrees >= 0 else -1
    dg = abs(degrees)
    return (dg + minutes / 60.0 + seconds / 3600.0) * sign


def deg_min_sec(degrees: float) -> list[float]:
    sign = 1 if degrees >= 0 else -1
    dg = abs(degrees)
    d = int(math.floor(dg))
    minutes = (dg - d) * 60.0
    m = int(math.floor(minutes))
    s = (minutes - m) * 60.0
    return [sign * d, m, s]


def format_bearing_dms(bearing_deg: float) -> str:
    bearing = bearing_deg % 360.0
    degrees = int(bearing)
    minutes_float = (bearing - degrees) * 60.0
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60.0
    return f'{degrees}°{minutes:02d}\'{seconds:05.2f}"'


def deg2rad(degrees: float) -> float:
    return degrees * math.pi / 180.0


def rad2deg(radians: float) -> float:
    return radians * 180.0 / math.pi


def get_sign(value: float) -> int:
    return -1 if value < 0 else 1
