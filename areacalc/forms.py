from django import forms
from django.forms import formset_factory


class ParcelSetupForm(forms.Form):
    parcel_name = forms.CharField(
        label='Parcel / plot name',
        max_length=64,
        required=False,
        initial='',
    )
    closed = forms.BooleanField(
        label='Closed boundary (compute area and closing edge)',
        required=False,
        initial=True,
        help_text='Uncheck for an open polyline — perimeter only, no area.',
    )


class BoundaryPointForm(forms.Form):
    label = forms.CharField(label='Point', max_length=32)
    easting = forms.DecimalField(label='Easting', max_digits=14, decimal_places=3)
    northing = forms.DecimalField(label='Northing', max_digits=14, decimal_places=3)

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned
        if not cleaned.get('label', '').strip():
            raise forms.ValidationError('Point label is required.')
        return cleaned


BoundaryPointFormSet = formset_factory(
    BoundaryPointForm,
    extra=4,
    min_num=2,
    validate_min=True,
    can_delete=False,
)
