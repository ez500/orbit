from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import SignupForm

# Create your views here.

class UserRegisterView(CreateView):
    form_class = SignupForm
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

class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    extra_context = {'title': 'Password Reset'}

class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'
    extra_context = {'title': 'Successful Password Reset'}

