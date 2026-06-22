from django.shortcuts import render
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
import os

from .forms import *
from .models import *
from .compute import (
    _convert_sheet,
    convert_data_custom,
    convert_data_custom_file,
)
from .crud import (
    add_control_formset,
    add_formset,
    add_in_params,
    delete_form,
    get_data_list,
    get_page,
    obj_create,
    obj_update,
    save_form,
)
from .map_utils import build_map_context


def handle_uploaded_file(infile, destfile):
    with open(destfile, 'wb+') as dest:
        for chunk in infile.chunks():
            dest.write(chunk)


def _results_context(retval, diagnostics=None, mode='sheet'):
    return {
        'data': retval,
        'diagnostics': diagnostics,
        'transform_mode': mode,
        'map_data': build_map_context(retval),
        'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }


def upload_file(request):
    if request.method == 'POST':
        form = GetInputFileForm(request.POST, request.FILES)
        if form.is_valid():
            destfile = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                'media/convert/file.asc',
            )
            handle_uploaded_file(request.FILES['source'], destfile)
            trtype = form.cleaned_data.get('trtype')
            method = form.cleaned_data.get('method', 'sheet')
            if method == 'custom':
                result = convert_data_custom_file(request, trtype, destfile)
                return render(
                    request,
                    'presentresults.html',
                    _results_context(result.as_legacy_retval(), result.diagnostics, mode='custom'),
                )
            sheetno = form.cleaned_data.get('shtno')
            result = _convert_sheet(request, sheetno, trtype, 'file')
            return render(
                request,
                'presentresults.html',
                _results_context(result.as_legacy_retval(), result.diagnostics, mode='sheet'),
            )
        return render(request, 'upload.html', {'form': form})
    return render(request, 'upload.html', {'form': GetInputFileForm()})


def enter_points(request):
    point_formset = add_formset(request, CPForm)
    control_formset = add_control_formset(request, ControlPairForm)
    in_form = add_in_params(request, GetInputForm)
    if not isinstance(in_form, list) or not isinstance(point_formset, list):
        return render(request, 'pointsentry.html', {
            'formset': [
                GetInputForm(),
                PointFormSet(),
                ControlPairFormSet(prefix='ctrl'),
            ],
        })

    method = in_form[0]
    trtype = in_form[1]
    sheetno = in_form[2] if len(in_form) > 2 else None

    if method == 'custom':
        if not isinstance(control_formset, list):
            return render(request, 'pointsentry.html', {
                'formset': [
                    GetInputForm(),
                    PointFormSet(),
                    ControlPairFormSet(prefix='ctrl'),
                ],
            })
        result = convert_data_custom(request, trtype, control_formset, point_formset)
        return render(
            request,
            'presentresults.html',
            _results_context(result.as_legacy_retval(), result.diagnostics, mode='custom'),
        )

    result = _convert_sheet(request, sheetno, trtype, 'form', form=point_formset)
    return render(
        request,
        'presentresults.html',
        _results_context(result.as_legacy_retval(), result.diagnostics, mode='sheet'),
    )


# Control Point CRUD Functionality
def get_controlpoint_list(request):
    page = get_page('Control Points', 'coords:controlpoint_create', 'Control Point')
    return get_data_list(request, ControlPoint, ControlPointForm, 'coords:controlpoint', page)


@staff_member_required
def controlpoint_list(request):
    data = get_controlpoint_list(request)
    return render(request, 'list.html', {'data': data})


@staff_member_required
def controlpoint_create(request):
    form, page = obj_create(request, ControlPointForm, ControlPoint, 'coords:controlpoint_create')
    return save_form(request, form, ControlPoint, page, 'coords:controlpoint', 'includes/partial_create.html')


@staff_member_required
def controlpoint_update(request, pk):
    form, page = obj_update(request, pk, ControlPointForm, ControlPoint, 'coords:controlpoint_update')
    return save_form(request, form, ControlPoint, page, 'coords:controlpoint', 'includes/partial_update.html')


@staff_member_required
def controlpoint_delete(request, pk):
    from django.http import JsonResponse
    url = reverse('coords:controlpoint_delete', args=(pk,))
    data = delete_form(request, pk, ControlPointForm, ControlPoint, url, 'coords:controlpoint')
    return JsonResponse(data)


# Sheet Reference CRUD Functionality
def get_sheetreference_list(request):
    page = get_page('Sheets', 'coords:sheetreference_create', 'Sheet')
    return get_data_list(request, SheetReference, SheetReferenceForm, 'coords:sheetreference', page)


@staff_member_required
def sheetreference_list(request):
    data = get_sheetreference_list(request)
    return render(request, 'list.html', {'data': data})


@staff_member_required
def sheetreference_create(request):
    form, page = obj_create(request, SheetReferenceForm, SheetReference, 'coords:sheetreference_create')
    return save_form(request, form, SheetReference, page, 'coords:sheetreference', 'includes/partial_create.html')


@staff_member_required
def sheetreference_update(request, pk):
    form, page = obj_update(request, pk, SheetReferenceForm, SheetReference, 'coords:sheetreference_update')
    return save_form(request, form, SheetReference, page, 'coords:sheetreference', 'includes/partial_update.html')


@staff_member_required
def sheetreference_delete(request, pk):
    from django.http import JsonResponse
    url = reverse('coords:sheetreference_delete', args=(pk,))
    data = delete_form(request, pk, SheetReferenceForm, SheetReference, url, 'coords:sheetreference')
    return JsonResponse(data)


# Transformation Request CRUD Functionality
def get_transrequest_list(request):
    page = get_page('Transformation Requests', 'coords:transrequest_create', 'Transformation Request')
    return get_data_list(request, TransRequest, TransRequestForm, 'coords:transrequest', page)


@staff_member_required
def transrequest_list(request):
    data = get_transrequest_list(request)
    return render(request, 'list.html', {'data': data})


@staff_member_required
def transrequest_create(request):
    form, page = obj_create(request, TransRequestForm, TransRequest, 'coords:transrequest_create')
    return save_form(request, form, TransRequest, page, 'coords:transrequest', 'includes/partial_create.html')


@staff_member_required
def transrequest_update(request, pk):
    form, page = obj_update(request, pk, TransRequestForm, TransRequest, 'coords:transrequest_update')
    return save_form(request, form, TransRequest, page, 'coords:transrequest', 'includes/partial_update.html')


@staff_member_required
def transrequest_delete(request, pk):
    from django.http import JsonResponse
    url = reverse('coords:transrequest_delete', args=(pk,))
    data = delete_form(request, pk, TransRequestForm, TransRequest, url, 'coords:transrequest')
    return JsonResponse(data)
