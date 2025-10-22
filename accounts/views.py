from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from accounts.forms import RegistrationForm, UpdateUserForm, UpdateProfileForm, ChangePasswordForm
from accounts.models import Profile
from teams.models import Team

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
        context['teams'] = Team.objects.filter(members=profile.user).order_by("name")
        context['projects'] = profile.projects.all()
        return context

    def get_object(self, queryset=None):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user.profile


@login_required
def edit_user_profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        password_form = ChangePasswordForm(user=request.user, data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('accounts:profile_view', username=request.user.username)

        if password_form.is_valid():
            password_form.save()
            return redirect('accounts:profile_view', username=request.user.username)
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
        password_form = ChangePasswordForm(user=request.user)

    return render(request, 'accounts/profile_edit.html', {
        'title': 'Edit Profile',
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form
    })

# TODO MANAGE SETTINGS ALLOCATION
@login_required
def settings(request):
    from django.http import JsonResponse
    import json

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        # Debug logging
        print("Request POST data:", request.POST)
        print("Files:", request.FILES)
        print("Theme color:", request.POST.get('theme_color'))
        print("Accent color:", request.POST.get('accent_color'))

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Debug logging
            print("Saved profile theme:", profile.theme_color)
            print("Saved profile accent:", profile.accent_color)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'theme': profile.theme_color,
                    'accent': profile.accent_color,
                    'message': 'Settings saved successfully!'
                })
            messages.success(request, 'Your settings have been updated successfully!')
            return redirect('accounts:settings')
        else:
            print("Form validation errors:")
            print("User form errors:", user_form.errors)
            print("Profile form errors:", profile_form.errors)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': {
                        'user_form': dict(user_form.errors),
                        'profile_form': dict(profile_form.errors)
                    },
                    'message': 'Please correct the errors below.'
                })
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'accounts/settings.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Settings'
    })

@login_required
def search(request):
    search_users = request.POST['search_users']
    users_found = User.objects.filter(username__icontains=search_users)
    context = {'title': "Search Users", 'search_users': search_users, 'users_found': users_found}
    return render(request, 'accounts/_search.html', context)
