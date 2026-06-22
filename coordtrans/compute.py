"""Sheet-based and custom affine coordinate transformation."""
from __future__ import annotations

import os

import numpy as np

from coordtrans.models import SheetReference, TransRequest
from georef.affine import (
    AffineDiagnostics,
    AffineTransformResult,
    apply_affine,
    diagnostics_from_fit,
    fit_affine,
    gen_coeff_matrix,
    parse_affine_file,
    read_convert_file,
    transform_with_controls,
)

__all__ = [
    'AffineDiagnostics',
    'AffineTransformResult',
    'convert_data',
    'convert_data_custom',
    'convert_data_custom_file',
    'read_convert_file',
    'store_transaction',
]


def _target_label(trtype: str) -> str:
    return 'Cassini' if trtype == 'cass' else 'U.T.M'


def _sheet_controls(sheet: SheetReference, trtype: str) -> tuple[np.ndarray, np.ndarray]:
    cass = []
    utm = []
    for pt in (sheet.pt1, sheet.pt2, sheet.pt3, sheet.pt4):
        cass.extend([float(pt.cass_x), float(pt.cass_y)])
        utm.extend([float(pt.utm_x), float(pt.utm_y)])
    if trtype == 'cass':
        return np.array(utm), np.array(cass)
    return np.array(cass), np.array(utm)


def _get_min_max(sheet_no: str, trtype: str) -> tuple[list, list]:
    sheet = SheetReference.objects.get(shtno=sheet_no)
    xpts = []
    ypts = []
    for pt in (sheet.pt1, sheet.pt2, sheet.pt3, sheet.pt4):
        if trtype == 'utm':
            xpts.append(pt.cass_x)
            ypts.append(pt.cass_y)
        else:
            xpts.append(pt.utm_x)
            ypts.append(pt.utm_y)
    xpts.sort()
    ypts.sort()
    return [xpts[0], ypts[0]], [xpts[3], ypts[3]]


def _point_in_bbox(minpt, maxpt, x, y) -> bool:
    return (
        float(minpt[0]) <= float(x) <= float(maxpt[0])
        and float(minpt[1]) <= float(y) <= float(maxpt[1])
    )


def _filter_points_in_sheet(
    sheet_no: str, conv: np.ndarray, trtype: str, active: bool,
) -> tuple[np.ndarray, list]:
    minpt, maxpt = _get_min_max(sheet_no, trtype)
    pts = len(conv) // 2
    n = pts if active else min(pts, 5)
    in_conv = []
    ptmap = []
    cnt = 0
    for i in range(n):
        if _point_in_bbox(minpt, maxpt, conv[2 * i], conv[2 * i + 1]):
            ptmap.append([i, cnt])
            in_conv.extend([conv[2 * i], conv[2 * i + 1]])
            cnt += 1
    return np.array(in_conv), ptmap


def convert_data(
    request,
    sheetno: str,
    trtype: str,
    source: str,
    form=None,
) -> list:
    """Sheet-based affine transform; returns legacy [meta, rows|error] list."""
    result = _convert_sheet(request, sheetno, trtype, source, form)
    return result.as_legacy_retval()


def _convert_sheet(
    request,
    sheetno: str,
    trtype: str,
    source: str,
    form=None,
) -> AffineTransformResult:
    target = _target_label(trtype)
    try:
        sheets = SheetReference.objects.filter(shtno=sheetno)
        if not sheets:
            return AffineTransformResult(
                target_label=target,
                mode='sheet',
                sheet_no=sheetno,
                input_count=0,
                transformed_count=0,
                rows=[],
                error_message='No sheet found',
            )
        sheet = sheets[0]
        source_coords, target_coords = _sheet_controls(sheet, trtype)
        coeff, residuals, ata_inv = fit_affine(source_coords, target_coords)
        diag = diagnostics_from_fit(coeff, residuals, ata_inv)

        if source == 'file':
            media_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                'media/convert/file.asc',
            )
            conv = read_convert_file(media_path)
        else:
            conv = np.array(form, dtype=float)

        in_conv, ptmap = _filter_points_in_sheet(sheetno, conv, trtype, active=True)
        input_count = len(conv) // 2

        if len(in_conv) == 0:
            store_transaction(request, sheetno, target, input_count, 0)
            msg = (
                'Input file format is suspect. Transformation aborted'
                if input_count == 0
                else 'All points to be transformed fall outside the sheet. Transformation aborted'
            )
            return AffineTransformResult(
                target_label=target,
                mode='sheet',
                sheet_no=sheetno,
                input_count=input_count,
                transformed_count=0,
                rows=[],
                diagnostics=diag,
                error_message=msg,
            )

        trans = apply_affine(coeff, in_conv)
        rows = []
        cnt = 0
        for i in range(input_count):
            orig = [float(conv[2 * i]), float(conv[2 * i + 1])]
            if any(m[0] == i for m in ptmap):
                out = [float(trans[2 * cnt]), float(trans[2 * cnt + 1])]
                cnt += 1
                rows.append([orig, out])
            else:
                rows.append([orig, 'Point outside sheet - Not transformed'])

        store_transaction(request, sheetno, target, input_count, cnt)
        return AffineTransformResult(
            target_label=target,
            mode='sheet',
            sheet_no=sheetno,
            input_count=input_count,
            transformed_count=cnt,
            rows=rows,
            diagnostics=diag,
        )
    except (ValueError, SheetReference.DoesNotExist):
        store_transaction(request, sheetno, target, 0, 0)
        return AffineTransformResult(
            target_label=target,
            mode='sheet',
            sheet_no=sheetno,
            input_count=0,
            transformed_count=0,
            rows=[],
            error_message='Input file is not a text file. Transformation aborted',
        )


def convert_data_custom(
    request,
    trtype: str,
    control_pairs: list[float],
    points: list[float],
) -> AffineTransformResult:
    source_controls = []
    target_controls = []
    for i in range(0, len(control_pairs), 4):
        source_controls.extend(control_pairs[i:i + 2])
        target_controls.extend(control_pairs[i + 2:i + 4])
    result = transform_with_controls(
        source_controls=source_controls,
        target_controls=target_controls,
        points=points,
        target_label=_target_label(trtype),
        mode='custom',
    )
    store_transaction(request, 'Custom', result.target_label, result.input_count, result.transformed_count)
    return result


def convert_data_custom_file(request, trtype: str, path: str) -> AffineTransformResult:
    source_controls, target_controls, points = parse_affine_file(path)
    result = transform_with_controls(
        source_controls=source_controls.tolist(),
        target_controls=target_controls.tolist(),
        points=points.tolist(),
        target_label=_target_label(trtype),
        mode='custom',
    )
    store_transaction(request, 'Custom', result.target_label, result.input_count, result.transformed_count)
    return result


def store_transaction(request, sheet_no, target_label, inpoints, points) -> None:
    if not getattr(request.user, 'is_authenticated', False):
        return
    if sheet_no == 'Custom':
        return
    try:
        sheet = SheetReference.objects.get(shtno=sheet_no)
    except SheetReference.DoesNotExist:
        return
    from django.utils import timezone
    tr = 'cass' if target_label == 'Cassini' else 'utm'
    trans = TransRequest()
    trans.user = request.user
    trans.sheet = sheet
    trans.trtype = tr
    trans.inpoints = inpoints
    trans.points = points
    trans.datedone = timezone.now()
    trans.save()
