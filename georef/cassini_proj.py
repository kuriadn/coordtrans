"""Cassini panel central meridian and PROJ4 helpers."""
from __future__ import annotations

import re
from math import floor


def panel_central_meridian(longitude: float) -> float:
    """Return panel central meridian for a geographic longitude (NLIMS rule)."""
    l = floor(longitude)
    if ((l + 1) / 2.0 - floor((l + 1) / 2.0)) > 0.01:
        return l + 1
    return l


def cassini_proj4_with_cm(central_meridian: float, base_proj4: str) -> str:
    """Replace lon_0 in a Cassini PROJ4 string with the given central meridian."""
    if '+lon_0=' not in base_proj4:
        return base_proj4
    return re.sub(r'\+lon_0=[^\s+]+', f'+lon_0={central_meridian}', base_proj4)
