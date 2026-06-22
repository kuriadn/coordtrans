#!/usr/bin/env python3
"""CLI affine transformation — thin wrapper over georef.affine."""
from __future__ import annotations

import argparse
import sys

import numpy as np

from georef.affine import apply_affine, diagnostics_from_fit, fit_affine, parse_affine_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Affine coordinate transformation from CSV control points.')
    parser.add_argument('-i', '--input', required=True, help='Input CSV file')
    parser.add_argument('-o', '--output', help='Optional output file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print parameters and residuals')
    args = parser.parse_args(argv)

    source, target, points = parse_affine_file(args.input)
    if len(source) < 4:
        print('At least two control point pairs (four columns) are required.', file=sys.stderr)
        return 1

    coeff, residuals, ata_inv = fit_affine(source, target)
    diag = diagnostics_from_fit(coeff, residuals, ata_inv)
    lines: list[str] = []

    if args.verbose:
        lines.append('Transformation Parameters')
        lines.append(f'{diag.scale:8.5f}, {diag.rotation:12.8f}, {diag.translate_x:12.2f}, {diag.translate_y:12.2f}')
        lines.append('Transformation Errors')
        lines.extend(f'{r:6.3f}' for r in diag.residuals)

    if len(points) > 0:
        trans = apply_affine(coeff, points)
        lines.append('Transformed Coordinates: Original vs Transformed list')
        for i in range(len(points) // 2):
            lines.append(
                f'{points[2*i]:12.2f}, {points[2*i+1]:12.2f}, '
                f'{trans[2*i]:12.2f}, {trans[2*i+1]:12.2f}'
            )

    output = '\n'.join(lines)
    if args.verbose or not args.output:
        print(output)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as handle:
            handle.write(output + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
