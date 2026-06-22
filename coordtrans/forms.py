from django import forms
from django.db.utils import OperationalError, ProgrammingError
from .models import *

TYPE = (('-----', '-----------'), ('cass', 'Cassini'), ('utm', 'U.T.M.'),)


def getSheets():
    sheets = [('-----', '-----------')]
    try:
        for sht in SheetReference.objects.all():
            sheets.append((sht.shtno, sht.shtno))
    except (OperationalError, ProgrammingError):
        pass
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


class GetInputFileForm(forms.Form):
    source = forms.FileField()
    trtype = forms.CharField(
        max_length=10,
        widget=forms.Select(choices=TYPE),
        label='Transformation Type',
    )
    shtno = forms.CharField(max_length=20, label='Sheet No.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shtno'].widget = forms.Select(choices=getSheets())


class GetInputForm(forms.Form):
    trtype = forms.CharField(
        max_length=10,
        widget=forms.Select(choices=TYPE),
        label='Transformation Type',
    )
    shtno = forms.CharField(max_length=20, label='Sheet No.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shtno'].widget = forms.Select(choices=getSheets())
