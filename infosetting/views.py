from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from .models import UserProfile
from .forms import ProfileForm

class ProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = "infosetting/profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        # Always show the logged-in user's profile
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    form_class = ProfileForm
    template_name = "infosetting/profile_edit.html"
    success_url = reverse_lazy("infosetting:me")

    def get_object(self, queryset=None):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def test_func(self):
        # Only the owner can edit
        return self.get_object().user_id == self.request.user.id

