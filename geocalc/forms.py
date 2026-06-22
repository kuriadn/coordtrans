from django import forms

from .compute import dms_to_decimal


class BearingDistanceForm(forms.Form):
    MODES = (
        ('forward', 'Forward (polar) — bearing & distance → coordinates'),
        ('inverse', 'Inverse (join) — coordinates → bearing & distance'),
    )

    mode = forms.ChoiceField(
        label='Computation',
        choices=MODES,
        initial='forward',
        widget=forms.RadioSelect,
    )

    from_label = forms.CharField(label='From station', max_length=32, initial='A')
    from_easting = forms.DecimalField(label='From easting', max_digits=14, decimal_places=3)
    from_northing = forms.DecimalField(label='From northing', max_digits=14, decimal_places=3)

    to_label = forms.CharField(label='To station', max_length=32, initial='B', required=False)
    to_easting = forms.DecimalField(
        label='To easting', max_digits=14, decimal_places=3, required=False,
    )
    to_northing = forms.DecimalField(
        label='To northing', max_digits=14, decimal_places=3, required=False,
    )

    bearing_deg = forms.IntegerField(label='Bearing °', min_value=0, max_value=360, required=False)
    bearing_min = forms.IntegerField(label='′', min_value=0, max_value=59, initial=0, required=False)
    bearing_sec = forms.DecimalField(
        label='″', min_value=0, max_value=59.999, decimal_places=3, initial=0, required=False,
    )
    distance = forms.DecimalField(
        label='Horizontal distance (m)', min_value=0, decimal_places=3, max_digits=12, required=False,
    )

    def clean(self):
        cleaned = super().clean()
        mode = cleaned.get('mode')

        if mode == 'forward':
            if cleaned.get('bearing_deg') is None:
                self.add_error('bearing_deg', 'Bearing is required for forward computation.')
            if cleaned.get('distance') is None:
                self.add_error('distance', 'Distance is required for forward computation.')
            elif cleaned['distance'] <= 0:
                self.add_error('distance', 'Distance must be greater than zero.')
            if not cleaned.get('to_label', '').strip():
                cleaned['to_label'] = 'B'
        elif mode == 'inverse':
            for field in ('to_easting', 'to_northing'):
                if cleaned.get(field) is None:
                    self.add_error(field, 'Required for inverse (join) computation.')
            if not cleaned.get('to_label', '').strip():
                self.add_error('to_label', 'To station label is required.')

        return cleaned

    def bearing_decimal(self) -> float:
        return dms_to_decimal(
            int(self.cleaned_data['bearing_deg']),
            int(self.cleaned_data['bearing_min']),
            float(self.cleaned_data['bearing_sec']),
        )
