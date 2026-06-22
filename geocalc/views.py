from django.conf import settings
from django.shortcuts import render

from .compute import forward_polar, inverse_join
from .forms import BearingDistanceForm
from .map_utils import build_geocalc_map_context


def compute_bearing_distance(request):
    if request.method == 'POST':
        form = BearingDistanceForm(request.POST)
        if form.is_valid():
            mode = form.cleaned_data['mode']
            try:
                if mode == 'forward':
                    result = forward_polar(
                        from_label=form.cleaned_data['from_label'].strip(),
                        from_e=float(form.cleaned_data['from_easting']),
                        from_n=float(form.cleaned_data['from_northing']),
                        to_label=form.cleaned_data['to_label'].strip(),
                        bearing_deg=form.bearing_decimal(),
                        distance=float(form.cleaned_data['distance']),
                    )
                else:
                    result = inverse_join(
                        from_label=form.cleaned_data['from_label'].strip(),
                        from_e=float(form.cleaned_data['from_easting']),
                        from_n=float(form.cleaned_data['from_northing']),
                        to_label=form.cleaned_data['to_label'].strip(),
                        to_e=float(form.cleaned_data['to_easting']),
                        to_n=float(form.cleaned_data['to_northing']),
                    )
            except ValueError as exc:
                form.add_error(None, str(exc))
            else:
                return render(
                    request,
                    'geocalc/results.html',
                    {
                        'result': result,
                        'form_data': form.cleaned_data,
                        'map_data': build_geocalc_map_context(result),
                        'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
                    },
                )
    else:
        form = BearingDistanceForm()

    return render(request, 'geocalc/enter.html', {'form': form})
