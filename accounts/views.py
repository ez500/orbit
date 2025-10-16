from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import RegistrationForm
from accounts.models import Profile

# Create your views here.

class UserRegisterView(CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy("accounts:login")
    template_name = 'accounts/register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'Register'
        return context

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    extra_context = {'title': 'Login'}

class UserLogoutView(LogoutView):
    template_name = 'accounts/logout.html'
    extra_context = {'title': 'Logged out'}

class UserPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject'
    success_message = 'An email has been sent with instructions to reset your password.'
    success_url = reverse_lazy('accounts:password_reset_done')
    extra_context = {'title': 'Password Reset'}

class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:login')
    extra_context = {'title': 'Set New Password'}

class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'
    extra_context = {'title': 'Successful Password Reset'}

@login_required
def profile_view(request, username):
    context = dict()

    context['title'] = f'{username}\'s Profile'
    context['profile'] = get_object_or_404(Profile, user__username=username)
    context['connections'] = context['profile'].connections.all()
    context['companies'] = context['profile'].companies.all()
    context['teams'] = context['profile'].teams.all()
    context['projects'] = context['profile'].projects.all()

    return render(request, 'accounts/profile.html', context)

