from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import RegistrationForm
from accounts.models import Profile


# Create your views here.

class UserRegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'accounts/register.html'
    extra_context = {'title': 'Register'}

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return HttpResponseRedirect(reverse_lazy("accounts:profile_view", kwargs={'username': self.object.username}))

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

@login_required
def profile_view(request, username):
    context = {'title': f'{username}\'s Profile'}

    context['profile'] = get_object_or_404(Profile, user__username=username)
    context['connections'] = context['profile'].connections.all()
    context['companies'] = context['profile'].companies.all()
    context['teams'] = context['profile'].teams.all()
    context['projects'] = context['profile'].projects.all()

    return render(request, 'accounts/profile.html', context)

