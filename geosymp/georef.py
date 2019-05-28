# Code developed by the NLIMS Directorate, National Land Commission
# This is free software to support Affine Transformation
# This is for the Cassini-Soldner to UTM transformations

# Prerequisites to running the code:
# 1. Python translation engine - python
# 2. Numpy for Matrix and array processing
# 3. Read write access on the machine it is to run on and the target output directory

import numpy as nm
import sys, getopt, os
from numpy.linalg import inv
from coordtrans.models import *
from coordtrans.forms import *
from django.forms import formset_factory
from django.utils import timezone 
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.shortcuts import render, get_object_or_404

def genCoeffMatrix(x):
# This function prepares the Matrix of Coefficients given an input vector
  n = len(x)
  #print ('n = {0}'.format(n))
  j = 0
  mat = []
  for i in range(0,int(n/2)):
  	tmp = []
  	tmp.append(x[j * 2 ])
  	tmp.append(-x[j * 2 +1])
  	tmp.append(1)
  	tmp.append(0)
  	mat.append(tmp)
  	tmp = []
  	tmp.append(x[j * 2 + 1])
  	tmp.append(x[j * 2])
  	tmp.append(0)
  	tmp.append(1)
  	mat.append(tmp)
  	j += 1
  return nm.array(mat)

def compute(x,l):
# This function computes the transformation parameters
# Matrix of coefficients
  A = genCoeffMatrix(x)

  L=l
  L=nm.transpose(L)
 
# Prepare system of equations
  AT=nm.transpose(A)
  ATA=nm.dot(AT,A)
  ATL=nm.dot(AT,L)
  ATAInv = inv(ATA)

# The solution
  x=nm.dot(ATAInv,ATL)
  L1 = nm.dot(A,x)

# The computation errors
  er=L1-L
  return x, er, ATAInv

def readData(src):
# This function reads the input file and prepares the input vector required for the transformation computations
  file = open(src, 'r')

  conv = []
  for line in file:
    data = line.split(",")
    if len(data) == 2:
      conv.append(float(data[0]))
      conv.append(float(data[1]))
  file.close()
  conv = nm.array(conv)
  return conv

def generateParams(sheetno, trtype):
  sheetarr = SheetReference.objects.filter(shtno=sheetno)
  if len(sheetarr) > 0:
    sheet = sheetarr[0]
  else: return 'No sheet found'
  cass = []
  utm = []
  geog = []
  # Cassini coordinates
  cass.append(float(sheet.pt1.cass_x))
  cass.append(float(sheet.pt1.cass_y))
  cass.append(float(sheet.pt2.cass_x))
  cass.append(float(sheet.pt2.cass_y))
  cass.append(float(sheet.pt3.cass_x))
  cass.append(float(sheet.pt3.cass_y))
  cass.append(float(sheet.pt4.cass_x))
  cass.append(float(sheet.pt4.cass_y))

  # U.T.M. coordinates
  utm.append(float(sheet.pt1.utm_x))
  utm.append(float(sheet.pt1.utm_y))
  utm.append(float(sheet.pt2.utm_x))
  utm.append(float(sheet.pt2.utm_y))
  utm.append(float(sheet.pt3.utm_x))
  utm.append(float(sheet.pt3.utm_y))
  utm.append(float(sheet.pt4.utm_x))
  utm.append(float(sheet.pt4.utm_y))

  if trtype == 'cass': # transform to Cassini
    x = utm
    l = cass
  else: # transform to U.T.M.
    x = cass
    l = utm
  #print ('x')
  #print (x)
  #print ('l')
  #print (l)
  return compute(x, l)

def getMinMax(sheet, trtype):
  sht = SheetReference.objects.filter(shtno=sheet)[0]
  xpts = []
  ypts = []
  # Get the controls
  if trtype == 'utm':
    xpts.append(sht.pt1.cass_x)
    ypts.append(sht.pt1.cass_y)
    xpts.append(sht.pt2.cass_x)
    ypts.append(sht.pt2.cass_y)
    xpts.append(sht.pt3.cass_x)
    ypts.append(sht.pt3.cass_y)
    xpts.append(sht.pt4.cass_x)
    ypts.append(sht.pt4.cass_y)
  else:
    xpts.append(sht.pt1.utm_x)
    ypts.append(sht.pt1.utm_y)
    xpts.append(sht.pt2.utm_x)
    ypts.append(sht.pt2.utm_y)
    xpts.append(sht.pt3.utm_x)
    ypts.append(sht.pt3.utm_y)
    xpts.append(sht.pt4.utm_x)
    ypts.append(sht.pt4.utm_y)
  # sort the reference data
  xpts.sort()
  ypts.sort()
  # Get the minimum bounding point
  minPt = []
  minPt.append(xpts[0])
  minPt.append(ypts[0])

  # Get the maximum bounding point
  maxPt = []
  maxPt.append(xpts[3])
  maxPt.append(ypts[3])  
  return minPt, maxPt

