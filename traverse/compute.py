"""Traverse computation — latitudes, departures, misclosure, and Bowditch/transit adjustment."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Literal

from fayvadgeo.survey_math import dms_to_decimal, format_bearing_dms


AdjustmentMethod = Literal['compass', 'transit']
TraverseType = Literal['closed', 'open']


@dataclass
class LegInput:
    from_station: str
    to_station: str
    bearing_deg: float
    distance: float


@dataclass
class LegComputed:
    index: int
    from_station: str
    to_station: str
    bearing_deg: float
    distance: float
    latitude: float
    departure: float
    corr_latitude: float = 0.0
    corr_departure: float = 0.0
    adj_latitude: float = 0.0
    adj_departure: float = 0.0


@dataclass
class StationCoord:
    name: str
    easting: float
    northing: float


@dataclass
class TraverseResult:
    traverse_type: TraverseType
    method: AdjustmentMethod | None
    start_easting: float
    start_northing: float
    legs: list[LegComputed] = field(default_factory=list)
    stations: list[StationCoord] = field(default_factory=list)
    sum_latitude: float = 0.0
    sum_departure: float = 0.0
    misclosure_latitude: float = 0.0
    misclosure_departure: float = 0.0
    misclosure_linear: float = 0.0
    total_distance: float = 0.0
    precision_ratio: float | None = None
    precision_label: str = ''
    is_closed_within_tolerance: bool = False


def bearing_to_components(bearing_deg: float, distance: float) -> tuple[float, float]:
    """Whole-circle bearing (clockwise from north) to latitude and departure."""
    radians = math.radians(bearing_deg % 360.0)
    latitude = distance * math.cos(radians)
    departure = distance * math.sin(radians)
    return latitude, departure


def _compass_corrections(
    legs: list[LegComputed], misclosure_lat: float, misclosure_dep: float, total_dist: float
) -> None:
    if total_dist == 0:
        return
    for leg in legs:
        leg.corr_latitude = -misclosure_lat * (leg.distance / total_dist)
        leg.corr_departure = -misclosure_dep * (leg.distance / total_dist)


def _transit_corrections(
    legs: list[LegComputed], misclosure_lat: float, misclosure_dep: float
) -> None:
    sum_abs_lat = sum(abs(leg.latitude) for leg in legs)
    sum_abs_dep = sum(abs(leg.departure) for leg in legs)
    for leg in legs:
        if sum_abs_lat:
            leg.corr_latitude = -misclosure_lat * (abs(leg.latitude) / sum_abs_lat)
        if sum_abs_dep:
            leg.corr_departure = -misclosure_dep * (abs(leg.departure) / sum_abs_dep)


def _apply_adjustments(legs: list[LegComputed]) -> None:
    for leg in legs:
        leg.adj_latitude = leg.latitude + leg.corr_latitude
        leg.adj_departure = leg.departure + leg.corr_departure


def _propagate_coordinates(
    legs: list[LegComputed],
    start_name: str,
    start_e: float,
    start_n: float,
    use_adjusted: bool,
) -> list[StationCoord]:
    stations = [StationCoord(name=start_name, easting=start_e, northing=start_n)]
    e, n = start_e, start_n
    for leg in legs:
        lat = leg.adj_latitude if use_adjusted else leg.latitude
        dep = leg.adj_departure if use_adjusted else leg.departure
        e += dep
        n += lat
        stations.append(StationCoord(name=leg.to_station, easting=e, northing=n))
    return stations


def _precision_label(total_distance: float, linear_misclosure: float) -> tuple[float | None, str]:
    if linear_misclosure <= 0:
        return None, 'Perfect closure'
    ratio = total_distance / linear_misclosure
    rounded = int(round(ratio))
    return ratio, f'1:{rounded:,}'


def compute_traverse(
    legs_in: list[LegInput],
    start_station: str,
    start_easting: float,
    start_northing: float,
    traverse_type: TraverseType = 'closed',
    method: AdjustmentMethod = 'compass',
) -> TraverseResult:
    if len(legs_in) < 1:
        raise ValueError('At least one traverse leg is required.')

    legs: list[LegComputed] = []
    total_distance = 0.0
    sum_lat = 0.0
    sum_dep = 0.0

    for idx, leg_in in enumerate(legs_in, start=1):
        if leg_in.distance <= 0:
            raise ValueError(f'Leg {idx} ({leg_in.from_station} → {leg_in.to_station}): distance must be positive.')
        lat, dep = bearing_to_components(leg_in.bearing_deg, leg_in.distance)
        legs.append(
            LegComputed(
                index=idx,
                from_station=leg_in.from_station,
                to_station=leg_in.to_station,
                bearing_deg=leg_in.bearing_deg,
                distance=leg_in.distance,
                latitude=lat,
                departure=dep,
            )
        )
        total_distance += leg_in.distance
        sum_lat += lat
        sum_dep += dep

    result = TraverseResult(
        traverse_type=traverse_type,
        method=method if traverse_type == 'closed' else None,
        start_easting=start_easting,
        start_northing=start_northing,
        legs=legs,
        sum_latitude=sum_lat,
        sum_departure=sum_dep,
        misclosure_latitude=sum_lat,
        misclosure_departure=sum_dep,
        total_distance=total_distance,
    )
    result.misclosure_linear = math.hypot(sum_lat, sum_dep)
    ratio, label = _precision_label(total_distance, result.misclosure_linear)
    result.precision_ratio = ratio
    result.precision_label = label
    result.is_closed_within_tolerance = result.misclosure_linear < 0.001

    use_adjusted = False
    if traverse_type == 'closed':
        if method == 'transit':
            _transit_corrections(legs, sum_lat, sum_dep)
        else:
            _compass_corrections(legs, sum_lat, sum_dep, total_distance)
        _apply_adjustments(legs)
        use_adjusted = True

    result.stations = _propagate_coordinates(
        legs, start_station, start_easting, start_northing, use_adjusted=use_adjusted
    )
    return result
