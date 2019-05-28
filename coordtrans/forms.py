from django import forms
from .models import *

TYPE = (('-----', '-----------'), ('cass', 'Cassini'), ('utm', 'U.T.M.'),)

def getSheets():
  sheets = []
  shts = SheetReference.objects.all()
  sheets.append(('-----', '-----------'))
  for i in range(len(shts)):
    sheets.append((shts[i].shtno, shts[i].shtno))
  return tuple(sheets)

class ControlPointForm(forms.ModelForm):
  class Meta:
  	model = ControlPoint
  	fields = ('pid', 'geog_x', 'geog_y', 'cass_x', 'cass_y', 'utm_x', 'utm_y')

class SheetReferenceForm(forms.ModelForm):
  class Meta:
  	model = SheetReference
  	fields = ('shtno', 'pt1', 'pt2', 'pt3', 'pt4', 'scan')

class TransRequestForm(forms.ModelForm):
  class Meta:
  	model = TransRequest
  	fields = ('user', 'sheet', 'inpoints', 'points', 'trtype', 'datedone')

class CPForm(forms.Form):
  E = forms.DecimalField(max_digits=12, decimal_places=3, label='Easting')
  N = forms.DecimalField(max_digits=12, decimal_places=3, label='Northing')
#  srid = forms.IntegerField() 
  
class GetInputFileForm(forms.Form):
  SHEETS = getSheets()
  source = forms.FileField()
  trtype = forms.CharField(max_length=10, widget=forms.Select(choices=TYPE), label='Transformation Type')
  shtno = forms.CharField(max_length=20, widget=forms.Select(choices=SHEETS), label='Sheet No.')

class GetInputForm(forms.Form):
  SHEETS = getSheets()
  trtype = forms.CharField(max_length=10, widget=forms.Select(choices=TYPE), label='Transformation Type')
  shtno = forms.CharField(max_length=20, widget=forms.Select(choices=SHEETS), label='Sheet No.')