def checkPoints(sheet, conv, trtype, active):
  ptmap = []
  inConv = []
  minpt, maxpt = getMinMax(sheet, trtype)
  pts = int(len(conv)/2)
  if active:
    n = pts
  else:
    if pts > 5:
      n = 5
    else: 
      n = pts
  cnt = 0
  for i in range(n):
    if checkPoint(minpt, maxpt, conv[2 * i], conv[2 * i + 1]): 
      pt = []
      pt.append(i)
      pt.append(cnt)
      ptmap.append(pt)
      inConv.append(conv[2 * i])
      inConv.append(conv[2 * i + 1])
      cnt += 1
  print ('Compliant {0}, all {1}'.format(cnt * 2, pts * 2))
  ret = []
  ret.append(inConv)
  ret.append(ptmap)
  return ret

def checkPoint(minpt, maxpt, x, y):
  default = False
  print (x, minpt[0], y, minpt[1])
  print (x, maxpt[0], y, maxpt[1])
  if float(x) >= float(minpt[0]) and float(x) <= float(maxpt[0]) and float(y) >= float(minpt[1]) and float(y) <= float(maxpt[1]):
    return True
  return default

def prepareInput(source, form=None):
  if source == 'file':
    infile = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'media/convert/file.asc')
    conv = readData(infile)
  else:
    if form:
      conv = form 
  return conv

def transformed(pts, idx):
  found = False
  for i in range(len(pts)):
    if idx == pts[i][0]: return True
  return found

def convertData(request, sheetno, trtype, source, form=None):
  retval = []
  pre = []
  if trtype == 'cass': 
    t = 'Cassini'
  else:
    t = 'U.T.M'
  pre.append(sheetno)
  pre.append(t)
  active = checkActive(request)
  try:
    coeff, er, ATAInv = generateParams(sheetno, trtype)
    conv = prepareInput(source, form)
    ret = checkPoints(sheetno, conv, trtype, active)
    inConv = ret[0]
    ptmap = ret[1]
    pre.append(int(len(conv)/2))
    pre.append(int(len(inConv)/2))
    if len(ret[0]) > 0: 
      B = genCoeffMatrix(inConv)
      trans = nm.dot(B, coeff)
      orig = []
      tran = []
      for i in range(int(len(conv)/2)):
        pt = []
        pt.append(conv[2 * i])
        pt.append(conv[2 * i + 1])
        orig.append(pt)
      for i in range(int(len(trans)/2)):
        pt = []
        pt.append(trans[2 * i])
        pt.append(trans[2 * i + 1])
        tran.append(pt)
      out = []
      cnt = 0
      for i in range(len(orig)):
        tr = []
        if transformed(ptmap, i):
          tr.append(orig[i])
          tr.append(tran[cnt])
          cnt += 1
        else:
          tr.append(orig[i])
          tr.append('Point outside sheet - Not transformed')
        out.append(tr)
      retval.append(pre)
      retval.append(out)
      storeTransaction(request, pre)
    else:
      retval.append(pre)
      #print ('pre[2] = {0}'.format(len(conv)))
      if len(conv) == 0:
        retval.append('Input file format is suspect. Transformation aborted')
      else:
        retval.append('All points to be transformed fall outside the sheet. Transformation aborted')
      storeTransaction(request, pre)
  except ValueError:
    retval.append(pre)
    retval.append('Input file is not a text file. Transformation aborted')
    storeTransaction(request, pre)
  return retval

def add_inParams(request, Form=GetInputForm):
  inForm = Form()
  fields = tuple(Form.base_fields)
  
  if request.method == "POST":
    form = Form(request.POST)
    if form.is_valid():
      formdata = []
      for fld in fields:
        if form.cleaned_data.get(fld) != '-----':
          formdata.append(form.cleaned_data.get(fld))
      if len(formdata) < 2:
        inForm = Form()
        return inForm
      else: return formdata
    else:
      inForm = Form()
  else:
    inForm = Form()
  return inForm

