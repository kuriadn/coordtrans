"""AJAX CRUD helpers and form parsing for coordtrans staff views."""
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse


def add_in_params(request, Form):
    in_form = Form()
    fields = tuple(Form.base_fields)

    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            formdata = []
            method = form.cleaned_data.get('method', 'sheet')
            for fld in fields:
                val = form.cleaned_data.get(fld)
                if fld == 'shtno' and method == 'custom':
                    continue
                if val is not None and val != '-----':
                    formdata.append(val)
            if method == 'sheet' and len(formdata) < 3:
                return Form()
            if method == 'custom' and len(formdata) < 2:
                return Form()
            return formdata
        return Form()
    return in_form


def add_formset(request, Form):
    model_formset = formset_factory(Form, extra=2)
    fields = tuple(Form.base_fields)

    if request.method == 'POST':
        formset = model_formset(request.POST, request.FILES)
        if formset.is_valid():
            formdata = []
            valid_data = False
            for fm in formset:
                for fld in fields:
                    if fm.cleaned_data.get(fld) is not None:
                        formdata.append(float(fm.cleaned_data.get(fld)))
                        valid_data = True
            if valid_data:
                return formdata
            return model_formset()
    return model_formset()


def add_control_formset(request, Form):
    """Parse control-point pair formset: from_e, from_n, to_e, to_n per row."""
    model_formset = formset_factory(Form, extra=2)
    fields = tuple(Form.base_fields)

    if request.method == 'POST':
        formset = model_formset(request.POST, prefix='ctrl')
        if formset.is_valid():
            formdata = []
            valid_data = False
            for fm in formset:
                row = []
                for fld in fields:
                    val = fm.cleaned_data.get(fld)
                    if val is not None:
                        row.append(float(val))
                if len(row) == len(fields):
                    formdata.extend(row)
                    valid_data = True
            if valid_data:
                return formdata
            return model_formset(prefix='ctrl')
    return model_formset(prefix='ctrl')


def save_form(request, form, Model, page, urlroot, template):
    data = {}
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            tmpl = 'includes/partial_list.html'
            objdata = get_data_list(request, Model, form, urlroot, page)
            data['html_list'] = render_to_string(tmpl, {'data': objdata})
        else:
            data['form_is_valid'] = False
    formdata = [page, form]
    data['html_form'] = render_to_string(template, {'formdata': formdata}, request=request)
    return JsonResponse(data)


def create_form(request, Form):
    if request.method == 'POST':
        return Form(request.POST, request.FILES)
    return Form()


def update_form(request, pk, Form, Model):
    obj = get_object_or_404(Model, pk=pk)
    if request.method == 'POST':
        return Form(request.POST, request.FILES, instance=obj)
    return Form(instance=obj)


def delete_form(request, pk, Form, Model, url, urlroot):
    obj = get_object_or_404(Model, pk=pk)
    data = {}
    if request.method == 'POST':
        obj.delete()
        page = get_page(Model._meta.verbose_name, urlroot + '_create', Model._meta.verbose_name)
        data['form_is_valid'] = True
        tmpl = 'includes/partial_list.html'
        objdata = get_data_list(request, Model, Form, urlroot, page)
        data['html_list'] = render_to_string(tmpl, {'data': objdata})
    else:
        page = {
            'url': url,
            'objname': Model._meta.verbose_name,
            'objtitle': str(obj),
        }
        data['html_form'] = render_to_string(
            'includes/partial_delete.html',
            {'formdata': [page, obj]},
            request=request,
        )
    return data


def get_page(heading, create_url, new):
    return {
        'heading': heading,
        'create_url': reverse(create_url),
        'new': new,
    }


def obj_create(request, Form, Model, rev_url):
    form = create_form(request, Form)
    page = {
        'url': reverse(rev_url),
        'objname': Model._meta.verbose_name,
    }
    return form, page


def obj_update(request, pk, Form, Model, rev_url):
    form = update_form(request, pk, Form, Model)
    page = {
        'url': reverse(rev_url, args=(pk,)),
        'objname': Model._meta.verbose_name,
    }
    return form, page


def paged_data(request, data, items):
    page = request.GET.get('page', 1)
    paginator = Paginator(data, items)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def get_data_list(request, Model, ModelForm, urlroot, pagedata):
    objects = Model.objects.all()
    fields = ModelForm._meta.fields
    data = []
    pk = Model._meta.pk.name
    update_url = urlroot + '_update'
    delete_url = urlroot + '_delete'
    for obj in objects:
        row = {}
        rowurl = {}
        for fld in fields:
            row[obj._meta.get_field(fld).verbose_name] = getattr(obj, fld)
        rowurl['update'] = reverse(update_url, args=(getattr(obj, pk),))
        rowurl['delete'] = reverse(delete_url, args=(getattr(obj, pk),))
        data.append([row, rowurl])
    pgdata = paged_data(request, data, 15)
    return [pagedata, pgdata]
