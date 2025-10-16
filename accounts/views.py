from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from accounts.forms import RegistrationForm, UpdateUserForm, UpdateProfileForm
from accounts.models import Profile


# Create your views here.

class UserRegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'accounts/register.html'
    extra_context = {'title': 'Register'}

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object, backend='django.contrib.auth.backends.ModelBackend')
        return redirect("accounts:profile_view", username=self.object.username)


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


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "accounts/profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        context['title'] = f'{profile}\'s Profile'
        context['connections'] = profile.connections.all()
        context['companies'] = profile.companies.all()
        context['teams'] = profile.teams.all()
        context['projects'] = profile.projects.all()
        return context

    def get_object(self, queryset=None):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


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


@login_required
def edit_user_profile(request, username):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('accounts:profile_view', username=request.user.username)
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
