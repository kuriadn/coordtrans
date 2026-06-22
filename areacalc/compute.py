"""Polygon area and perimeter from boundary coordinates."""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class VertexInput:
    label: str
    easting: float
    northing: float


@dataclass
class VertexResult:
    index: int
    label: str
    easting: float
    northing: float


@dataclass
class EdgeResult:
    index: int
    from_label: str
    to_label: str
    easting_from: float
    northing_from: float
    easting_to: float
    northing_to: float
    distance: float
    bearing_deg: float


@dataclass
class AreaResult:
    parcel_name: str
    closed: bool
    vertices: list[VertexResult] = field(default_factory=list)
    edges: list[EdgeResult] = field(default_factory=list)
    area_sq_m: float | None = None
    area_hectares: float | None = None
    area_acres: float | None = None
    perimeter_m: float = 0.0


from fayvadgeo.survey_math import format_bearing_dms


def _edge_components(e1: float, n1: float, e2: float, n2: float) -> tuple[float, float, float]:
    dep = e2 - e1
    lat = n2 - n1
    distance = math.hypot(dep, lat)
    bearing = math.degrees(math.atan2(dep, lat)) % 360.0
    return distance, bearing, dep


def _shoelace_area(vertices: list[VertexResult]) -> float:
    n = len(vertices)
    twice = 0.0
    for i in range(n):
        j = (i + 1) % n
        twice += vertices[i].easting * vertices[j].northing
        twice -= vertices[j].easting * vertices[i].northing
    return abs(twice) / 2.0


def compute_area_perimeter(
    vertices_in: list[VertexInput],
    parcel_name: str = '',
    closed: bool = True,
) -> AreaResult:
    if len(vertices_in) < 2:
        raise ValueError('At least two boundary points are required.')
    if closed and len(vertices_in) < 3:
        raise ValueError('A closed parcel needs at least three boundary points.')

    vertices = [
        VertexResult(index=i + 1, label=v.label, easting=v.easting, northing=v.northing)
        for i, v in enumerate(vertices_in)
    ]

    edges: list[EdgeResult] = []
    perimeter = 0.0
    edge_count = len(vertices) if closed else len(vertices) - 1

    for i in range(edge_count):
        a = vertices[i]
        b = vertices[(i + 1) % len(vertices)]
        distance, bearing, _ = _edge_components(a.easting, a.northing, b.easting, b.northing)
        if distance <= 0:
            raise ValueError(f'Edge {a.label} → {b.label} has zero length — remove duplicate points.')
        perimeter += distance
        edges.append(
            EdgeResult(
                index=i + 1,
                from_label=a.label,
                to_label=b.label,
                easting_from=a.easting,
                northing_from=a.northing,
                easting_to=b.easting,
                northing_to=b.northing,
                distance=distance,
                bearing_deg=bearing,
            )
        )

    area_sq_m = _shoelace_area(vertices) if closed else None
    area_ha = area_sq_m / 10000.0 if area_sq_m is not None else None
    area_acres = area_sq_m / 4046.8564224 if area_sq_m is not None else None

    return AreaResult(
        parcel_name=parcel_name.strip(),
        closed=closed,
        vertices=vertices,
        edges=edges,
        area_sq_m=area_sq_m,
        area_hectares=area_ha,
        area_acres=area_acres,
        perimeter_m=perimeter,
    )
