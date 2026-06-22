from django.conf import settings
from django.shortcuts import render

from .compute import VertexInput, compute_area_perimeter
from .forms import BoundaryPointFormSet, ParcelSetupForm
from .map_utils import build_area_map_context


def compute_parcel(request):
    if request.method == 'POST':
        setup_form = ParcelSetupForm(request.POST)
        point_formset = BoundaryPointFormSet(request.POST, prefix='pts')

        if setup_form.is_valid() and point_formset.is_valid():
            vertices_in = []
            for form in point_formset:
                if not form.cleaned_data:
                    continue
                vertices_in.append(
                    VertexInput(
                        label=form.cleaned_data['label'].strip(),
                        easting=float(form.cleaned_data['easting']),
                        northing=float(form.cleaned_data['northing']),
                    )
                )

            if len(vertices_in) < 2:
                point_formset.add_error(None, 'Enter at least two boundary points.')
            else:
                try:
                    result = compute_area_perimeter(
                        vertices_in=vertices_in,
                        parcel_name=setup_form.cleaned_data.get('parcel_name', ''),
                        closed=setup_form.cleaned_data.get('closed', True),
                    )
                except ValueError as exc:
                    setup_form.add_error(None, str(exc))
                else:
                    return render(
                        request,
                        'areacalc/results.html',
                        {
                            'result': result,
                            'setup': setup_form.cleaned_data,
                            'map_data': build_area_map_context(result),
                            'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
                        },
                    )

        return render(
            request,
            'areacalc/enter.html',
            {
                'setup_form': setup_form,
                'point_formset': point_formset,
            },
        )

    return render(
        request,
        'areacalc/enter.html',
        {
            'setup_form': ParcelSetupForm(),
            'point_formset': BoundaryPointFormSet(prefix='pts'),
        },
    )
