from __future__ import unicode_literals
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth import views as authviews
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.views import generic
from braces import views as bracesviews
from . import forms

User = get_user_model()


class LoginView(bracesviews.AnonymousRequiredMixin, authviews.LoginView):
    template_name = "accounts/login.html"
    form_class = forms.LoginForm

    def form_valid(self, form):
        redirect = super(LoginView, self).form_valid(form)
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me is True:
            one_month = 30 * 24 * 60 * 60
            expiry = getattr(settings, "KEEP_LOGGED_DURATION", one_month)
            self.request.session.set_expiry(expiry)
        return redirect


class LogoutView(authviews.LogoutView):
    next_page = reverse_lazy('home')


class SignUpView(bracesviews.AnonymousRequiredMixin,
                 bracesviews.FormValidMessageMixin,
                 generic.CreateView):
    form_class = forms.SignupForm
    model = User
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')
    form_valid_message = "You're signed up!"

    def form_valid(self, form):
        response = super(SignUpView, self).form_valid(form)
        user = authenticate(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
        )
        if user is not None:
            login(self.request, user)
        return response


class PasswordChangeView(authviews.PasswordChangeView):
    form_class = forms.PasswordChangeForm
    template_name = 'accounts/password-change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Your password was changed, "
            "hence you have been logged out. Please relogin",
        )
        return super(PasswordChangeView, self).form_valid(form)


class PasswordResetView(authviews.PasswordResetView):
    form_class = forms.PasswordResetForm
    template_name = 'accounts/password-reset.html'
    success_url = reverse_lazy('accounts:password-reset-done')
    subject_template_name = 'accounts/emails/password-reset-subject.txt'
    email_template_name = 'accounts/emails/password-reset-email.html'


class PasswordResetDoneView(authviews.PasswordResetDoneView):
    template_name = 'accounts/password-reset-done.html'


class PasswordResetConfirmView(authviews.PasswordResetConfirmView):
    template_name = 'accounts/password-reset-confirm.html'
    form_class = forms.SetPasswordForm
    success_url = reverse_lazy('accounts:login')
