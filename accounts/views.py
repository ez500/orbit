from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.forms import SignupForm, UserSettingsForm, ProfileSettingsForm

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

@login_required
def settings(request):
    from django.http import JsonResponse
    import json

    if request.method == 'POST':
        user_form = UserSettingsForm(request.POST, instance=request.user)
        profile_form = ProfileSettingsForm(request.POST, request.FILES, instance=request.user.profile)
        
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
        user_form = UserSettingsForm(instance=request.user)
        profile_form = ProfileSettingsForm(instance=request.user.profile)
    
    return render(request, 'accounts/settings.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Settings'
    })
