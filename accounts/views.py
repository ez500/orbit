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
from django.http import JsonResponse, HttpResponseBadRequest

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

@login_required
def settings(request):
    if request.method == 'POST':
        # For appearance settings, we only need to update profile
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            profile = request.user.profile
            data = {}
            
            # Only update the appearance fields we receive
            for field in ['theme_color', 'accent_color', 'high_contrast', 'font_size', 'spacing']:
                if field in request.POST:
                    value = request.POST[field]
                    if field == 'high_contrast':
                        value = value.lower() == 'true'
                    setattr(profile, field, value)
                    data[field] = value
                else:
                    data[field] = getattr(profile, field)
            
            try:
                profile.save(update_fields=list(data.keys()))
                return JsonResponse({
                    'status': 'success',
                    'message': 'Settings saved successfully!',
                    'profile': data
                })
            except Exception as e:
                import traceback
                print("Error saving settings:", str(e))
                print(traceback.format_exc())
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to save settings: ' + str(e),
                }, status=400)
        
        # For regular form submission, handle both user and profile forms
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if profile_form.is_valid() and user_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            user_form.save()
            messages.success(request, 'Settings saved successfully!')
            return redirect('accounts:settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    accent_choices = Profile.ACCENT_CHOICES
    theme_choices = Profile.THEME_CHOICES

    return render(request, 'accounts/settings.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'accent_choices': accent_choices,
        'theme_choices': theme_choices,
        'title': 'Settings'
    })
