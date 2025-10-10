from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from .models import Team, TeamMembership
from django.urls import reverse_lazy


class MyTeamsView(LoginRequiredMixin, ListView):
    model = Team
    template_name = "teams/my_teams.html"
    context_object_name = "teams"
    paginate_by = 12

    def get_queryset(self):
        qs = Team.objects.filter(members=self.request.user).order_by("name").prefetch_related("members")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = "teams/team_detail.html"
    context_object_name = "team"

class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = "teams/create_team.html"
    fields = ["name", "description"]
    success_url = reverse_lazy("teams:my_teams")

    def form_valid(self, form):
        response = super().form_valid(form)
        TeamMembership.objects.create(
            user=self.request.user,
            team=self.object,
            role="Owner"
        )
        return response
