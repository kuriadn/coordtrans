from django.conf import settings
from django.shortcuts import render

from .compute import LegInput, compute_traverse
from .forms import TraverseLegFormSet, TraverseSetupForm
from .map_utils import build_traverse_map_context


def _empty_context():
    return {
        'setup_form': TraverseSetupForm(),
        'leg_formset': TraverseLegFormSet(prefix='legs'),
    }


def adjust_traverse(request):
    if request.method == 'POST':
        setup_form = TraverseSetupForm(request.POST)
        leg_formset = TraverseLegFormSet(request.POST, prefix='legs')

        if setup_form.is_valid() and leg_formset.is_valid():
            legs_in = []
            for form in leg_formset:
                if not form.cleaned_data:
                    continue
                legs_in.append(
                    LegInput(
                        from_station=form.cleaned_data['from_station'].strip(),
                        to_station=form.cleaned_data['to_station'].strip(),
                        bearing_deg=form.leg_bearing_decimal(),
                        distance=float(form.cleaned_data['distance']),
                    )
                )

            if not legs_in:
                leg_formset.add_error(None, 'Enter at least one traverse leg.')
            else:
                try:
                    result = compute_traverse(
                        legs_in=legs_in,
                        start_station=setup_form.cleaned_data['start_station'].strip(),
                        start_easting=float(setup_form.cleaned_data['start_easting']),
                        start_northing=float(setup_form.cleaned_data['start_northing']),
                        traverse_type=setup_form.cleaned_data['traverse_type'],
                        method=setup_form.cleaned_data.get('method') or 'compass',
                    )
                except ValueError as exc:
                    setup_form.add_error(None, str(exc))
                else:
                    return render(
                        request,
                        'traverse/results.html',
                        {
                            'result': result,
                            'setup': setup_form.cleaned_data,
                            'map_data': build_traverse_map_context(result),
                            'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
                        },
                    )

        return render(
            request,
            'traverse/enter.html',
            {
                'setup_form': setup_form,
                'leg_formset': leg_formset,
            },
        )

    return render(request, 'traverse/enter.html', _empty_context())
