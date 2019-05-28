from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.conf import settings
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
import os
from .forms import *
from .models import *
from ultigeo.georef import *

def handle_uploaded_file(infile, destfile):
  with open(destfile, 'wb+') as dest:
  	for chunk in infile.chunks():
  	  dest.write(chunk)

@login_required
def upload_file(request):
  if request.method == 'POST':
  	form = GetInputFileForm(request.POST, request.FILES)
  	if form.is_valid():
  	  destfile = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'media/convert/file.asc')
  	  handle_uploaded_file(request.FILES['source'], destfile)
  	  sheetno = form.cleaned_data.get('shtno')
  	  trtype = form.cleaned_data.get('trtype')
  	  retval = convertData(request, sheetno, trtype, 'file')
  	  return render(request, 'presentresults.html', {'data': retval})
  	else:
  	  form = GetInputFileForm()
  	  return render(request, 'upload.html', {'form': form})  
  else:
  	form = GetInputFileForm()
  	return render(request, 'upload.html', {'form': form})

@login_required
def enter_points(request):
  formset = add_formset(request, CPForm)
  inForm = add_inParams(request)
  forms = []
  if type(inForm) != list or type(formset) != list:
  	forms.append(GetInputForm())
  	forms.append(formset_factory(CPForm, extra=2))
  if type(inForm) == list and type(formset) == list:
  	data = []
  	data.append(inForm)
  	data.append(formset)
  	retval = convertData(request, inForm[1], inForm[0], 'form', form=formset)
  	return render(request, 'presentresults.html', {'data': retval})
  return render(request, 'pointsentry.html', {'formset': forms})

# Control Point CRUD Functionality
def get_controlpoint_list(request):
    page = get_page('Control Points', 'coords:controlpoint_create', 'Control Point')
    data = get_data_list(request,ControlPoint, ControlPointForm, 'coords:controlpoint', page)
    return data

@login_required
def controlpoint_list(request):
    data = get_controlpoint_list(request)
    return render(request, 'list.html', {'data': data})

@login_required
def controlpoint_create(request):
    form, page = obj_create(request, ControlPointForm, ControlPoint, 'coords:controlpoint_create')
    return save_form(request, form, ControlPoint, page, 'coords:controlpoint', 'includes/partial_create.html')

@login_required
def controlpoint_update(request, pk):
    form, page = obj_update(request, pk, ControlPointForm, ControlPoint, 'coords:controlpoint_update')
    return save_form(request, form, ControlPoint, page, 'coords:controlpoint', 'includes/partial_update.html')

@login_required
def controlpoint_delete(request, pk):
    url = reverse('coords:controlpoint_delete', args={pk})
    data = delete_form(request, pk, ControlPointForm, ControlPoint, url, 'coords:controlpoint',)
    return JsonResponse(data)

# Sheet Reference CRUD Functionality
def get_sheetreference_list(request):
    page = get_page('Sheets', 'coords:sheetreference_create', 'Sheet')
    data = get_data_list(request,SheetReference, SheetReferenceForm, 'coords:sheetreference', page)
    return data

@login_required
def sheetreference_list(request):
    data = get_sheetreference_list(request)
    return render(request, 'list.html', {'data': data})

@login_required
def sheetreference_create(request):
    form, page = obj_create(request, SheetReferenceForm, SheetReference, 'coords:sheetreference_create')
    return save_form(request, form, SheetReference, page, 'coords:sheetreference', 'includes/partial_create.html')

@login_required
def sheetreference_update(request, pk):
    form, page = obj_update(request, pk, SheetReferenceForm, SheetReference, 'coords:sheetreference_update')
    return save_form(request, form, SheetReference, page, 'coords:sheetreference', 'includes/partial_update.html')

@login_required
def sheetreference_delete(request, pk):
    url = reverse('coords:sheetreference_delete', args={pk})
    data = delete_form(request, pk, SheetReferenceForm, SheetReference, url, 'coords:sheetreference',)
    return JsonResponse(data)

# Transformation Request CRUD Functionality
def get_transrequest_list(request):
    page = get_page('Transformation Requests', 'coords:transrequest_create', 'Transformation Request')
    data = get_data_list(request,TransRequest, TransRequestForm, 'coords:transrequest', page)
    return data

@login_required
def transrequest_list(request):
    data = get_transrequest_list(request)
    return render(request, 'list.html', {'data': data})

@login_required
def transrequest_create(request):
    form, page = obj_create(request, TransRequestForm, TransRequest, 'coords:transrequest_create')
    return save_form(request, form, TransRequest, page, 'coords:transrequest', 'includes/partial_create.html')

@login_required
def transrequest_update(request, pk):
    form, page = obj_update(request, pk, TransRequestForm, TransRequest, 'coords:transrequest_update')
    return save_form(request, form, TransRequest, page, 'coords:transrequest', 'includes/partial_update.html')

@login_required
def transrequest_delete(request, pk):
    url = reverse('coords:transrequest_delete', args={pk})
    data = delete_form(request, pk, TransRequestForm, TransRequest, url, 'coords:transrequest',)
    return JsonResponse(data)

