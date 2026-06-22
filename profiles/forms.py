from __future__ import unicode_literals
from django import forms
from django.contrib.auth import get_user_model
from . import models

User = get_user_model()
INPUT_CLASS = 'form-input'


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.setdefault('class', INPUT_CLASS)


class ProfileForm(forms.ModelForm):

    class Meta:
        model = models.Profile
        fields = ['picture', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            if name == 'bio':
                self.fields[name].widget.attrs.setdefault('class', INPUT_CLASS)
            else:
                self.fields[name].widget.attrs.setdefault('class', 'form-input')
