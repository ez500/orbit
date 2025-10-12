from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from .models import Team, TeamMembership
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import JoinTeamForm

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

@login_required
def join_team(request):
    if request.method == "POST":
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            team = form.cleaned_data["team_name"]
            already_member = TeamMembership.objects.filter(user=request.user, team=team).exists()
            if already_member:
                messages.warning(request, f"You’re already in {team.name}.")
                return redirect("teams:my_teams")

            TeamMembership.objects.create(user=request.user, team=team, role="Member")
            messages.success(request, f"You joined {team.name} successfully!")
            return redirect("teams:my_teams")
    else:
        form = JoinTeamForm()

    return render(request, "teams/join_team.html", {"form": form})
