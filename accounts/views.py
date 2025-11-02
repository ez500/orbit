from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView

from accounts import models
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
        context['can_view'] = self.can_view_private_info()
        return context

    def get_object(self, queryset=None):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user.profile

    def dispatch(self, request, *args, **kwargs):
        if not self.can_access():
            raise Http404(
                "User %s is hidden." % self.kwargs['username']
            )
        return super().dispatch(request, *args, **kwargs)

    def can_access(self):
        searched_profile = self.get_object()
        requesting_user = self.request.user

        searched_is_visible = searched_profile.visibility != models.Profile.Visibility.HIDDEN.name
        requesting_is_staff = requesting_user.is_staff or requesting_user.is_superuser
        is_connection = requesting_user.profile.connections.filter(pk=searched_profile.pk).exists()
        is_self = requesting_user.profile == searched_profile
        return searched_is_visible or requesting_is_staff or is_connection or is_self

    def can_view_private_info(self):
        searched_profile = self.get_object()
        requesting_user = self.request.user

        searched_is_public = searched_profile.visibility == models.Profile.Visibility.PUBLIC.name
        requesting_is_staff = requesting_user.is_staff or requesting_user.is_superuser
        is_connection = requesting_user.profile.connections.filter(pk=searched_profile.pk).exists()
        is_self = requesting_user.profile == searched_profile
        return searched_is_public or requesting_is_staff or is_connection or is_self


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

@login_required
@require_http_methods(['POST'])
def search(request):
    user_search_query = request.POST.get('user_search_query', '')
    if request.user.is_staff or request.user.is_superuser:
        users_found = User.objects.filter(username__icontains=user_search_query)
    else:
        users_found = User.objects.filter(username__icontains=user_search_query).filter(
            ~Q(profile__visibility__icontains='HIDDEN') |
            Q(profile__connections=request.user.profile) |
            Q(profile=request.user.profile)
        )
    context = {
        'title': "Search Users", 'requesting_user': request.user,
        'user_search_query': user_search_query, 'users_found': users_found}
    return render(request, 'accounts/_search.html', context)

@login_required
def add_connection(request, username):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user__username=username)

        if profile.connections.filter(pk=request.user.profile.pk).exists():
            messages.info(request, f"{profile} is already a connection.")
        else:
            profile.connections.add(request.user.profile)
            messages.success(request, f'{profile} is now a connection.')
    return redirect('accounts:profile_view', username=username)

@login_required
def remove_connection(request, username):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user__username=username)

        if profile.connections.filter(pk=request.user.profile.pk).exists():
            profile.connections.remove(request.user.profile)
            messages.success(request, f"{profile} is no longer a connection.")
        else:
            messages.error(request, f"{profile} is not a connection.")
    return redirect('accounts:profile_view', username=request.user.username)
