from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView

from dashboard.models import Task, Event
from dashboard.forms import TaskForm, EventForm
from .models import Team, TeamMembership
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import JoinTeamForm
from django.shortcuts import get_object_or_404, redirect


class MyTeamsView(LoginRequiredMixin, ListView):
    model = Team
    template_name = "teams/my_teams.html"
    context_object_name = "teams"
    paginate_by = 12
    extra_context = {'title': 'My Teams'}

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
    extra_context = {'title': 'My Teams'}


# TODO: EDIT TEAM
class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = "teams/create_team.html"
    fields = ["name", "description", "company"]
    success_url = reverse_lazy("teams:my_teams")
    extra_context = {'title': 'Create Team'}

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


@login_required
def team_dashboard(request, pk):
    team = get_object_or_404(Team, pk=pk)

    if request.user not in team.members.all():
        messages.error(request, "You are not a member of this team.")
        return redirect("teams:my_teams")

    # Handle adding tasks
    if request.method == "POST":
        if "add_task" in request.POST:
            task_form = TaskForm(request.POST, user=request.user, team=team)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.team = team
                task.save()
                task_form.save_m2m()
                messages.success(request, f"Task '{task.title}' added.")
                return redirect("teams:team_dashboard", pk=pk)

        elif "add_event" in request.POST:
            event_form = EventForm(request.POST, user=request.user, team=team)
            if event_form.is_valid():
                event = event_form.save(commit=False)
                event.team = team
                event.save()
                event_form.save_m2m()
                messages.success(request, f"Event '{event.title}' created.")
                return redirect("teams:team_dashboard", pk=pk)

    task_form = TaskForm(team=team)
    event_form = EventForm(team=team)

    tasks = team.tasks.all().order_by("-pub_date")
    events = team.events.all().order_by("-start_datetime")

    context = {
        "team": team,
        "team_tasks": tasks,
        "team_events": events,
        "task_form": task_form,
        "event_form": event_form,
        "title": f"{team.name} Dashboard",
    }
    return render(request, "teams/team_dashboard.html", context)


@login_required
def delete_team_task(request, team_pk, task_pk):
    task = get_object_or_404(Task, pk=task_pk, team_id=team_pk)
    team = task.team

    if request.user not in team.members.all():
        messages.error(request, "You are not allowed to delete this task.")
        return redirect("teams:team_dashboard", pk=team_pk)

    task.delete()
    messages.success(request, f"Task '{task.title}' deleted.")
    return redirect("teams:team_dashboard", pk=team_pk)


@login_required
def delete_team_event(request, team_pk, event_pk):
    event = get_object_or_404(Event, pk=event_pk, team_id=team_pk)
    team = event.team

    if request.user not in team.members.all():
        messages.error(request, "You are not allowed to delete this event.")
        return redirect("teams:team_dashboard", pk=team_pk)

    event.delete()
    messages.success(request, f"Event '{event.title}' deleted.")
    return redirect("teams:team_dashboard", pk=team_pk)


@login_required
def leave_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.user in team.members.all():
        team.members.remove(request.user)
        messages.success(request, f"You have left the team '{team.name}'.")
    else:
        messages.warning(request, "You are not a member of this team.")
    return redirect("teams:my_teams")
