"""CRS-to-CRS point transformation via pyproj."""
from __future__ import annotations

from dataclasses import dataclass, field

try:
    import pyproj
except ImportError:  # pragma: no cover
    pyproj = None


@dataclass
class TransformRow:
    index: int
    in_x: float
    in_y: float
    out_x: float
    out_y: float


@dataclass
class CrsTransformResult:
    preset: str
    preset_label: str
    source_crs: str
    target_crs: str
    source_geographic: bool
    target_geographic: bool
    rows: list[TransformRow] = field(default_factory=list)
    input_count: int = 0
    success_count: int = 0


def _crs_display(crs_input: str | int) -> str:
    if pyproj is None:
        return str(crs_input)
    try:
        crs = pyproj.CRS.from_user_input(crs_input)
        name = crs.name
        if name:
            return name
    except Exception:
        pass
    text = str(crs_input)
    return text if len(text) <= 80 else text[:77] + '...'


def _crs_props(crs_input: str | int) -> tuple[str, bool]:
    if pyproj is None:
        raise RuntimeError('pyproj is required for CRS transformation.')
    crs = pyproj.CRS.from_user_input(crs_input)
    return crs.to_string(), bool(crs.is_geographic)


def read_points_file(path: str) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    with open(path, encoding='utf-8', errors='replace') as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                points.append((float(parts[0]), float(parts[1])))
    return points


def transform_points(
    source_crs: str | int,
    target_crs: str | int,
    points: list[tuple[float, float]],
    preset: str = 'custom',
    preset_label_text: str = 'Custom',
) -> CrsTransformResult:
    if not points:
        raise ValueError('No points to transform.')

    if pyproj is None:
        raise RuntimeError('pyproj is not installed.')

    try:
        source_str, source_geo = _crs_props(source_crs)
        target_str, target_geo = _crs_props(target_crs)
        transformer = pyproj.Transformer.from_crs(
            source_crs, target_crs, always_xy=True,
        )
    except Exception as exc:
        raise ValueError(f'Invalid CRS definition: {exc}') from exc

    rows: list[TransformRow] = []
    for index, (x, y) in enumerate(points, start=1):
        try:
            out_x, out_y = transformer.transform(float(x), float(y))
        except Exception as exc:
            raise ValueError(f'Point {index} could not be transformed: {exc}') from exc
        rows.append(
            TransformRow(
                index=index,
                in_x=float(x),
                in_y=float(y),
                out_x=float(out_x),
                out_y=float(out_y),
            )
        )

    return CrsTransformResult(
        preset=preset,
        preset_label=preset_label_text,
        source_crs=source_str,
        target_crs=target_str,
        source_geographic=source_geo,
        target_geographic=target_geo,
        rows=rows,
        input_count=len(points),
        success_count=len(rows),
    )
