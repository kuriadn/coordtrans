from __future__ import unicode_literals
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from authtools import forms as authtoolsforms
from django.contrib.auth import forms as authforms

INPUT_CLASS = 'form-input'
CHECKBOX_CLASS = 'form-checkbox'


def _style_fields(form, field_names):
    for name in field_names:
        if name in form.fields:
            if isinstance(form.fields[name].widget, forms.CheckboxInput):
                form.fields[name].widget.attrs.setdefault('class', CHECKBOX_CLASS)
            else:
                form.fields[name].widget.attrs.setdefault('class', INPUT_CLASS)


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False, label='Remember me')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['username'].widget.input_type = 'email'
        _style_fields(self, ['username', 'password', 'remember_me'])


class SignupForm(authtoolsforms.UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.input_type = 'email'
        _style_fields(self, ['email', 'name', 'password1', 'password2'])


class PasswordChangeForm(authforms.PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self, ['old_password', 'new_password1', 'new_password2'])


class PasswordResetForm(authtoolsforms.FriendlyPasswordResetForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.input_type = 'email'
        _style_fields(self, ['email'])


class SetPasswordForm(authforms.SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self, ['new_password1', 'new_password2'])
