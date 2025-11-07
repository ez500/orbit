from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView

from accounts import models
from accounts.forms import RegistrationForm, UpdateUserForm, UpdateProfileForm, ChangePasswordForm
from accounts.models import Profile, ConnectionRequest
from company.models import Company
from projects.models import Project
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
        context['already_requested'] = ConnectionRequest.objects.filter(from_profile=self.request.user.profile, to_profile=profile).exists()
        context['requests'] = ConnectionRequest.objects.filter(to_profile=profile)
        context['companies'] = Company.objects.filter(members=profile.user).order_by("name")
        context['teams'] = Team.objects.filter(members=profile.user).order_by("name")
        context['projects'] = Project.objects.filter(collaborators=profile.user).order_by("name")
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


class CompanyListView(LoginRequiredMixin, ListView):
    context_object_name = "companies"
    template_name = "company/list.html"
    paginate_by = 10

    def get_object(self):
        return get_object_or_404(Profile, user__username=self.kwargs['username'])

    def get_queryset(self):
        return Company.objects.filter(members=self.get_object().user).order_by("name")

    def get_context_data(self, **kwargs):
        profile = self.get_object()
        context = super().get_context_data(**kwargs)

        context['profile'] = profile
        context['title'] = f'{profile}\'s Company Info'
        context['can_view'] = self.can_view_private_info()
        return context

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


# TODO DELETE USER ACCOUNT VIEW/CONFIG
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
        # Handle both user and profile forms
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if profile_form.is_valid() and user_form.is_valid():
            # Save both forms
            user_form.save()
            profile_form.save()
            messages.success(request, 'Settings saved successfully!')
            return redirect('accounts:settings')
        else:
            # Show error messages for validation issues
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
def search(request):
    user_search_query = request.GET.get('user_search_query', '')
    if request.user.is_staff or request.user.is_superuser:
        users_found = User.objects.filter(username__icontains=user_search_query)
    else:
        users_found = User.objects.filter(username__icontains=user_search_query).filter(
            ~Q(profile__visibility__icontains='HIDDEN') |
            Q(profile__connections=request.user.profile) |
            Q(profile=request.user.profile)
        )

    requested_users = ConnectionRequest.objects.filter(
        from_profile__user=request.user).values_list('to_profile__user__username', flat=True)

    context = {
        'title': "Search Users", 'requesting_user': request.user,
        'user_search_query': user_search_query, 'users_found': users_found, 'requested_users': requested_users}
    return render(request, 'accounts/_search.html', context)


def _safe_redirect_back(request, fallback_url):
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect(fallback_url)


@login_required
def send_connection_request(request, username):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user__username=username)

        if profile.connections.filter(pk=request.user.profile.pk).exists():
            messages.info(request, f"{profile} is already a connection.")
        else:
            ConnectionRequest.objects.create(
                from_profile=request.user.profile,
                to_profile=profile
            )
            messages.success(request, f'Connection request sent to {profile}.')
    return _safe_redirect_back(request, fallback_url=reverse('accounts:profile_view', args=[request.user.profile]))


@login_required
def accept_connection_request(request, username):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user__username=username)

        try:
            connection_request = ConnectionRequest.objects.get(from_profile=profile, to_profile=request.user.profile)
            connection_request.delete()

            if profile.connections.filter(pk=request.user.profile.pk).exists():
                messages.info(request, f"{profile} is already a connection.")
            else:
                profile.connections.add(request.user.profile)
                messages.success(request, f'{profile} is now a connection.')
        except ConnectionRequest.DoesNotExist:
            messages.error(request, f'No connection request from {profile} found.')
    return _safe_redirect_back(request, fallback_url=reverse('accounts:profile_view', args=[username]))


@login_required
def ignore_connection_request(request, username):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user__username=username)

        try:
            connection_request = ConnectionRequest.objects.get(from_profile=profile, to_profile=request.user.profile)
            connection_request.delete()

            if profile.connections.filter(pk=request.user.profile.pk).exists():
                messages.info(request, f"{profile} is already a connection.")
            else:
                messages.success(request, f'Connection request from {profile} ignored.')

        except ConnectionRequest.DoesNotExist:
            messages.error(request, f'No connection request from {profile} found.')
    return _safe_redirect_back(request, fallback_url=reverse('accounts:profile_view', args=[request.user.profile]))


@login_required
def remove_connection(request, username):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user__username=username)

        if profile.connections.filter(user=request.user).exists():
            profile.connections.remove(request.user.profile)
            messages.success(request, f"{profile} is no longer a connection.")
        else:
            messages.error(request, f"{profile} is not a connection.")
    return _safe_redirect_back(request, fallback_url=reverse('accounts:profile_view', args=[request.user.profile]))
