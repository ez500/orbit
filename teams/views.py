from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Team

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

