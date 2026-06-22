from django import forms
from django.forms import formset_factory

from .compute import dms_to_decimal


class TraverseSetupForm(forms.Form):
    TRAVERSE_TYPES = (
        ('closed', 'Closed traverse'),
        ('open', 'Open traverse'),
    )
    METHODS = (
        ('compass', 'Compass rule (Bowditch)'),
        ('transit', 'Transit rule'),
    )

    start_station = forms.CharField(
        label='Start station',
        max_length=32,
        initial='TP1',
    )
    start_easting = forms.DecimalField(
        label='Start easting',
        max_digits=14,
        decimal_places=3,
        initial=0,
    )
    start_northing = forms.DecimalField(
        label='Start northing',
        max_digits=14,
        decimal_places=3,
        initial=0,
    )
    traverse_type = forms.ChoiceField(
        label='Traverse type',
        choices=TRAVERSE_TYPES,
        initial='closed',
    )
    method = forms.ChoiceField(
        label='Adjustment method',
        choices=METHODS,
        initial='compass',
        required=False,
        help_text='Applied only for closed traverses.',
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('traverse_type') == 'closed' and not cleaned.get('method'):
            self.add_error('method', 'Select an adjustment method for a closed traverse.')
        return cleaned


class TraverseLegForm(forms.Form):
    from_station = forms.CharField(label='From', max_length=32)
    to_station = forms.CharField(label='To', max_length=32)
    bearing_deg = forms.IntegerField(label='Bearing °', min_value=0, max_value=360)
    bearing_min = forms.IntegerField(label='′', min_value=0, max_value=59, initial=0)
    bearing_sec = forms.DecimalField(label='″', min_value=0, max_value=59.999, decimal_places=3, initial=0)
    distance = forms.DecimalField(label='Distance (m)', min_value=0, decimal_places=3, max_digits=12)

    def leg_bearing_decimal(self) -> float:
        return dms_to_decimal(
            int(self.cleaned_data['bearing_deg']),
            int(self.cleaned_data['bearing_min']),
            float(self.cleaned_data['bearing_sec']),
        )

    def clean_distance(self):
        distance = self.cleaned_data.get('distance')
        if distance is not None and distance <= 0:
            raise forms.ValidationError('Distance must be greater than zero.')
        return distance

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned
        if not cleaned.get('from_station', '').strip():
            raise forms.ValidationError('From station is required.')
        if not cleaned.get('to_station', '').strip():
            raise forms.ValidationError('To station is required.')
        return cleaned


TraverseLegFormSet = formset_factory(
    TraverseLegForm,
    extra=3,
    min_num=1,
    validate_min=True,
    can_delete=False,
)
