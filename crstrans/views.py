from django.conf import settings
from django.shortcuts import render

from .compute import read_points_file, transform_points, transform_points_tables
from .forms import CrsFileForm, CrsPointFormSet, CrsSetupForm
from .map_utils import build_crs_map_context
from .presets import is_table_preset, preset_label


def _results_context(result):
    return {
        'result': result,
        'map_data': build_crs_map_context(result),
        'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }


def _run_transform(setup_form, points):
    preset = setup_form.cleaned_data['preset']
    if is_table_preset(preset):
        return transform_points_tables(
            preset=preset,
            points=points,
            central_meridian=float(setup_form.cleaned_data['central_meridian']),
            preset_label_text=preset_label(preset),
        )
    source, target = setup_form.resolve_crs_pair()
    return transform_points(
        source_crs=source,
        target_crs=target,
        points=points,
        preset=preset,
        preset_label_text=preset_label(preset),
    )


def transform_points_view(request):
    if request.method == 'POST':
        setup_form = CrsSetupForm(request.POST)
        point_formset = CrsPointFormSet(request.POST, prefix='pts')

        if setup_form.is_valid() and point_formset.is_valid():
            points = []
            for form in point_formset:
                if not form.cleaned_data:
                    continue
                points.append(
                    (float(form.cleaned_data['easting']), float(form.cleaned_data['northing']))
                )
            if not points:
                point_formset.add_error(None, 'Enter at least one point.')
            else:
                try:
                    result = _run_transform(setup_form, points)
                except ValueError as exc:
                    setup_form.add_error(None, str(exc))
                else:
                    return render(request, 'crstrans/results.html', _results_context(result))

        return render(
            request,
            'crstrans/enter.html',
            {'setup_form': setup_form, 'point_formset': point_formset},
        )

    return render(
        request,
        'crstrans/enter.html',
        {
            'setup_form': CrsSetupForm(),
            'point_formset': CrsPointFormSet(prefix='pts'),
        },
    )


def transform_file_view(request):
    if request.method == 'POST':
        form = CrsFileForm(request.POST, request.FILES)
        if form.is_valid():
            import os
            import tempfile

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
            try:
                for chunk in form.cleaned_data['source'].chunks():
                    tmp.write(chunk)
                tmp.close()
                points = read_points_file(tmp.name)
            finally:
                os.unlink(tmp.name)

            if not points:
                form.add_error('source', 'No valid coordinate pairs found in file.')
            else:
                try:
                    result = _run_transform(form, points)
                except ValueError as exc:
                    form.add_error(None, str(exc))
                else:
                    return render(request, 'crstrans/results.html', _results_context(result))
    else:
        form = CrsFileForm()

    return render(request, 'crstrans/upload.html', {'form': form})
