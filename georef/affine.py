"""Affine least-squares coordinate transformation (4-parameter)."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.linalg import inv


def gen_coeff_matrix(coords: np.ndarray) -> np.ndarray:
    n = len(coords)
    mat = []
    j = 0
    for _ in range(n // 2):
        mat.append([coords[j * 2], -coords[j * 2 + 1], 1, 0])
        mat.append([coords[j * 2 + 1], coords[j * 2], 0, 1])
        j += 1
    return np.array(mat)


def fit_affine(source: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (coefficients, residuals, inverse ATA)."""
    a_matrix = gen_coeff_matrix(source)
    l_vector = np.transpose(target)
    at = np.transpose(a_matrix)
    ata = np.dot(at, a_matrix)
    atl = np.dot(at, l_vector)
    ata_inv = inv(ata)
    coeff = np.dot(ata_inv, atl)
    fitted = np.dot(a_matrix, coeff)
    residuals = fitted - l_vector
    return coeff, residuals, ata_inv


def apply_affine(coeff: np.ndarray, points: np.ndarray) -> np.ndarray:
    b_matrix = gen_coeff_matrix(points)
    return np.dot(b_matrix, coeff)


def parse_affine_file(path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Read control pairs (4 columns) and points to transform (2 columns)."""
    source = []
    target = []
    convert = []
    with open(path, encoding='utf-8', errors='replace') as handle:
        for line in handle:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) > 3:
                source.append(float(parts[0]))
                source.append(float(parts[1]))
                target.append(float(parts[2]))
                target.append(float(parts[3]))
            elif len(parts) >= 2 and parts[0] and parts[1]:
                convert.append(float(parts[0]))
                convert.append(float(parts[1]))
    return np.array(source), np.array(target), np.array(convert)


def read_convert_file(path: str) -> np.ndarray:
    """Read two-column point file."""
    convert = []
    with open(path, encoding='utf-8', errors='replace') as handle:
        for line in handle:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2 and parts[0] and parts[1]:
                convert.append(float(parts[0]))
                convert.append(float(parts[1]))
    return np.array(convert)


@dataclass
class AffineDiagnostics:
    scale: float
    rotation: float
    translate_x: float
    translate_y: float
    residuals: list[float] = field(default_factory=list)
    ata_inverse: list[list[float]] = field(default_factory=list)


def diagnostics_from_fit(
    coeff: np.ndarray, residuals: np.ndarray, ata_inv: np.ndarray,
) -> AffineDiagnostics:
    return AffineDiagnostics(
        scale=float(coeff[0]),
        rotation=float(coeff[1]),
        translate_x=float(coeff[2]),
        translate_y=float(coeff[3]),
        residuals=[float(v) for v in residuals],
        ata_inverse=[[float(v) for v in row] for row in ata_inv],
    )


@dataclass
class AffineTransformResult:
    target_label: str
    mode: str
    sheet_no: str
    input_count: int
    transformed_count: int
    rows: list
    diagnostics: AffineDiagnostics | None = None
    error_message: str | None = None
    control_rows: list | None = None

    def as_legacy_retval(self) -> list:
        """Template-compatible [meta, rows|error] structure."""
        pre = [self.sheet_no, self.target_label, self.input_count, self.transformed_count]
        if self.error_message:
            return [pre, self.error_message]
        return [pre, self.rows]


def transform_with_controls(
    source_controls: list[float],
    target_controls: list[float],
    points: list[float],
    target_label: str = 'Target',
    mode: str = 'custom',
    sheet_no: str = 'Custom',
) -> AffineTransformResult:
    if len(source_controls) < 4 or len(target_controls) < 4:
        return AffineTransformResult(
            target_label=target_label,
            mode=mode,
            sheet_no=sheet_no,
            input_count=len(points) // 2,
            transformed_count=0,
            rows=[],
            error_message='At least two control point pairs are required.',
        )
    if len(points) < 2:
        return AffineTransformResult(
            target_label=target_label,
            mode=mode,
            sheet_no=sheet_no,
            input_count=0,
            transformed_count=0,
            rows=[],
            error_message='Enter at least one point to transform.',
        )

    x = np.array(source_controls, dtype=float)
    l = np.array(target_controls, dtype=float)
    conv = np.array(points, dtype=float)
    coeff, residuals, ata_inv = fit_affine(x, l)
    trans = apply_affine(coeff, conv)
    diag = diagnostics_from_fit(coeff, residuals, ata_inv)

    rows = []
    for i in range(len(conv) // 2):
        rows.append([
            [float(conv[2 * i]), float(conv[2 * i + 1])],
            [float(trans[2 * i]), float(trans[2 * i + 1])],
        ])

    control_rows = []
    for i in range(len(x) // 2):
        control_rows.append([
            [float(x[2 * i]), float(x[2 * i + 1])],
            [float(l[2 * i]), float(l[2 * i + 1])],
        ])

    return AffineTransformResult(
        target_label=target_label,
        mode=mode,
        sheet_no=sheet_no,
        input_count=len(conv) // 2,
        transformed_count=len(rows),
        rows=rows,
        diagnostics=diag,
        control_rows=control_rows,
    )
