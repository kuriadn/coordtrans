from django.conf import settings
from django import forms
from django.forms import formset_factory

from georef.cassini_proj import cassini_proj4_with_cm

from .presets import PRESET_CHOICES, TABLE_PRESETS, is_table_preset, resolve_preset


class CrsSetupForm(forms.Form):
    preset = forms.ChoiceField(
        label='CRS preset',
        choices=PRESET_CHOICES,
        initial='cassini-utm',
    )
    central_meridian = forms.DecimalField(
        label='Central meridian (°E)',
        required=False,
        max_digits=6,
        decimal_places=4,
        initial=37.0,
        help_text='Required for log-table Cassini presets. Also overrides lon_0 for custom Cassini PROJ strings.',
    )
    source_crs = forms.CharField(
        label='Source CRS (PROJ4 or EPSG)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': '+proj=... or EPSG:32637'}),
        help_text='Used when preset is Custom.',
    )
    target_crs = forms.CharField(
        label='Target CRS (PROJ4 or EPSG)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'EPSG:4326'}),
    )

    def resolve_crs_pair(self) -> tuple[str | int, str | int]:
        preset = self.cleaned_data['preset']
        if is_table_preset(preset):
            raise forms.ValidationError('Table presets do not use PROJ CRS pairs.')
        if preset == 'custom':
            source = (self.cleaned_data.get('source_crs') or '').strip()
            target = (self.cleaned_data.get('target_crs') or '').strip()
            if not source:
                raise forms.ValidationError('Source CRS is required for a custom preset.')
            if not target:
                raise forms.ValidationError('Target CRS is required for a custom preset.')
            cm = self.cleaned_data.get('central_meridian')
            if cm is not None and '+proj=cass' in source:
                source = cassini_proj4_with_cm(float(cm), source)
            if cm is not None and '+proj=cass' in target:
                target = cassini_proj4_with_cm(float(cm), target)
            return source, target
        return resolve_preset(preset)

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned
        preset = cleaned.get('preset')
        if is_table_preset(preset) and cleaned.get('central_meridian') in (None, ''):
            self.add_error('central_meridian', 'Central meridian is required for log-table presets.')
        if preset == 'custom':
            if not cleaned.get('source_crs', '').strip():
                self.add_error('source_crs', 'Required for custom CRS.')
            if not cleaned.get('target_crs', '').strip():
                self.add_error('target_crs', 'Required for custom CRS.')
        return cleaned


class CrsPointForm(forms.Form):
    easting = forms.DecimalField(label='X / Easting / Lon', max_digits=16, decimal_places=6)
    northing = forms.DecimalField(label='Y / Northing / Lat', max_digits=16, decimal_places=6)


CrsPointFormSet = formset_factory(
    CrsPointForm,
    extra=3,
    min_num=1,
    validate_min=True,
    can_delete=False,
)


class CrsFileForm(CrsSetupForm):
    source = forms.FileField(label='Coordinate file')

    def clean_source(self):
        uploaded = self.cleaned_data['source']
        if uploaded.size > 2 * 1024 * 1024:
            raise forms.ValidationError('File must be smaller than 2 MB.')
        return uploaded
