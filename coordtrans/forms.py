from django import forms
from django.db.utils import OperationalError, ProgrammingError
from django.forms import formset_factory
from .models import *

TYPE = (('-----', '-----------'), ('cass', 'Cassini'), ('utm', 'U.T.M.'),)
METHOD = (('sheet', 'Cadastral sheet (4 control points in database)'), ('custom', 'Custom control points'))


class ControlPairForm(forms.Form):
    from_e = forms.DecimalField(max_digits=12, decimal_places=3, label='From easting')
    from_n = forms.DecimalField(max_digits=12, decimal_places=3, label='From northing')
    to_e = forms.DecimalField(max_digits=12, decimal_places=3, label='To easting')
    to_n = forms.DecimalField(max_digits=12, decimal_places=3, label='To northing')


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


PointFormSet = formset_factory(CPForm, extra=2)
ControlPairFormSet = formset_factory(ControlPairForm, extra=2)


class GetInputFileForm(forms.Form):
    method = forms.ChoiceField(
        choices=METHOD,
        initial='sheet',
        label='Transform method',
        widget=forms.RadioSelect,
    )
    source = forms.FileField()
    trtype = forms.CharField(
        max_length=10,
        widget=forms.Select(choices=TYPE),
        label='Transformation Type',
    )
    shtno = forms.CharField(max_length=20, label='Sheet No.', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shtno'].widget = forms.Select(choices=getSheets())

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('method') == 'sheet' and not cleaned.get('shtno'):
            self.add_error('shtno', 'Sheet number is required for sheet-based transforms.')
        return cleaned


class GetInputForm(forms.Form):
    method = forms.ChoiceField(
        choices=METHOD,
        initial='sheet',
        label='Transform method',
        widget=forms.RadioSelect,
    )
    trtype = forms.CharField(
        max_length=10,
        widget=forms.Select(choices=TYPE),
        label='Transformation Type',
    )
    shtno = forms.CharField(max_length=20, label='Sheet No.', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shtno'].widget = forms.Select(choices=getSheets())

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('method') == 'sheet' and not cleaned.get('shtno'):
            self.add_error('shtno', 'Sheet number is required for sheet-based transforms.')
        return cleaned