def add_formset(request, Form):
  ModelFormset = formset_factory(Form, extra=2)
  fields = tuple(Form.base_fields)

  if request.method == "POST":
    formset = ModelFormset(request.POST, request.FILES)
    if formset.is_valid():
      formdata = []
      valid_data = False 
      for fm in formset:
        for fld in fields:
          if fm.cleaned_data.get(fld) != None:
            formdata.append(float(fm.cleaned_data.get(fld)))
            valid_data = True 
      if valid_data:
        return formdata
      else: return ModelFormset()
  else:
      formset = ModelFormset()
  return formset

def storeTransaction(request, pre):
  sheet = SheetReference.objects.filter(shtno=pre[0])[0]
  if pre[1] == 'Cassini':
    tr = 'cass'
  else:
    tr = 'utm'
  trans = TransRequest()
  trans.user=request.user
  trans.sheet=sheet
  trans.trtype=tr
  trans.inpoints = 0
  trans.points = 0 
  trans.datedone=timezone.now()
  if len(pre) > 2:
    trans.inpoints=pre[2]
    trans.points=pre[3]
  trans.save()
  return 

def checkActive(request):
  trans = TransRequest.objects.filter(user=request.user)[0]
  return True

def save_form(request, form, Model, page, urlroot, template):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            tmpl = 'includes/partial_list.html'
            objdata = get_data_list(request, Model, form, urlroot, page)
            data['html_list'] = render_to_string(tmpl, {'data': objdata})
        else:
            data['form_is_valid'] = False
    formdata = []
    formdata.append(page)
    formdata.append(form)
    context = {'formdata': formdata}
    data['html_form'] = render_to_string(template, context, request=request)
    return JsonResponse(data)

def create_form(request, Form):
    if request.method == 'POST':
        form = Form(request.POST, request.FILES)
    else:
        form = Form()
    return form

def update_form(request, pk, Form, Model):
    obj = get_object_or_404(Model, pk=pk)
    if request.method == 'POST':
        form = Form(request.POST, request.FILES, instance=obj)
    else:
        form = Form(instance=obj)
    return form

def delete_form(request, pk, Form, Model, url, urlroot):
    obj = get_object_or_404(Model, pk=pk)
    page = dict()
    data = dict()
    if request.method == 'POST':
        obj.delete()
        page = get_page(Model._meta.verbose_name, urlroot + '_create', Model._meta.verbose_name)
        data['form_is_valid'] = True
        tmpl = 'includes/partial_list.html'
        objdata = get_data_list(request, Model, Form, urlroot, page)
        data['html_list'] = render_to_string(tmpl, {'data': objdata})
    else:
        page['url'] = url
        page['objname'] = Model._meta.verbose_name
        page['objtitle'] = obj.__str__()
        formdata = []
        formdata.append(page)
        formdata.append(obj)
        context = {'formdata': formdata}
        tmpl = 'includes/partial_delete.html'
        data['html_form'] = render_to_string(tmpl, context, request=request)
    return data

#Term Object manipulation
def get_page(heading, create_url, new):
    page = dict()
    page['heading'] = heading
    page['create_url'] = reverse(create_url)
    page['new'] = new 
    return page

def obj_create(request, Form, Model, rev_url):
    form = create_form(request, Form)
    page = dict()
    page['url'] = reverse(rev_url)
    page['objname'] = Model._meta.verbose_name
    return form, page

def obj_update(request, pk, Form, Model, rev_url):
    form = update_form(request, pk, Form, Model)
    page = dict()
    page['url'] = reverse(rev_url, args={pk})
    page['objname'] = Model._meta.verbose_name
    return form, page

def pageddata(request, data, items):
    page = request.GET.get('page', 1)
    paginator = Paginator(data, items)
    try:
        pgdata = paginator.page(page)
    except PageNotAnInteger:
        pgdata = paginator.page(1)
    except EmptyPage:
        pgdata = paginator.page(paginator.num_pages)
    return pgdata

def get_data_list(request, Model, ModelForm, urlroot, pagedata):
    objects = Model.objects.all()
    fields = ModelForm._meta.fields
    data = []
    pk = Model._meta.pk.name
    create_url = urlroot + '_create'
    update_url = urlroot + '_update'
    delete_url = urlroot + '_delete'
    for obj in objects:
      row = dict()
      rowurl = dict()
      datapiece = []
      for fld in fields:
        row[obj._meta.get_field(fld).verbose_name] = getattr(obj, fld)
      rowurl['update'] = reverse(update_url, args={getattr(obj, pk)})
      rowurl['delete'] = reverse(delete_url, args={getattr(obj, pk)})
      datapiece.append(row)
      datapiece.append(rowurl)
      data.append(datapiece)
    pgdata = pageddata(request, data, 15)
    objdata = [] 
    objdata.append(pagedata)
    objdata.append(pgdata)
    return objdata

